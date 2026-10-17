"""Create the working schema and tables. Safe to run twice.

Run: .venv\\Scripts\\python -m app.initdb
(Alembic migrations replace this before production: see CHECKPOINTS CP1 rules.)
"""
from app import db
from app.settings import get_settings

if __name__ == "__main__":
    s = get_settings()
    eng = db.make_engine(s.database_url, schema=s.db_schema)
    db.create_all(eng)
    print(f"schema '{s.db_schema}' ready")
