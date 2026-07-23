import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import employees, analytics

# For this exercise, tables are created directly from models rather than via
# a migration tool (Alembic) — a real production system would use migrations,
# but that's overhead this scope doesn't need. Noted as a fast-follow.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Salary Management API", version="0.1.0")

# Local dev origins are always allowed. The deployed frontend origin is read
# from an env var (set on Railway) rather than hardcoded, so this file doesn't
# need to change again once the Vercel URL is known.
default_origins = ["http://localhost:3000", "http://localhost:5173"]
extra_origin = os.getenv("FRONTEND_ORIGIN")
allow_origins = default_origins + ([extra_origin] if extra_origin else [])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router)
app.include_router(analytics.router)


@app.get("/health")
def health():
    return {"status": "ok"}