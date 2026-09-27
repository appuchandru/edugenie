"""FastAPI application for the EduGenie Nan Mudhalvan project."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from explanation_module import explain_topic
from gemini_client import GeminiError
from learning_path import create_learning_path
from qna import answer_question
from quiz_module import generate_quiz
from summary_module import summarize_text


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="EduGenie",
    description="A simple Gemini-powered learning assistant for college students.",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


class GenerateRequest(BaseModel):
    task: str = Field(min_length=1)
    user_input: str = Field(min_length=1, max_length=12000)


TASK_LABELS = {
    "qna": "Ask Question / Q&A",
    "explain": "Explain a Topic",
    "quiz": "Generate Quiz",
    "summarize": "Summarize Text",
    "learning_path": "Personalized Learning Path",
}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"task_labels": TASK_LABELS},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "app": "EduGenie"}


@app.post("/generate")
async def generate(request: GenerateRequest) -> dict[str, str]:
    """Route the selected task to its feature module."""

    handlers = {
        "qna": answer_question,
        "explain": explain_topic,
        "quiz": generate_quiz,
        "summarize": summarize_text,
        "learning_path": create_learning_path,
    }
    handler = handlers.get(request.task)
    if handler is None:
        return {
            "success": "false",
            "result": "Please choose one of the EduGenie tasks.",
        }

    try:
        result = await handler(request.user_input.strip())
    except GeminiError as error:
        return {"success": "false", "result": str(error)}
    return {
        "success": "true",
        "task": TASK_LABELS[request.task],
        "result": result,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )