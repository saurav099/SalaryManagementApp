from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=schemas.PaginatedEmployees)
def list_employees(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: Optional[str] = None,
    department: Optional[str] = None,
    country: Optional[str] = None,
    job_level: Optional[str] = None,
    db: Session = Depends(get_db),
):
    total, employees = crud.list_employees(
        db, page, page_size, search, department, country, job_level
    )
    items = []
    for emp in employees:
        current = emp.salary_records[0] if emp.salary_records else None
        items.append(
            schemas.EmployeeListItem(
                id=emp.id,
                name=emp.name,
                email=emp.email,
                department=emp.department,
                country=emp.country,
                job_level=emp.job_level,
                status=emp.status,
                current_salary=current,
            )
        )
    return schemas.PaginatedEmployees(total=total, page=page, page_size=page_size, items=items)


@router.get("/{employee_id}", response_model=schemas.EmployeeDetail)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = crud.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.post("/{employee_id}/salary", response_model=schemas.SalaryRecordOut)
def update_salary(
    employee_id: int, record_in: schemas.SalaryRecordCreate, db: Session = Depends(get_db)
):
    employee = crud.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return crud.add_salary_record(db, employee_id, record_in)