# EduGenie

EduGenie is a simple Gemini-powered FastAPI learning assistant for the Nan Mudhalvan college project.

## Run & Operate

- `pnpm --filter @workspace/api-server run dev` — run the API server (port 5000)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required env: `DATABASE_URL` — Postgres connection string
- `python -m edugenie` — show the EduGenie CLI
- `python -m unittest discover -s edugenie/tests -v` — run EduGenie tests
- `cd edugenie && uvicorn main:app --reload --host 0.0.0.0 --port 8000` — run the EduGenie web app

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)
- FastAPI, Uvicorn, Jinja2, and HTTPX
- Google Gemini REST API via `GEMINI_API_KEY`

## Where things live

_Populate as you build — short repo map plus pointers to the source-of-truth file for DB schema, API contracts, theme files, etc._

- `edugenie/main.py` — FastAPI app, page route, health route, and generation endpoint
- `edugenie/gemini_client.py` — shared Gemini API client
- `edugenie/qna.py` — Ask Question / Q&A prompt
- `edugenie/explanation_module.py` — Explain a Topic prompt
- `edugenie/quiz_module.py` — 3 MCQ prompt
- `edugenie/summary_module.py` — Summarize Text prompt
- `edugenie/learning_path.py` — Personalized Learning Path prompt
- `edugenie/templates/index.html` and `edugenie/static/style.css` — web UI
- `edugenie/tests/` — Python unit tests

## Architecture decisions

- Each requested learning task has its own small Python module so the college demo is easy to explain.
- The frontend calls one FastAPI `/generate` endpoint, which routes the selected task to the right module.
- Gemini is called through the Google REST API and the key is read only from `GEMINI_API_KEY`.
- The quiz prompt explicitly requires 3 questions and 4 options per question.

## Product

_Describe the high-level user-facing capabilities of this app once they exist._

- Students can ask questions and request topic explanations.
- Students can generate structured quizzes with 3 MCQs.
- Students can summarize pasted study material.
- Students can get a learning path from beginner to advanced.

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

_Populate as you build — sharp edges, "always run X before Y" rules._

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
