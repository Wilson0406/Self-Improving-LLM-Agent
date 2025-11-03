from google.adk.agents import LlmAgent
import os
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
from google.adk.runners import Runner
import asyncio
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()


extract_agent = LlmAgent(
    name="pdf_to_excel_extractor",
    model=LiteLlm(model="openai/gpt-4o", ),
    description="Extracts specified columns from PDF using Excel instructions.",
    instruction=f"""
        "You are an expert data extractor for business documents. "
        "Extract only the columns defined in the provided schema, and strictly follow the row instructions. "
        "Output results in JSON format with each column as a key and its extracted value from the PDF text as value."
    """
)

async def call_extraction_agent(pdf_text, columns, instructions):
    schema_str = ', '.join(columns)
    instr_str = '; '.join(instructions)
    prompt = (
        f"Extract the following columns from the PDF text:\n"
        f"Columns: {schema_str}\n"
        f"Instructions: {instr_str}\n"
        f"PDF Content:\n{pdf_text[:2000]}\n"
        "Output JSON only with column/value pairs."
    )
    
    temp_service = InMemorySessionService()
    example_session = await temp_service.create_session(
        app_name="agents",
        user_id="example_user",
        state={"initial_key": "initial_value"}
    )
    content = types.Content(role='user', parts=[types.Part(text=prompt)])
    
    runner = Runner(app_name="agents", agent=extract_agent, session_service=temp_service)
    response = runner.run_async(user_id=example_session.user_id, session_id=example_session.id, new_message=content)

    result_data = ""
    gen = response
    async for res in gen:
        # print(res)
        parts = []
        if hasattr(res, "content") and hasattr(res.content, "parts"):
            for part in res.content.parts:
                if hasattr(part, "text"):
                    parts.append(part.text)

        full_text = "\n".join(parts)
        result_data += getattr(res, "text", str(res))
    print("Agent Response:", full_text)
    return full_text

# # Example usage:
# if __name__ == "__main__":
#     # Placeholder test data (replace with actual Streamlit utility output)
#     pdf_text = "Company Name: ExampleCorp\nDate: 2023-10-01\nTotal: $1,234.56"
#     columns = ["Company Name", "Date", "Total"]
#     instructions = ["Extract the registered company name", "Format date as YYYY-MM-DD", "Get the invoice's total amount"]
#     extracted = call_extraction_agent(pdf_text, columns, instructions)
#     print("Extracted Data:", extracted)
