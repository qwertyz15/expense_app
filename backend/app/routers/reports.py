from datetime import date, datetime
from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..deps import get_db

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/dashboard", response_model=schemas.DashboardSummary)
def dashboard(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total_spent = db.query(func.coalesce(func.sum(models.Expense.amount), 0)).filter(models.Expense.owner_id == current_user.id).scalar()

    today = date.today()
    month_start = datetime(today.year, today.month, 1)
    month_to_date = (
        db.query(func.coalesce(func.sum(models.Expense.amount), 0))
        .filter(models.Expense.owner_id == current_user.id)
        .filter(models.Expense.spent_at >= month_start)
        .scalar()
    )

    budgets = (
        db.query(models.Budget)
        .filter(models.Budget.owner_id == current_user.id)
        .order_by(models.Budget.month.desc())
        .all()
    )

    top_categories_rows = (
        db.query(
            models.Category.id.label("category_id"),
            models.Category.name,
            models.Category.color,
            func.coalesce(func.sum(models.Expense.amount), 0).label("total"),
        )
        .join(models.Expense, models.Category.id == models.Expense.category_id)
        .filter(models.Expense.owner_id == current_user.id)
        .group_by(models.Category.id, models.Category.name, models.Category.color)
        .order_by(func.sum(models.Expense.amount).desc())
        .limit(4)
        .all()
    )

    top_categories = [
        schemas.TopCategoryBreakdown(
            category_id=row.category_id, name=row.name, color=row.color, total=row.total
        )
        for row in top_categories_rows
    ]

    return schemas.DashboardSummary(
        total_spent=total_spent or Decimal("0"),
        month_to_date=month_to_date or Decimal("0"),
        budgets=budgets,
        top_categories=top_categories,
    )
