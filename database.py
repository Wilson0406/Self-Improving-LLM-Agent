import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.connection_string = self._build_connection_string()
        
    def _build_connection_string(self):
        """Build SQL Server connection string from environment variables"""
        # First, try to get a complete connection string from environment
        connection_string = os.getenv("DB_CONNECTION_STRING")
        
        if connection_string:
            # Use the provided connection string directly
            return connection_string
        
        # If no complete connection string, build from individual components
        server = os.getenv("DB_SERVER")
        database = os.getenv("DB_DATABASE")
        username = os.getenv("DB_USERNAME")
        password = os.getenv("DB_PASSWORD")
        driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
        
        if not server:
            raise ValueError("Missing required database configuration. Provide either DB_CONNECTION_STRING or DB_SERVER environment variable.")
        
        # Build connection string based on authentication method
        if username and password:
            # SQL Server Authentication
            conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
        else:
            # Windows Authentication (Trusted Connection)
            if not database:
                raise ValueError("DATABASE is required when using Windows Authentication")
            conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes"
        
        return conn_str
    
    def get_connection(self):
        """Get database connection"""
        try:
            return pyodbc.connect(self.connection_string)
        except Exception as e:
            logging.error(f"Database connection failed: {str(e)}")
            raise
    
    def get_active_prompt(self, use_case=None):
        """
        Retrieve the active prompt for a specific use case
        
        Args:
            use_case (str, optional): The use case to filter by
            
        Returns:
            dict: Prompt details or None if not found
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("EXEC usp_GetActivePrompt ?", (use_case,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'PromptID': row[0],
                        'PromptTitle': row[1],
                        'PromptText': row[2],
                        'UseCase': row[3],
                        'EffectivenessScore': row[4]
                    }
                return None
                
        except Exception as e:
            logging.error(f"Error fetching active prompt: {str(e)}")
            raise
    
    def insert_prompt_and_set_active(self, prompt_title, prompt_text, use_case, effectiveness_score=None, feedback_requested=None):
        """
        Insert new prompt and set it as active for the use case
        
        Args:
            prompt_title (str): Title/name for the prompt
            prompt_text (str): The full prompt text
            use_case (str): Use case category
            effectiveness_score (float, optional): Score for the prompt effectiveness
            feedback_requested (str, optional): The user feedback that led to this improved prompt
            
        Returns:
            bool: True if successful
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "EXEC usp_InsertPromptAndSetActive ?, ?, ?, ?, ?",
                    (prompt_title, prompt_text, use_case, effectiveness_score, feedback_requested)
                )
                conn.commit()
                return True
                
        except Exception as e:
            logging.error(f"Error inserting prompt: {str(e)}")
            raise
    
    def insert_document_request(self, file_name, user_id=None, source_type=None):
        """
        Insert a new document processing request
        
        Args:
            file_name (str): Name of the file to process
            user_id (str, optional): User who submitted the request
            source_type (str, optional): Source type of the document
            
        Returns:
            int: DocumentID of the inserted record, or None if failed
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Execute the stored procedure
                cursor.execute(
                    "EXEC usp_InsertDocumentRequest ?, ?, ?",
                    (file_name, user_id, source_type)
                )
                
                # Move to the next result set if exists (some procedures return multiple result sets)
                while cursor.nextset():
                    pass
                
                # Get the inserted DocumentID using SCOPE_IDENTITY in a separate query
                cursor.execute("SELECT SCOPE_IDENTITY() AS DocumentID")
                result = cursor.fetchone()
                
                if result and result[0]:
                    document_id = int(result[0])
                    conn.commit()
                    return document_id
                else:
                    # If SCOPE_IDENTITY returns NULL, try to find the document by filename
                    cursor.execute("""
                        SELECT TOP 1 DocumentID 
                        FROM document_master 
                        WHERE FileName = ? 
                        ORDER BY CreatedTime DESC
                    """, (file_name,))
                    
                    fallback_result = cursor.fetchone()
                    if fallback_result:
                        document_id = int(fallback_result[0])
                        conn.commit()
                        return document_id
                    
                conn.commit()
                return None
                
        except Exception as e:
            logging.error(f"Error inserting document request: {str(e)}")
            print(f"Database error details: {str(e)}")  # Add debug output
            return None  # Return None instead of raising to prevent app crash
    
    def fetch_and_lock_next_document(self, current_status='Submitted', next_status='Processing', assigned_to=None):
        """
        Fetch and lock the next available document for processing
        
        Args:
            current_status (str): Status to look for
            next_status (str): Status to set when picked up
            assigned_to (str, optional): User to assign the document to
            
        Returns:
            dict: Document details or None if no documents available
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "EXEC usp_FetchAndLockNextDocument ?, ?, ?",
                    (current_status, next_status, assigned_to)
                )
                
                row = cursor.fetchone()
                if row and row[0] is not None:  # Check if DocumentID is not None
                    # Convert row to dictionary (adjust based on your document_master table structure)
                    columns = [column[0] for column in cursor.description]
                    return dict(zip(columns, row))
                return None
                
        except Exception as e:
            logging.error(f"Error fetching next document: {str(e)}")
            raise
    
    def update_document_master_by_id(self, document_id, extraction_status=None, extraction_output=None, 
                                   prompt_id=None, retry_count=None, error_message=None, comments=None):
        """
        Update document master record by ID using your stored procedure
        
        Args:
            document_id (int): Document ID to update
            extraction_status (str, optional): New extraction status
            extraction_output (str, optional): Extraction results
            prompt_id (int, optional): Prompt ID used
            retry_count (int, optional): Number of retries
            error_message (str, optional): Error message if any
            comments (str, optional): Additional comments
            
        Returns:
            bool: True if successful
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "EXEC usp_UpdateDocumentMasterByID ?, ?, ?, ?, ?, ?, ?",
                    (document_id, extraction_status, extraction_output, prompt_id, retry_count, error_message, comments)
                )
                conn.commit()
                return True
                
        except Exception as e:
            logging.error(f"Error updating document: {str(e)}")
            raise
    
    def get_document_by_filename(self, filename):
        """
        Get document record by filename (for tracking uploaded files)
        
        Args:
            filename (str): The filename to search for
            
        Returns:
            dict: Document details or None if not found
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT TOP 1 DocumentID, FileName, ExtractionStatus, CreatedTime, LastUpdated, 
                           UserID, SourceType, RetryCount, PromptID, ExtractionOutput, ErrorMessage, Comments
                    FROM document_master 
                    WHERE FileName = ?
                    ORDER BY CreatedTime DESC
                """, (filename,))
                
                row = cursor.fetchone()
                if row:
                    columns = [column[0] for column in cursor.description]
                    return dict(zip(columns, row))
                return None
                
        except Exception as e:
            logging.error(f"Error fetching document by filename: {str(e)}")
            raise
    
    def test_connection(self):
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 as test_value")
                result = cursor.fetchone()
                return result[0] == 1
        except Exception as e:
            logging.error(f"Connection test failed: {str(e)}")
            return False
    
    def get_connection_info(self):
        """Get connection string info for debugging (without sensitive data)"""
        try:
            conn_str = self.connection_string
            # Remove sensitive information for display
            safe_conn_str = conn_str
            if "PWD=" in safe_conn_str:
                import re
                safe_conn_str = re.sub(r'PWD=[^;]*', 'PWD=***', safe_conn_str)
            return safe_conn_str
        except Exception as e:
            return f"Error getting connection info: {str(e)}"
    
    def test_document_insertion(self, test_filename="test_file.pdf"):
        """Test document insertion procedure for debugging"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # First, check if stored procedure exists
                cursor.execute("""
                    SELECT COUNT(*) FROM sys.procedures 
                    WHERE name = 'usp_InsertDocumentRequest'
                """)
                proc_count = cursor.fetchone()[0]
                
                if proc_count == 0:
                    return {"error": "Stored procedure usp_InsertDocumentRequest not found"}
                
                # Try to insert a test document
                cursor.execute(
                    "EXEC usp_InsertDocumentRequest ?, ?, ?",
                    (test_filename, "test_user", "test_source")
                )
                
                # Get the identity
                cursor.execute("SELECT SCOPE_IDENTITY() AS DocumentID")
                result = cursor.fetchone()
                
                if result and result[0]:
                    document_id = int(result[0])
                    
                    # Clean up test record
                    cursor.execute("DELETE FROM document_master WHERE DocumentID = ?", (document_id,))
                    conn.commit()
                    
                    return {"success": True, "document_id": document_id, "message": "Test insertion successful"}
                else:
                    return {"error": "SCOPE_IDENTITY returned NULL"}
                    
        except Exception as e:
            return {"error": f"Test failed: {str(e)}"}

