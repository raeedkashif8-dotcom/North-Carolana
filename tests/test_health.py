from fastapi.testclient import TestClient

from app.main import app


def test_healthz_without_database(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "")
    r = TestClient(app).get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
