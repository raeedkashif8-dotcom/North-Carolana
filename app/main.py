"""Web app entry point (C-1). Run: .venv\\Scripts\\uvicorn app.main:app --reload"""
from fastapi import FastAPI
from sqlalchemy import create_engine, text

from app.settings import get_settings

app = FastAPI(title="AutoM8X Buyer Agreement Agent")


@app.get("/healthz")
def healthz():
    """Health check for the uptime monitor (ENV-6)."""
    s = get_settings()
    db = "not configured"
    if s.database_url:
        try:
            engine = create_engine(s.database_url, pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(text("select 1"))
            db = "ok"
        except Exception as e:  # report, don't crash the health check
            db = f"error: {type(e).__name__}"
    return {"status": "ok" if db in ("ok", "not configured") else "degraded", "database": db,
            "environment": s.environment}
