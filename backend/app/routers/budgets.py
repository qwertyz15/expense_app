from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..deps import get_db

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("/", response_model=schemas.Budget, status_code=status.HTTP_201_CREATED)
def create_budget(
    payload: schemas.BudgetBase,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    budget = models.Budget(owner_id=current_user.id, **payload.model_dump())
    db.add(budget)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(budget)
    return budget


@router.get("/", response_model=list[schemas.Budget])
def list_budgets(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(models.Budget)
        .filter(models.Budget.owner_id == current_user.id)
        .order_by(models.Budget.month.desc())
        .all()
    )


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    budget = db.get(models.Budget, budget_id)
    if not budget or budget.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Budget not found")
    db.delete(budget)
    db.commit()
    return None
