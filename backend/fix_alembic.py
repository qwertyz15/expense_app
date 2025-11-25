"""Script to fix Alembic version table issue"""
from app.database import db_engine
from sqlalchemy import text

def fix_alembic_version():
    """Drop the alembic_version table to reset migration state"""
    with db_engine.connect() as conn:
        # Drop the alembic_version table if it exists
        conn.execute(text('DROP TABLE IF EXISTS alembic_version'))
        conn.commit()
        print('✓ alembic_version table dropped successfully')
        print('You can now run: alembic revision --autogenerate -m "Initial migration"')

if __name__ == '__main__':
    fix_alembic_version()
