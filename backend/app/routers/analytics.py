from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.models import Employee

router = APIRouter(prefix="/analytics", tags=["analytics"])

_GROUP_COLUMNS = {
    "department": Employee.department,
    "country": Employee.country,
    "job_level": Employee.job_level,
}


@router.get("/pay-by/{dimension}", response_model=list[schemas.DepartmentPayStats])
def pay_by_dimension(dimension: str, db: Session = Depends(get_db)):
    column = _GROUP_COLUMNS.get(dimension)
    if column is None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail=f"Unknown dimension '{dimension}'. Use one of: {list(_GROUP_COLUMNS)}",
        )
    return crud.pay_stats_by(db, column)