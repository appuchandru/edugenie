"""Summarize Text feature."""

from gemini_client import generate_with_gemini


async def summarize_text(text: str) -> str:
    prompt = f"""
You are EduGenie, a study assistant.
Summarize the text below for a college student.
Return a short overview followed by 3 to 5 important bullet points.
Preserve important facts and do not add information that is not in the text.

Text to summarize:
{text}
""".strip()
    return await generate_with_gemini(prompt)