import sys
import uuid
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Employee, SalaryRecord, EmployeeStatus


@pytest.fixture()
def db_session():
    """Fresh in-memory SQLite DB per test — fast, isolated, no shared state
    between tests, no dependency on a running Postgres instance."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session):
    """TestClient wired to use the test DB session instead of the real one."""

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def make_employee(db_session):
    """Factory fixture: creates an Employee + an initial SalaryRecord.
    Returns the Employee (already committed, with a real id)."""

    def _make(
        name="Test Person",
        department="Engineering",
        country="US",
        job_level="mid",
        salary=Decimal("80000.00"),
        currency="USD",
        effective_date=date(2024, 1, 1),
        manager_id=None,
    ):
        employee = Employee(
            name=name,
            email=f"{uuid.uuid4().hex[:10]}@example.com",
            department=department,
            country=country,
            job_level=job_level,
            hire_date=effective_date,
            manager_id=manager_id,
            status=EmployeeStatus.active,
        )
        db_session.add(employee)
        db_session.flush()

        db_session.add(
            SalaryRecord(
                employee_id=employee.id,
                amount=salary,
                currency=currency,
                effective_date=effective_date,
                reason="initial hire",
            )
        )
        db_session.commit()
        db_session.refresh(employee)
        return employee

    return _make