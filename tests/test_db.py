"""CP1-T2 tables. TP-CMP-18 (append-only), TP-U-IDEM-01 and 03 (unique keys), outbound dedupe (IP-4)."""
from datetime import datetime, timezone

from sqlalchemy import func, select, text
from sqlalchemy.dialects.postgresql import insert

from app import db
from tests.conftest import TEST_SCHEMA, savepoint_error

S = TEST_SCHEMA


def test_tables_exist_in_test_schema_not_public(conn):
    names = set(conn.execute(text(
        "select table_name from information_schema.tables where table_schema = :s"), {"s": S}).scalars())
    expected = {"agents", "agent_config_versions", "leads", "consent_events", "inbound_events",
                "outbound_messages", "jobs", "template_versions", "template_approvals", "audit_log"}
    assert expected <= names
    in_public = set(conn.execute(text(
        "select table_name from information_schema.tables where table_schema = 'public'")).scalars())
    assert not (expected & in_public), "our tables must never be in Supabase's API-exposed public schema"


def test_cmp_18_audit_log_is_append_only(conn):
    row_id = conn.execute(db.audit_log.insert().values(actor_type="system", action="test")
                          .returning(db.audit_log.c.id)).scalar()
    err = savepoint_error(conn, f"update {S}.audit_log set action = 'changed' where id = {row_id}")
    assert err is not None and "append-only" in str(err)
    err = savepoint_error(conn, f"delete from {S}.audit_log where id = {row_id}")
    assert err is not None and "append-only" in str(err)
    assert conn.execute(select(db.audit_log.c.action).where(db.audit_log.c.id == row_id)).scalar() == "test"


def test_audit_purge_allowed_only_with_retention_flag(conn):
    row_id = conn.execute(db.audit_log.insert().values(actor_type="system", action="old")
                          .returning(db.audit_log.c.id)).scalar()
    conn.execute(text("set local app.allow_audit_purge = 'on'"))
    assert savepoint_error(conn, f"delete from {S}.audit_log where id = {row_id}") is None


def test_consent_log_is_append_only(conn, agent):
    lead_id = conn.execute(db.leads.insert().values(agent_id=agent, token="t1", source_id="website_form")
                           .returning(db.leads.c.id)).scalar()
    cid = conn.execute(db.consent_events.insert().values(lead_id=lead_id, channel="email", kind="grant",
                                                         basis="own_form").returning(db.consent_events.c.id)).scalar()
    err = savepoint_error(conn, f"update {S}.consent_events set basis = 'none' where id = {cid}")
    assert err is not None and "append-only" in str(err)


def test_idem_01_same_event_key_saved_once(conn):
    stmt = insert(db.inbound_events).values(event_key="twilio:SM123", source="twilio",
                                            payload={"Body": "STOP"}).on_conflict_do_nothing()
    first = conn.execute(stmt.returning(db.inbound_events.c.id)).fetchall()
    second = conn.execute(stmt.returning(db.inbound_events.c.id)).fetchall()
    assert len(first) == 1 and len(second) == 0
    n = conn.execute(select(func.count()).select_from(db.inbound_events)
                     .where(db.inbound_events.c.event_key == "twilio:SM123")).scalar()
    assert n == 1


def test_idem_03_job_key_scheduled_once(conn, agent):
    run_at = datetime(2026, 10, 21, 14, 0, tzinfo=timezone.utc)
    stmt = insert(db.jobs).values(job_key="L1:reminder:2", kind="reminder", agent_id=agent,
                                  run_at=run_at).on_conflict_do_nothing()
    conn.execute(stmt)
    conn.execute(stmt)
    assert conn.execute(select(func.count()).select_from(db.jobs)).scalar() == 1


def test_outbound_dedupe_key_blocks_second_row(conn, agent):
    stmt = insert(db.outbound_messages).values(
        dedupe_key="L1:M-01:instant:email", agent_id=agent, template_id="M-01", template_version=1,
        channel="email", to_address="buyer@example.com").on_conflict_do_nothing()
    assert len(conn.execute(stmt.returning(db.outbound_messages.c.id)).fetchall()) == 1
    assert len(conn.execute(stmt.returning(db.outbound_messages.c.id)).fetchall()) == 0


def test_bad_state_rejected(conn, agent):
    err = savepoint_error(conn, db.leads.insert().values(agent_id=agent, token="t2",
                                                         source_id="x", state="MAYBE"))
    assert err is not None and "leads_state" in str(err)


def test_refuses_to_drop_working_schema():
    import pytest
    eng = db.make_engine("postgresql+psycopg://u:p@localhost/x", schema="app")
    with pytest.raises(RuntimeError, match="refusing"):
        db.drop_schema(eng)
