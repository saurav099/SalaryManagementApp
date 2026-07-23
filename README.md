# ACME Salary Management System

A web application that replaces ACME's spreadsheet-based salary tracking, letting the HR Manager view, update, and understand salary data for ~10,000 employees across multiple countries.

Built for the Incubyte Software Craftsperson / Python / AI-III take-home assessment.

## Live deployment

- **App**: https://salary-management-app-beta.vercel.app
- **API**: https://salarymanagementapp-production.up.railway.app
- **API docs (Swagger)**: https://salarymanagementapp-production.up.railway.app/docs

## What this is

Full requirements, scope, and — importantly — what was **deliberately left out and why**, are in [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md). Read that first; it's the one-page doc that frames every decision below.

Short version: HR manager can search/filter a paginated directory of 10,000 employees, view an employee's full salary history (not just their current salary), record a salary change, and see org-wide pay analytics broken down by department, country, and job level.

## Architecture

```
┌─────────────┐         ┌──────────────┐        ┌────────────┐
│  React (TS) │─HTTP─▶ |  FastAPI      │ ─SQL─▶│ PostgreSQL │
│  Vite       │         │  SQLAlchemy  │        │            │
└─────────────┘         └──────────────┘        └────────────┘
   Vercel                  Railway                  Railway
```

**Backend** — FastAPI + SQLAlchemy + PostgreSQL (SQLite fallback for local dev with zero setup). Two tables: `Employee` and `SalaryRecord`. Salary changes are
**append-only** — updating a salary inserts a new dated record rather than overwriting the existing one, so full history is always available and nothing is ever silently lost. See [`backend/app/models.py`](backend/app/models.py) for the reasoning in context.

**Frontend** — React + TypeScript + Vite + Tailwind, with Recharts for the analytics chart. No component library dependency beyond Tailwind utilities — kept deliberately light for a 3-page app.

**Analytics** — pay statistics are grouped by **dimension AND currency**, never mixed. Averaging a USD salary with an INR salary without a real FX rate produces a meaningless number, so the API always returns one row per `(department|country|job_level, currency)` combination instead of silently merging currencies into a single misleading average. This surfaced as a real bug during development — see `docs/AI_WORKFLOW.md` for how it was caught and fixed.

## Folder structure

```
SalaryManagementApp/
├── docs/
│   ├── REQUIREMENTS.md      # goal, scope, what's excluded and why
│   └── AI_WORKFLOW.md       # how AI tools were used through the build
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app, CORS, table creation
│   │   ├── database.py       # SQLAlchemy engine/session
│   │   ├── models.py         # Employee, SalaryRecord
│   │   ├── schemas.py        # Pydantic request/response shapes
│   │   ├── crud.py           # query logic (list/filter/paginate, analytics)
│   │   └── routers/          # HTTP layer (employees, analytics)
│   ├── seed/
│   │   └── seed.py           # generates 10,000 employees with a plausible hierarchy
│   ├── tests/                # pytest suite (13 tests, 96% coverage on app/)
│   └── requirements.txt
└── frontend/
    └── src/
        ├── api/client.ts      # typed API calls
        ├── types/             # shared TS types + filter-dropdown constants
        ├── components/        # Layout (nav shell)
        └── pages/             # EmployeeList, EmployeeDetail, Analytics
```

## Running it locally

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows; use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
python -m seed.seed          # seeds 10,000 employees into a local SQLite file
uvicorn app.main:app --reload
```
Visit `http://localhost:8000/docs` for the interactive API docs.

**Frontend** (in a second terminal):
```bash
cd frontend
npm install
npm run dev
```
Visit `http://localhost:3000`.

**Tests:**
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app --cov-report=term-missing   # coverage report
```

## Known limitations / fast follows

These are deliberate scope cuts explained in full in [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md):

- No authentication — single trusted HR-admin user assumed.
- No live FX conversion — analytics are correct within a currency, never merged across currencies.
- No CSV bulk import/export.
- No database migrations (Alembic) — tables are created directly from models; fine for this exercise, not how a long-lived production schema should evolve.
- Department/country/job-level filter options are hardcoded in the frontend (kept in sync with `seed/seed.py`) rather than served from a "distinct values" endpoint.