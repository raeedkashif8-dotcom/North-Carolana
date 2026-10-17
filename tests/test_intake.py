"""CP1-T5 intake. TP-U-SM-01 (intake part), TP-U-SM-02, TP-U-SM-18, TP-CMP-19, FR-3, FR-6."""
import re
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app import db
from app.main import app, get_conn

FORM = "/f/demo-agent/website_form"


@pytest.fixture
def client(conn):
    app.dependency_overrides[get_conn] = lambda: conn
    yield TestClient(app)
    app.dependency_overrides.clear()


def submit(client, **fields):
    data = {"submission_id": str(uuid.uuid4()), "name": "Test Buyer", "email": "", "phone": "", "zip": ""}
    data.update(fields)
    return client.post(FORM, data=data)


def count(conn, table, *where):
    return conn.execute(select(func.count()).select_from(table).where(*where)).scalar()


def lead_rows(conn):
    return conn.execute(select(db.leads)).mappings().all()


def test_form_page_shows_consent_and_demo_label(client):
    r = client.get(FORM)
    assert r.status_code == 200
    assert "Reply STOP to opt out" in r.text and "Demo agent" in r.text
    assert re.search(r'name="submission_id" value="[0-9a-f-]{36}"', r.text)


def test_sm_01_new_lead_with_email(client, conn):
    r = submit(client, email="Buyer@Example.com", zip="27601")
    assert r.status_code == 200 and "Thanks" in r.text
    [lead] = lead_rows(conn)
    assert lead["state"] == "NEW" and lead["email"] == "buyer@example.com" and lead["agent_id"] == "demo-agent"
    assert count(conn, db.consent_events, db.consent_events.c.lead_id == lead["id"],
                 db.consent_events.c.channel == "email", db.consent_events.c.kind == "grant") == 1
    assert count(conn, db.jobs, db.jobs.c.job_key == f"L{lead['id']}:instant:email",
                 db.jobs.c.kind == "send_instant_reply") == 1
    assert count(conn, db.audit_log, db.audit_log.c.action == "lead_created",
                 db.audit_log.c.lead_id == lead["id"]) == 1
    event = conn.execute(select(db.inbound_events)).mappings().one()
    assert event["outcome"] == "created" and event["lead_id"] == lead["id"] and event["processed_at"]


def test_text_consent_recorded_only_when_ticked(client, conn):
    submit(client, email="a@example.com", phone="(919) 555-0142", text_consent="yes")
    submit(client, email="b@example.com", phone="(919) 555-0143")
    a, b = sorted(lead_rows(conn), key=lambda r: r["email"])
    assert a["phone_e164"] == "+19195550142"
    texts = conn.execute(select(db.consent_events.c.lead_id, db.consent_events.c.wording_version)
                         .where(db.consent_events.c.channel == "text")).all()
    assert texts == [(a["id"], "form-text-consent-v1")]


def test_sm_02_same_email_within_30_days_attaches(client, conn):
    submit(client, email="buyer@example.com")
    r = submit(client, email="BUYER@example.com", name="Same Person")
    assert r.status_code == 200
    assert count(conn, db.leads) == 1
    assert count(conn, db.jobs, db.jobs.c.kind == "send_instant_reply") == 1
    assert count(conn, db.audit_log, db.audit_log.c.action == "inquiry_attached") == 1


def test_double_submit_same_page_is_dropped(client, conn):
    sid = str(uuid.uuid4())
    submit(client, submission_id=sid, email="buyer@example.com")
    submit(client, submission_id=sid, email="buyer@example.com")
    assert count(conn, db.leads) == 1 and count(conn, db.inbound_events) == 1


def test_sm_18_no_usable_contact(client, conn):
    r = submit(client, email="not-an-email", phone="123")
    assert "add an email" in r.text
    [lead] = lead_rows(conn)
    assert lead["state"] == "CLOSED"
    assert count(conn, db.jobs, db.jobs.c.job_key == f"L{lead['id']}:alert:M-38") == 1
    assert count(conn, db.jobs, db.jobs.c.kind == "send_instant_reply") == 0


def test_phone_only_closed_then_reopened_when_email_added(client, conn):
    submit(client, phone="919-555-0144")          # texting is off for the demo agent (FR-6)
    [lead] = lead_rows(conn)
    assert lead["state"] == "CLOSED"
    submit(client, phone="919-555-0144", email="later@example.com")
    [lead] = lead_rows(conn)
    assert lead["state"] == "NEW" and lead["email"] == "later@example.com"
    assert count(conn, db.jobs, db.jobs.c.job_key == f"L{lead['id']}:instant:email") == 1


def test_fr_3_non_buyer_source_ignored(client, conn):
    r = client.post("/f/demo-agent/seller_form", data={"submission_id": str(uuid.uuid4()), "email": "s@example.com"})
    assert r.status_code == 404
    assert count(conn, db.leads) == 0
    assert conn.execute(select(db.inbound_events.c.outcome)).scalar() == "ignored_source"


def test_unknown_agent_404(client):
    assert client.get("/f/nobody/website_form").status_code == 404
    assert client.get("/f/..%2F..%2Fsecrets/website_form").status_code == 404


def test_cmp_19_only_the_form_creates_leads(client):
    lead_routes = [r.path for r in app.routes if getattr(r, "methods", None) and "POST" in r.methods]
    assert lead_routes == ["/f/{agent_id}/{source_id}"]
    assert client.post("/leads", json={"email": "x@example.com"}).status_code == 404
    assert client.post("/import", json=[]).status_code == 404
