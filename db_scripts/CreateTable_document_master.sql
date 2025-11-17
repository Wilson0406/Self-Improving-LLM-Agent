
CREATE TABLE document_master (
    DocumentID INT IDENTITY(1,1) PRIMARY KEY,
    FileName NVARCHAR(255),
    ExtractionStatus NVARCHAR(50),
    ExtractionOutput NVARCHAR(MAX),
    CreatedTime DATETIME DEFAULT GETDATE(),
    PickedTime DATETIME NULL,
    CompletedTime DATETIME NULL,
    PromptID NVARCHAR(100) NULL,			-- LLM prompt/template variant for extraction
    LastUpdated DATETIME DEFAULT GETDATE(),
    UserID NVARCHAR(100) NULL,
    SourceType NVARCHAR(50) NULL,			-- e.g., 'PDF', 'DOCX'
    Comments NVARCHAR(MAX) NULL,
    RetryCount INT DEFAULT 0,
    ErrorMessage NVARCHAR(MAX) NULL
);
GO