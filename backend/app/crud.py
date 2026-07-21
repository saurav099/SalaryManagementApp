from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Employee, SalaryRecord


def _current_salary_subquery(db: Session):
    """Latest salary_record.id per employee, by effective_date then created_at."""
    return (
        select(
            SalaryRecord.employee_id,
            func.max(SalaryRecord.id).label("latest_id"),
        )
        .group_by(SalaryRecord.employee_id)
        .subquery()
    )


def list_employees(
    db: Session,
    page: int = 1,
    page_size: int = 25,
    search: Optional[str] = None,
    department: Optional[str] = None,
    country: Optional[str] = None,
    job_level: Optional[str] = None,
):
    query = db.query(Employee)

    if search:
        like = f"%{search}%"
        query = query.filter((Employee.name.ilike(like)) | (Employee.email.ilike(like)))
    if department:
        query = query.filter(Employee.department == department)
    if country:
        query = query.filter(Employee.country == country)
    if job_level:
        query = query.filter(Employee.job_level == job_level)

    total = query.count()
    employees = (
        query.order_by(Employee.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return total, employees


def get_employee(db: Session, employee_id: int) -> Optional[Employee]:
    return db.query(Employee).filter(Employee.id == employee_id).first()


def add_salary_record(db: Session, employee_id: int, record_in) -> SalaryRecord:
    record = SalaryRecord(employee_id=employee_id, **record_in.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def pay_stats_by(db: Session, group_column):
    """
    Aggregate salary stats grouped by an Employee column (department/country/job_level),
    using each employee's most recent salary record.

    Deliberately ALSO groups by currency: with no FX conversion in scope (see
    requirements doc), summing/averaging amounts across currencies would produce a
    meaningless number (e.g. INR and USD amounts added together). Each row returned
    here is single-currency and therefore actually means something. The trade-off is
    a department can appear as multiple rows (one per currency present in it) instead
    of one combined row -- that's the honest reflection of "no FX conversion," not an
    extra feature.
    """
    latest = _current_salary_subquery(db)

    rows = (
        db.query(
            group_column.label("group"),
            SalaryRecord.currency.label("currency"),
            func.count(Employee.id).label("headcount"),
            func.avg(SalaryRecord.amount).label("avg_salary"),
            func.min(SalaryRecord.amount).label("min_salary"),
            func.max(SalaryRecord.amount).label("max_salary"),
        )
        .join(latest, latest.c.employee_id == Employee.id)
        .join(SalaryRecord, SalaryRecord.id == latest.c.latest_id)
        .group_by(group_column, SalaryRecord.currency)
        .order_by(group_column, SalaryRecord.currency)
        .all()
    )

    # Median isn't a portable SQL aggregate across SQLite/Postgres, so it's
    # computed in Python per (group, currency) -- fine at this scale (grouped, not per-row).
    results = []
    for row in rows:
        amounts = sorted(
            r.amount
            for r in db.query(SalaryRecord.amount)
            .join(latest, latest.c.latest_id == SalaryRecord.id)
            .join(Employee, Employee.id == latest.c.employee_id)
            .filter(group_column == row.group, SalaryRecord.currency == row.currency)
            .all()
        )
        mid = len(amounts) // 2
        median = amounts[mid] if len(amounts) % 2 else (amounts[mid - 1] + amounts[mid]) / 2
        results.append(
            {
                "group": row.group,
                "currency": row.currency,
                "headcount": row.headcount,
                "avg_salary": round(row.avg_salary, 2),
                "median_salary": round(median, 2),
                "min_salary": row.min_salary,
                "max_salary": row.max_salary,
            }
        )
    return results