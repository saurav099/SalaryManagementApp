import enum
from datetime import date, datetime

from sqlalchemy import (
    Column, Integer, String, Date, DateTime, ForeignKey, Enum, Index, Numeric, func
)
from sqlalchemy.orm import relationship

from app.database import Base


class EmployeeStatus(str, enum.Enum):
    active = "active"
    terminated = "terminated"


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(160), nullable=False, unique=True, index=True)
    department = Column(String(60), nullable=False, index=True)
    country = Column(String(60), nullable=False, index=True)
    job_level = Column(String(30), nullable=False, index=True)
    hire_date = Column(Date, nullable=False)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    status = Column(Enum(EmployeeStatus), nullable=False, default=EmployeeStatus.active, index=True)

    salary_records = relationship(
        "SalaryRecord", back_populates="employee", order_by="desc(SalaryRecord.effective_date)"
    )

    # Composite index: the analytics/filter queries group by these together.
    __table_args__ = (
        Index("ix_employee_dept_country_level", "department", "country", "job_level"),
    )


class SalaryRecord(Base):
    """
    Append-only history of an employee's salary. A "salary update" is always an
    INSERT of a new row, never an UPDATE of an existing one — this preserves
    full history and lets us answer "what did this person earn on date X".
    """
    __tablename__ = "salary_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False)  # ISO 4217, e.g. "USD", "INR"
    effective_date = Column(Date, nullable=False, default=date.today)
    reason = Column(String(120), nullable=True)  # e.g. "promotion", "annual review"
    created_at = Column(DateTime, server_default=func.now())

    employee = relationship("Employee", back_populates="salary_records")

    __table_args__ = (
        Index("ix_salary_employee_effective", "employee_id", "effective_date"),
    )