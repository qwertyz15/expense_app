from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..deps import get_db

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: schemas.CategoryBase,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    exists = (
        db.query(models.Category)
        .filter(models.Category.owner_id == current_user.id, models.Category.name == payload.name)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Category already exists")
    category = models.Category(owner_id=current_user.id, **payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/", response_model=list[schemas.Category])
def list_categories(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(models.Category)
        .filter(models.Category.owner_id == current_user.id)
        .order_by(models.Category.name)
        .all()
    )


@router.put("/{category_id}", response_model=schemas.Category)
def update_category(
    category_id: int,
    payload: schemas.CategoryUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = db.get(models.Category, category_id)
    if not category or category.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(category, key, value)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = db.get(models.Category, category_id)
    if not category or category.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return None
