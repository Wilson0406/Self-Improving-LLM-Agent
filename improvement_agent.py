from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.genai import types
import json
import os
from dotenv import load_dotenv
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

load_dotenv()

improvement_agent = LlmAgent(
    name="extraction_prompt_improver",
    model=LiteLlm(
        model=os.getenv("OPENAI_DEPLOYMENT"),
        api_base=os.getenv("OPENAI_ENDPOINT"),
        api_key=os.getenv("OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION")
    ),
    description = "Dynamically refines and improves prompts based on received user feedback, tailoring instructions for more accurate or relevant results.",
    instruction = f"""
            "You are an expert prompt engineer for business automation and data extraction tasks."
            "When feedback is provided, carefully analyze it to understand both explicit and implicit suggestions for improvement."
            "Revise or extend the original prompt to address any gaps, ambiguities, or shortcomings highlighted in the feedback."
            "When modifying the prompt, prioritize clarity, specificity, and alignment with the user's evolving objectives, while maintaining consistency with the original intent."
            "Output the updated Prompt and Prompt Title(max 200 char) as structured JSON, ready for immediate use with minimal further revision."
            "If feedback introduces new requirements, integrate them clearly and explicitly in the revised prompt."
            "Do NOT include any PDF content, document text, or specific data in your response - only the extraction instructions and format specifications."
    """
)

async def call_improvement_agent(original_extraction, feedback_text, previous_prompt):
    context = (
        f"Previous Extraction JSON:\n{original_extraction}\n"
        f"User Feedback:\n{feedback_text}\n"
        f"Original Prompt:\n{previous_prompt}\n\n"
        "Based on the feedback above, generate an improved extraction prompt template that addresses the user's concerns. "
        "Output ONLY the improved prompt template/instructions - do NOT include any PDF content, document text, or specific data. "
        "Focus on the extraction instructions, format specifications, and any new requirements from the feedback."
    )
    content = types.Content(role='user', parts=[types.Part(text=context)])

    temp_service = InMemorySessionService()
    session = await temp_service.create_session(
        app_name="improver",
        user_id="improver_user",
        state={}
    )
    runner = Runner(app_name="improver", agent=improvement_agent, session_service=temp_service)
    gen = runner.run_async(user_id=session.user_id, session_id=session.id, new_message=content)
    
    response_text = ""
    async for res in gen:
        # extract cleaned text just like before
        parts = []
        if hasattr(res, "content") and hasattr(res.content, "parts"):
            for part in res.content.parts:
                if hasattr(part, "text"):
                    parts.append(part.text)
        response_text += "\n".join(parts)
    
    response_text = response_text.strip()
    
    # Try to parse as JSON first
    try:
        json_data = json.loads(response_text)
        if isinstance(json_data, dict) and 'Prompt Title' in json_data and 'Prompt' in json_data:
            return response_text  # Return JSON string directly
    except json.JSONDecodeError:
        pass  # Not valid JSON, continue with fallback
        
    # If not valid JSON with required fields, wrap the text in our own JSON structure
    return json.dumps({
        "Prompt Title": "Improved Prompt",
        "Prompt": response_text
    })
