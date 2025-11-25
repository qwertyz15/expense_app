from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    pass


class UserRegister(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


class User(UserBase):
    id: int
    created_at: datetime

    model_config = dict(from_attributes=True)


class CategoryBase(BaseModel):
    name: str
    color: str = Field("#3b82f6", description="Hex color used for UI chips")


class CategoryCreate(CategoryBase):
    owner_id: int


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class Category(CategoryBase):
    id: int
    owner_id: int

    model_config = dict(from_attributes=True)


class ExpenseBase(BaseModel):
    description: str
    amount: Decimal = Field(..., gt=0)
    spent_at: datetime = Field(default_factory=datetime.utcnow)
    category_id: Optional[int] = None


class ExpenseCreate(ExpenseBase):
    owner_id: int


class ExpenseUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[Decimal] = Field(default=None, gt=0)
    spent_at: Optional[datetime] = None
    category_id: Optional[int] = None


class Expense(ExpenseBase):
    id: int
    owner_id: int

    model_config = dict(from_attributes=True)


class BudgetBase(BaseModel):
    month: date = Field(description="First day of the target month")
    amount: Decimal = Field(..., gt=0)
    category_id: Optional[int] = Field(default=None, description="Null for an overall budget")


class BudgetCreate(BudgetBase):
    owner_id: int


class Budget(BudgetBase):
    id: int
    owner_id: int

    model_config = dict(from_attributes=True)


class DailyTotal(BaseModel):
    day: date
    total: Decimal


class TopCategoryBreakdown(BaseModel):
    category_id: int
    name: str
    color: str
    total: Decimal


class DashboardSummary(BaseModel):
    total_spent: Decimal
    month_to_date: Decimal
    budgets: List[Budget]
    top_categories: List[TopCategoryBreakdown]
