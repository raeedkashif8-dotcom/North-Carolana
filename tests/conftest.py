import os

import pytest
from sqlalchemy import text

from app import db
from app.settings import get_settings

TEST_SCHEMA = os.environ.get("TEST_DB_SCHEMA", "app_test")  # never "app" (D-34)


@pytest.fixture(scope="session")
def engine():
    url = get_settings().database_url
    if not url:
        pytest.skip("no DATABASE_URL: database tests skipped")
    eng = db.make_engine(url, schema=TEST_SCHEMA)
    db.drop_schema(eng)
    db.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def conn(engine):
    """Each test runs inside a transaction that is rolled back, so tests can't affect each other."""
    with engine.connect() as c:
        tx = c.begin()
        yield c
        tx.rollback()


@pytest.fixture
def agent(conn):
    conn.execute(db.agents.insert().values(id="demo-agent", timezone="America/New_York"))
    return "demo-agent"


def savepoint_error(conn, stmt):
    """Run stmt in a savepoint; return the error it raised (or None) and keep the outer transaction usable."""
    sp = conn.begin_nested()
    try:
        conn.execute(stmt if not isinstance(stmt, str) else text(stmt))
        sp.commit()
        return None
    except Exception as e:
        sp.rollback()
        return e
