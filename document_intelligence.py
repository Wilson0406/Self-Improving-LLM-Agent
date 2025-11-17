
from pydantic import BaseModel, Field
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, DocumentContentFormat, AnalyzeResult
from azure.ai.documentintelligence import DocumentIntelligenceClient
import os
from openai import AzureOpenAI
import pandas as pd
import re
import io
import json

endpoint = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
fr_key = os.getenv("DOCUMENT_INTELLIGENCE_KEY")

def doc_intelligence(file_input):
    # Handle both file paths (strings) and file content (bytes)
    if isinstance(file_input, str):
        # If it's a file path
        with open(file_input, "rb") as file:
            f = file.read()
    else:
        # If it's already file content (bytes)
        f = file_input
    
    document_analysis_client = DocumentIntelligenceClient(
            endpoint=endpoint, credential=AzureKeyCredential(fr_key)
        )

    poller = document_analysis_client.begin_analyze_document("prebuilt-layout", f, content_type="application/octet-stream", output_content_format=DocumentContentFormat.MARKDOWN)
    result = poller.result()

    content_per_page = []
    page_number = 1
    content = ""
    for page in result.pages: 
        cont = result.content[page.spans[0]['offset']: page.spans[0]['offset'] + page.spans[0]['length']]
        # content += cont + "\n\n"
        content += f"Page {page_number}:\n{cont}\n\n"
        content_per_page.append({"page_number": page_number, "content": cont})
        page_number+=1
    # print(content)
    return content