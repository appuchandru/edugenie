"""Ask Question / Q&A feature."""

from gemini_client import generate_with_gemini


async def answer_question(question: str) -> str:
    prompt = f"""
You are EduGenie, a friendly college learning assistant.
Answer the student's question clearly and accurately.
Use simple language, short paragraphs, and one small example when useful.
If the question is unclear, say what extra detail would help.

Student question:
{question}
""".strip()
    return await generate_with_gemini(prompt)