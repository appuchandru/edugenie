# EduGenie — Nan Mudhalvan Project

EduGenie is a simple Gemini-powered FastAPI web application that helps college
students ask questions, understand topics, create quizzes, summarize text, and
follow a personalized learning path.

## Features

1. Ask Question / Q&A
2. Explain a Topic
3. Generate exactly 3 multiple-choice questions with 4 options each
4. Summarize Text
5. Personalized Learning Path from beginner to advanced

## Requirements

- Python 3.10 or newer
- A Google Gemini API key stored as the `GEMINI_API_KEY` environment secret

The Gemini client uses `gemini-3.5-flash-lite` by default to reduce quota
pressure. You can optionally set `GEMINI_MODEL` to choose the primary model and
`GEMINI_FALLBACK_MODELS` to provide a comma-separated fallback list. Quota
errors do not retry the exhausted model repeatedly; temporary capacity and
network errors use short, bounded retries.

## Run it

From the repository root:

```bash
cd edugenie
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` in a browser.

The application never hard-codes the API key. It reads `GEMINI_API_KEY` only
when a student submits a task.

## Project structure

```text
edugenie/
├── main.py                  # FastAPI app and API routes
├── gemini_client.py         # Shared Gemini REST client
├── qna.py                   # Ask Question / Q&A
├── explanation_module.py    # Explain a Topic
├── quiz_module.py           # 3-question, 4-option quiz generation
├── summary_module.py        # Summarize Text
├── learning_path.py         # Beginner-to-advanced learning path
├── requirements.txt
├── templates/index.html     # Student-facing interface
└── static/style.css         # Responsive page styling
```