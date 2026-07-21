from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import employees, analytics

# For this exercise, tables are created directly from models rather than via
# a migration tool (Alembic) — a real production system would use migrations,
# but that's overhead this scope doesn't need. Noted as a fast-follow.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Salary Management API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router)
app.include_router(analytics.router)


@app.get("/health")
def health():
    return {"status": "ok"}