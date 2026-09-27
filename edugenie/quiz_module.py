"""Generate Quiz feature."""

from gemini_client import generate_with_gemini


async def generate_quiz(topic: str) -> str:
    prompt = f"""
You are EduGenie, a college quiz creator.
Create exactly 3 multiple-choice questions about the topic below.
Each question must have exactly 4 options labelled A, B, C, and D.
After each question, show the correct answer and a one-sentence explanation.
Do not create more or fewer than 3 questions.
Format the result so a student can read it easily.

Topic:
{topic}
""".strip()
    return await generate_with_gemini(prompt)