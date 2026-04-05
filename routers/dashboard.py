from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import FinancialRecord, RecordType, Role, User
from schemas import DashboardSummary, CategoryTotal, RecordResponse
from dependencies import require_role

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

all_roles = require_role(Role.VIEWER, Role.ANALYST, Role.ADMIN)


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    db: Session = Depends(get_db),
    _: User = Depends(all_roles),
):
    # calculates total income
    total_income = db.query(func.sum(FinancialRecord.amount)).filter(
        FinancialRecord.type == RecordType.INCOME
    ).scalar() or 0.0

    # calculate total expenses
    total_expenses = db.query(func.sum(FinancialRecord.amount)).filter(
        FinancialRecord.type == RecordType.EXPENSE
    ).scalar() or 0.0

    # category-wise totals (across all types)
    category_rows = (
        db.query(FinancialRecord.category, func.sum(FinancialRecord.amount))
        .group_by(FinancialRecord.category)
        .all()
    )
    category_totals = [
        CategoryTotal(category=row[0], total=row[1]) for row in category_rows
    ]

    # 5 most recent records
    recent = (
        db.query(FinancialRecord)
        .order_by(FinancialRecord.date.desc(), FinancialRecord.created_at.desc())
        .limit(5)
        .all()
    )

    return DashboardSummary(
        total_income=total_income,
        total_expenses=total_expenses,
        net_balance=total_income - total_expenses,
        category_totals=category_totals,
        recent_records=recent,
    )
