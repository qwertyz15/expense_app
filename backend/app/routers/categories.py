from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_category(payload: schemas.CategoryCreate, db: Session = Depends(get_db)):
    exists = (
        db.query(models.Category)
        .filter(models.Category.owner_id == payload.owner_id, models.Category.name == payload.name)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Category already exists")
    category = models.Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/", response_model=list[schemas.Category])
def list_categories(owner_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Category)
    if owner_id is not None:
        query = query.filter(models.Category.owner_id == owner_id)
    return query.order_by(models.Category.name).all()


@router.put("/{category_id}", response_model=schemas.Category)
def update_category(category_id: int, payload: schemas.CategoryUpdate, db: Session = Depends(get_db)):
    category = db.get(models.Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(category, key, value)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.get(models.Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return None
