from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..deps import get_db

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("/", response_model=schemas.Expense, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: schemas.ExpenseBase,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if payload.category_id:
        category = db.get(models.Category, payload.category_id)
        if not category or category.owner_id != current_user.id:
            raise HTTPException(status_code=404, detail="Category not found")
    expense = models.Expense(owner_id=current_user.id, **payload.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/", response_model=list[schemas.Expense])
def list_expenses(
    category_id: int | None = None,
    start_date: date | None = Query(default=None, description="Inclusive start date"),
    end_date: date | None = Query(default=None, description="Inclusive end date"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.Expense).filter(models.Expense.owner_id == current_user.id)
    if category_id is not None:
        query = query.filter(models.Expense.category_id == category_id)
    if start_date is not None:
        query = query.filter(models.Expense.spent_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date is not None:
        end_ts = datetime.combine(end_date, datetime.max.time())
        query = query.filter(models.Expense.spent_at <= end_ts)
    return query.order_by(models.Expense.spent_at.desc()).all()


@router.put("/{expense_id}", response_model=schemas.Expense)
def update_expense(
    expense_id: int,
    payload: schemas.ExpenseUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expense = db.get(models.Expense, expense_id)
    if not expense or expense.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Expense not found")
    data = payload.model_dump(exclude_none=True)
    for key, value in data.items():
        setattr(expense, key, value)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expense = db.get(models.Expense, expense_id)
    if not expense or expense.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return None


@router.get("/daily", response_model=list[schemas.DailyTotal])
def daily_totals(
    start_date: date = Query(default=None, description="Defaults to last 7 days"),
    end_date: date = Query(default=None, description="Defaults to today"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    start = start_date or today - timedelta(days=6)
    end = end_date or today

    query = (
        db.query(func.date(models.Expense.spent_at).label("day"), func.sum(models.Expense.amount).label("total"))
        .filter(models.Expense.owner_id == current_user.id)
        .filter(models.Expense.spent_at >= datetime.combine(start, datetime.min.time()))
        .filter(models.Expense.spent_at <= datetime.combine(end, datetime.max.time()))
        .group_by(func.date(models.Expense.spent_at))
        .order_by(func.date(models.Expense.spent_at))
    )

    return [schemas.DailyTotal(day=row.day, total=row.total) for row in query.all()]