# Utility functions for common operations
def get_latest_prompt(use_case="Document_Extraction"):
    """Get the latest active prompt for document extraction"""
    db = DatabaseManager()
    return db.get_active_prompt(use_case)

def save_improved_prompt(prompt_text, feedback_summary, use_case="Document_Extraction", effectiveness_score=None, feedback_requested=None):
    """Save an improved prompt to the database
    
    Args:
        prompt_text (str): The improved prompt text or JSON string containing prompt data
        feedback_summary (str): Summary of feedback that led to the improvement
        use_case (str, optional): The use case category for the prompt. Defaults to "Document_Extraction"
        effectiveness_score (float, optional): Effectiveness score for the prompt
        feedback_requested (str, optional): Full feedback text that led to this improvement
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not prompt_text:
        logging.error("Cannot save empty prompt")
        return False

    db = DatabaseManager()
    prompt_title = None
    actual_prompt_text = None
    
    try:
        # Try to parse JSON from improvement agent output
        import json
        # Convert to string first if it's already a dict
        text_to_parse = prompt_text if isinstance(prompt_text, str) else json.dumps(prompt_text)
        improved_data = json.loads(text_to_parse)
        
        if isinstance(improved_data, dict):
            # Get title and text from JSON structure
            prompt_title = improved_data.get('Prompt Title')
            actual_prompt_text = improved_data.get('Prompt')
            
            # Validate we have required data
            if not prompt_title or not actual_prompt_text:
                logging.warning("JSON format valid but missing required fields")
                prompt_title = None  # Force fallback
            
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logging.warning(f"Could not parse improvement agent output as JSON: {str(e)}")
    
    # Fallback if JSON parsing failed or data was invalid
    if prompt_title is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        prompt_title = f"Improved Prompt - {timestamp} - {feedback_summary[:50]}..."
        actual_prompt_text = prompt_text
    
    try:
        success = db.insert_prompt_and_set_active(
            prompt_title=prompt_title,
            prompt_text=actual_prompt_text,
            use_case=use_case,
            effectiveness_score=effectiveness_score,
            feedback_requested=feedback_requested
        )
        
        if success:
            logging.info(f"Successfully saved improved prompt with title: {prompt_title}")
        else:
            logging.warning("Database insert returned False")
            
        return success
        
    except Exception as e:
        logging.error(f"Failed to save improved prompt: {str(e)}")
        return False