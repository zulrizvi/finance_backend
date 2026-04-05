from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database import get_db
from models import FinancialRecord, RecordType, Role, User
from schemas import RecordCreate, RecordUpdate, RecordResponse
from dependencies import require_role, get_current_user

router = APIRouter(prefix="/records", tags=["Financial Records"])

analyst_and_above = require_role(Role.ANALYST, Role.ADMIN)
admin_only = require_role(Role.ADMIN)


@router.get("", response_model=list[RecordResponse])
def list_records(
    type: Optional[RecordType] = Query(None),
    category: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(analyst_and_above),
):
    q = db.query(FinancialRecord)
    if type:
        q = q.filter(FinancialRecord.type == type)
    if category:
        q = q.filter(FinancialRecord.category.ilike(f"%{category}%"))
    if date_from:
        q = q.filter(FinancialRecord.date >= date_from)
    if date_to:
        q = q.filter(FinancialRecord.date <= date_to)

    offset = (page - 1) * limit
    return q.order_by(FinancialRecord.date.desc()).offset(offset).limit(limit).all()


@router.post("", response_model=RecordResponse, status_code=status.HTTP_201_CREATED)
def create_record(
    body: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    record = FinancialRecord(**body.model_dump(), created_by=current_user.id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/{record_id}", response_model=RecordResponse)
def update_record(
    record_id: int,
    body: RecordUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
):
    record = db.query(FinancialRecord).filter(FinancialRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
):
    record = db.query(FinancialRecord).filter(FinancialRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
