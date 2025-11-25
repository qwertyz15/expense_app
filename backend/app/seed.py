from datetime import datetime, timedelta, date
from decimal import Decimal

from .database import get_session
from . import models


COLORS = ["#ec4899", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b"]


def seed():
    with get_session() as db:
        if db.query(models.User).count() > 0:
            return

        user = models.User(name="Demo User", email="demo@example.com")
        db.add(user)
        db.flush()

        categories = [
            models.Category(name="Food", color=COLORS[0], owner_id=user.id),
            models.Category(name="Transport", color=COLORS[1], owner_id=user.id),
            models.Category(name="Rent", color=COLORS[2], owner_id=user.id),
            models.Category(name="Health", color=COLORS[3], owner_id=user.id),
        ]
        db.add_all(categories)
        db.flush()

        today = datetime.utcnow().date()
        expenses = []
        for i in range(10):
            expenses.append(
                models.Expense(
                    description=f"Lunch {i+1}",
                    amount=Decimal("12.50"),
                    spent_at=datetime.combine(today - timedelta(days=i), datetime.min.time()),
                    owner_id=user.id,
                    category_id=categories[0].id,
                )
            )
        expenses.append(
            models.Expense(
                description="Bus pass",
                amount=Decimal("45.00"),
                spent_at=datetime.combine(today - timedelta(days=2), datetime.min.time()),
                owner_id=user.id,
                category_id=categories[1].id,
            )
        )
        expenses.append(
            models.Expense(
                description="Groceries",
                amount=Decimal("82.10"),
                spent_at=datetime.combine(today - timedelta(days=1), datetime.min.time()),
                owner_id=user.id,
                category_id=categories[0].id,
            )
        )
        db.add_all(expenses)

        budgets = [
            models.Budget(month=date(today.year, today.month, 1), amount=Decimal("1200"), owner_id=user.id),
            models.Budget(
                month=date(today.year, today.month, 1),
                amount=Decimal("300"),
                owner_id=user.id,
                category_id=categories[0].id,
            ),
        ]
        db.add_all(budgets)

        db.commit()
        print("Seed data inserted for demo user")


if __name__ == "__main__":
    seed()
