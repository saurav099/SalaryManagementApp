"""
Seeds the database with 10,000 employees across departments/countries/levels,
with a plausible reporting hierarchy and non-flat salary distribution.

Run from the `backend/` directory:
    python -m seed.seed
"""
import random
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

# Allow running as `python -m seed.seed` or `python seed/seed.py` from backend/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from faker import Faker
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.models import Employee, SalaryRecord, EmployeeStatus

fake = Faker()
random.seed(42)  # fixed seed -> reproducible data across runs, useful for demo/tests

TOTAL_EMPLOYEES = 10_000

DEPARTMENTS = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations"]

# market_multiplier scales the USD base band into a plausible number for that
# country/currency. These are illustrative, not real FX/market-survey data —
# the goal is realistic-looking spread for the analytics view, not accuracy.
COUNTRIES = {
    "US": {"currency": "USD", "market_multiplier": 1.0},
    "UK": {"currency": "GBP", "market_multiplier": 0.80},
    "India": {"currency": "INR", "market_multiplier": 45.0},
    "Germany": {"currency": "EUR", "market_multiplier": 0.85},
    "Singapore": {"currency": "SGD", "market_multiplier": 1.30},
}

# Annual base salary bands (USD-equivalent), before country market_multiplier.
LEVEL_BANDS_USD = {
    "junior": (45_000, 65_000),
    "mid": (65_000, 95_000),
    "senior": (95_000, 140_000),
    "lead": (130_000, 170_000),
    "manager": (150_000, 210_000),
    "ceo": (300_000, 500_000),
}

# Narrow at the top, wide at the base — must sum to TOTAL_EMPLOYEES.
LEVEL_COUNTS = {
    "ceo": 1,
    "manager": 99,
    "lead": 400,
    "senior": 2000,
    "mid": 4000,
    "junior": 3500,
}
assert sum(LEVEL_COUNTS.values()) == TOTAL_EMPLOYEES

# Top-to-bottom processing order, so a level's potential managers already
# exist (with real DB ids) by the time we assign manager_id.
LEVEL_ORDER = ["ceo", "manager", "lead", "senior", "mid", "junior"]
REPORTS_TO = {
    "manager": "ceo",
    "lead": "manager",
    "senior": "lead",
    "mid": "lead",
    "junior": "mid",
}


def random_salary(level: str, country: str) -> tuple[Decimal, str]:
    lo, hi = LEVEL_BANDS_USD[level]
    base = random.uniform(lo, hi)
    amount = round(base * COUNTRIES[country]["market_multiplier"], 2)
    return Decimal(str(amount)), COUNTRIES[country]["currency"]


def random_hire_date() -> date:
    days_back = random.randint(30, 365 * 12)
    return date.today() - timedelta(days=days_back)


def seed(total: int = TOTAL_EMPLOYEES):
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Wipe existing seed data so the script is safely re-runnable.
    db.query(SalaryRecord).delete()
    db.query(Employee).delete()
    db.commit()

    # Per-level, per-department pools of employee ids already created —
    # used to pick a plausible manager from the level above.
    pools: dict[str, dict[str, list[int]]] = {
        lvl: {d: [] for d in DEPARTMENTS} for lvl in LEVEL_ORDER
    }
    used_emails: set[str] = set()

    def unique_email(name: str) -> str:
        base = name.lower().replace(" ", ".").replace("'", "")
        email, n = f"{base}@acme-corp.com", 1
        while email in used_emails:
            email = f"{base}{n}@acme-corp.com"
            n += 1
        used_emails.add(email)
        return email

    scale = total / TOTAL_EMPLOYEES

    for level in LEVEL_ORDER:
        count = max(1, round(LEVEL_COUNTS[level] * scale))
        for _ in range(count):
            name = fake.name()
            department = random.choice(DEPARTMENTS)
            country = random.choice(list(COUNTRIES.keys()))

            manager_id = None
            report_level = REPORTS_TO.get(level)
            if report_level:
                # Prefer a manager in the same department; fall back to any
                # manager at that level (random dept assignment can leave a
                # department without one yet, especially at small counts).
                same_dept = pools[report_level][department]
                candidates = same_dept or [
                    mid for pool in pools[report_level].values() for mid in pool
                ]
                if candidates:
                    manager_id = random.choice(candidates)

            employee = Employee(
                name=name,
                email=unique_email(name),
                department=department,
                country=country,
                job_level=level,
                hire_date=random_hire_date(),
                manager_id=manager_id,
                status=EmployeeStatus.active,
            )
            db.add(employee)
            db.flush()  # assigns employee.id without committing yet

            amount, currency = random_salary(level, country)
            db.add(
                SalaryRecord(
                    employee_id=employee.id,
                    amount=amount,
                    currency=currency,
                    effective_date=employee.hire_date,
                    reason="initial hire",
                )
            )
            pools[level][department].append(employee.id)

        db.commit()
        print(f"Seeded {count} employees at level '{level}'")

    print(f"Done. Total employees: {db.query(Employee).count()}")
    db.close()


if __name__ == "__main__":
    seed()