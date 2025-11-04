from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

improvement_agent = LlmAgent(
    name="extraction_prompt_improver",
    model=LiteLlm(model="openai/gpt-4o"),
    description="Improves extraction prompts/instructions based on feedback.",
    instruction="""You are an assistant that rewrites or enhances extraction instructions to directly address user corrections.
Given the original extraction output and user feedback, generate a revised prompt that incorporates the feedback for the extraction agent."""
)

async def call_improvement_agent(original_extraction, feedback_text, previous_prompt):
    from google.genai import types
    import json
    context = (
        f"Previous Extraction JSON:\n{original_extraction}\n"
        f"User Feedback:\n{feedback_text}\n"
        f"Original Prompt:\n{previous_prompt}\n"
        "Based on this, generate a new prompt for the extraction agent that incorporates the feedback. Only output the new prompt."
    )
    content = types.Content(role='user', parts=[types.Part(text=context)])

    from google.adk.sessions import InMemorySessionService
    from google.adk.runners import Runner

    temp_service = InMemorySessionService()
    session = await temp_service.create_session(
        app_name="improver",
        user_id="improver_user",
        state={}
    )
    runner = Runner(app_name="improver", agent=improvement_agent, session_service=temp_service)
    gen = runner.run_async(user_id=session.user_id, session_id=session.id, new_message=content)
    
    improved_prompt = ""
    async for res in gen:
        # extract cleaned text just like before
        parts = []
        if hasattr(res, "content") and hasattr(res.content, "parts"):
            for part in res.content.parts:
                if hasattr(part, "text"):
                    parts.append(part.text)
        improved_prompt += "\n".join(parts)
    return improved_prompt.strip()
