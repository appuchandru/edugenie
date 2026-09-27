"""Personalized Learning Path feature."""

from gemini_client import generate_with_gemini


async def create_learning_path(topic: str) -> str:
    prompt = f"""
You are EduGenie, a personal learning-path designer for college students.
Create a practical learning path for the requested topic.
Organize it into exactly three stages: Beginner, Intermediate, and Advanced.
For each stage include topics to learn, a small practice activity, and a
clear outcome. Finish with a suggested weekly sequence.

Topic:
{topic}
""".strip()
    return await generate_with_gemini(prompt)