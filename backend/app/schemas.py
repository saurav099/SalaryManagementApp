from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models import EmployeeStatus


class SalaryRecordCreate(BaseModel):
    amount: Decimal
    currency: str
    effective_date: date = date.today()
    reason: Optional[str] = None


class SalaryRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    currency: str
    effective_date: date
    reason: Optional[str] = None
    created_at: datetime


class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    department: str
    country: str
    job_level: str
    hire_date: date
    manager_id: Optional[int] = None
    status: EmployeeStatus = EmployeeStatus.active


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeListItem(BaseModel):
    """Lightweight shape for the paginated list view — avoids pulling full
    salary history for every row when rendering a table of thousands."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    department: str
    country: str
    job_level: str
    status: EmployeeStatus
    current_salary: Optional[SalaryRecordOut] = None


class EmployeeDetail(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    salary_records: list[SalaryRecordOut] = []


class PaginatedEmployees(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[EmployeeListItem]


class DepartmentPayStats(BaseModel):
    group: str
    currency: str
    headcount: int
    avg_salary: Decimal
    median_salary: Decimal
    min_salary: Decimal
    max_salary: Decimal