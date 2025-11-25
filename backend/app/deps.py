from fastapi import Depends
from sqlalchemy.orm import Session

from .database import get_session


def get_db() -> Session:
    # FastAPI dependency to provide a SQLAlchemy session per request
    with get_session() as session:
        yield session
