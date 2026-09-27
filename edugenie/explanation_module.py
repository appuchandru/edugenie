"""Explain a Topic feature."""

from gemini_client import generate_with_gemini


async def explain_topic(topic: str) -> str:
    prompt = f"""
You are EduGenie, explaining a college topic to a student.
Explain the requested topic from basic idea to a little more detail.
Use headings for Definition, How it works, and Example.
Avoid unnecessary jargon and keep the response suitable for a classroom demo.

Topic:
{topic}
""".strip()
    return await generate_with_gemini(prompt)