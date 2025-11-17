from google.adk.agents import LlmAgent
import os
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
from google.adk.runners import Runner
import asyncio
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

# Configure for Azure OpenAI
extract_agent = LlmAgent(
    name="pdf_to_excel_extractor",
    model=LiteLlm(
        model=os.getenv("OPENAI_DEPLOYMENT"),
        api_base=os.getenv("OPENAI_ENDPOINT"),
        api_key=os.getenv("OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION")
    ),
    description="Extracts specified columns from PDF using Excel instructions.",
    instruction=f"""
        "You are an expert data extractor for business documents. "
        "Extract only the columns defined in the provided schema, and strictly follow the row instructions. "
        "Output results in JSON format with each column as a key and its extracted value from the PDF text as value."
    """
)

async def call_extraction_agent(prompt, columns, instructions):
    # Use the prompt that's passed in directly instead of rebuilding it
    
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
