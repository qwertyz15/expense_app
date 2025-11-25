#!/usr/bin/env python
"""
Script to drop all tables and run Alembic migrations step by step.

This script will:
1. Drop all existing tables in the database
2. Drop the alembic_version table
3. Run all migrations step by step from base to head

Usage:
    python reset_and_migrate.py
"""
import subprocess
import sys
from sqlalchemy import text, inspect
from app.database import db_engine


def print_step(step_num, message):
    """Print a formatted step message"""
    print(f"\n{'='*60}")
    print(f"Step {step_num}: {message}")
    print('='*60)


def drop_all_tables():
    """Drop all tables in the database including alembic_version"""
    print_step(1, "Dropping all existing tables")
    
    with db_engine.connect() as conn:
        # Get inspector to list all tables
        inspector = inspect(db_engine)
        tables = inspector.get_table_names()
        
        if not tables:
            print("✓ No tables found in database")
            return
        
        print(f"Found {len(tables)} tables: {', '.join(tables)}")
        
        # Drop all tables using CASCADE to handle foreign key constraints
        for table in tables:
            print(f"  Dropping table: {table}")
            conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
        
        # Also drop alembic_version if it exists
        print("  Dropping table: alembic_version")
        conn.execute(text('DROP TABLE IF EXISTS alembic_version CASCADE'))
        
        conn.commit()
        print("✓ All tables dropped successfully")


def get_migration_revisions():
    """Get list of all migration revisions in order"""
    print_step(2, "Getting list of migrations")
    
    try:
        result = subprocess.run(
            ['alembic', 'history'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the output to get revision IDs
        revisions = []
        for line in result.stdout.split('\n'):
            if '->' in line:
                # Extract revision ID (format: "rev_id (head) -> rev_id, message")
                parts = line.split(',')[0].strip()
                if '->' in parts:
                    rev_id = parts.split('->')[1].strip().split()[0]
                    revisions.append(rev_id)
        
        # Reverse to get chronological order (base to head)
        revisions.reverse()
        
        print(f"✓ Found {len(revisions)} migration(s)")
        for i, rev in enumerate(revisions, 1):
            print(f"  {i}. {rev}")
        
        return revisions
    except subprocess.CalledProcessError as e:
        print(f"✗ Error getting migration history: {e}")
        return []


def run_migrations_step_by_step(revisions):
    """Run migrations one by one"""
    print_step(3, "Running migrations step by step")
    
    if not revisions:
        print("No migrations to run")
        return False
    
    for i, revision in enumerate(revisions, 1):
        print(f"\n--- Migration {i}/{len(revisions)}: {revision} ---")
        
        try:
            result = subprocess.run(
                ['alembic', 'upgrade', revision],
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)
            print(f"✓ Migration {revision} applied successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error applying migration {revision}:")
            print(e.stdout)
            print(e.stderr)
            return False
    
    return True


def verify_migrations():
    """Verify that all migrations have been applied"""
    print_step(4, "Verifying migration status")
    
    try:
        result = subprocess.run(
            ['alembic', 'current'],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        print("✓ Migration verification complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error verifying migrations: {e}")
        return False


def list_tables():
    """List all tables in the database after migration"""
    print_step(5, "Listing all tables in database")
    
    inspector = inspect(db_engine)
    tables = inspector.get_table_names()
    
    if tables:
        print(f"✓ Found {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  - {table}")
    else:
        print("✗ No tables found")


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("DATABASE RESET AND MIGRATION SCRIPT")
    print("="*60)
    print("\nWARNING: This will DROP ALL TABLES in your database!")
    print("Make sure you have a backup if needed.\n")
    
    # Ask for confirmation
    response = input("Do you want to continue? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("\n✗ Operation cancelled by user")
        sys.exit(0)
    
    try:
        # Step 1: Drop all tables
        drop_all_tables()
        
        # Step 2: Get migration revisions
        revisions = get_migration_revisions()
        
        # Step 3: Run migrations step by step
        if revisions:
            success = run_migrations_step_by_step(revisions)
            if not success:
                print("\n✗ Migration process failed")
                sys.exit(1)
        else:
            # If no revisions found, just upgrade to head
            print("\nRunning 'alembic upgrade head' instead...")
            subprocess.run(['alembic', 'upgrade', 'head'], check=True)
        
        # Step 4: Verify migrations
        verify_migrations()
        
        # Step 5: List final tables
        list_tables()
        
        print("\n" + "="*60)
        print("✓ DATABASE RESET AND MIGRATION COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
