# Self-Improving-LLM-Agent


## Overview

This project is a web-based tool that helps users extract structured data from PDF documents based on an Excel template. Users can upload a PDF file and an Excel file specifying the desired fields and extraction instructions. The application uses a language model to map information from the PDF to the Excel structure, presents the results for review, and lets users leave feedback. Submitted feedback is used to generate improved prompts and rerun extraction, with both original and updated results shown for comparison.

---

## Features

- Upload a PDF and Excel file together to start an extraction session.
- Automatically extracts data from the PDF based on column names and instructions in the Excel file.
- Shows the extracted data in a readable format for validation.
- Allows users to submit feedback or corrections for specific extracted fields.
- Uses a secondary agent to improve the extraction prompt based on feedback and reruns the extraction.
- Displays both the original and improved outputs side by side.

---

## Tech Stack

- **Python:** Entire backend logic and integrations.
- **Streamlit:** User interface for uploading files, viewing results, and submitting feedback.
- **Google ADK:** Agent development and orchestration.
- **GPT-5:** For extraction and prompt refinement via Google ADK.
- **Azure Document Intelligence:** Reads text from PDF files.
- **openpyxl:** Reads Excel schemas and instructions.

---

## How to Run

1. Clone the repository and navigate to the project folder.

2. Create and activate environment:
```python -m venv env```
```env\Scripts\activate```
3. Install required packages:
```pip install -r requirements.txt```


4. Add your Google ADK and GPT-4o keys/configuration to a `.env` file (see ADK docs).

5. Run the app:
```streamlit run app.py```

6. Upload a PDF and Excel file using the sidebar form.

7. Review and correct the extracted information. When you submit feedback, the tool will show both the original extraction and the improved result (after incorporating your feedback).

---

## Example Workflow

1. Upload an invoice PDF and an Excel sheet containing column names like `Company Name`, `Date`, `Total` and row 2 containing extraction instructions if any.
2. View extracted data in Table/JSON format.
3. If any field is incorrect or incomplete, enter feedback (e.g., “Total value missing currency symbol”).
4. The prompt improvement agent will rewrite the extraction instructions using your feedback and re-run the extraction, showing both versions for easy comparison.

---

## Folder Structure

├── main.py # Main Streamlit app
├── extraction_agent.py # Extraction agent code (LLM + ADK)
├── improvement_agent.py # Prompt improvement agent code
├── document_intelligence.py # Azure Document Intelligence wrapper: reads PDF, extracts text/blocks/metadata and returns structured page content for the extraction agent  
├── database.py # Persistence layer: extracted results, feedback, and improved prompts; simple CRUD helpers for the app  

├── requirements.txt # Python dependencies
├── .env # API keys and config (not committed)


---

With ❤️ by Team ByteHeads07