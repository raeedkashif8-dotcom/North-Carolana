"""Database tables for CP1 (ARCHITECTURE section 5) and engine helpers.

Tables are declared in schema "app". At runtime the schema name comes from settings
(D-33, D-34), so tests can map "app" to "app_test" without touching real data.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (BigInteger, Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer,
                        MetaData, String, Table, Text, UniqueConstraint, create_engine, event, text)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Engine

SCHEMA = "app"
metadata = MetaData(schema=SCHEMA)


def now() -> datetime:
    return datetime.now(timezone.utc)


def ts(name, **kw):
    return Column(name, DateTime(timezone=True), **kw)  # always UTC (section 5)


agents = Table(
    "agents", metadata,
    Column("id", String(64), primary_key=True),
    Column("status", String(16), nullable=False, server_default="test"),
    Column("config_version", Integer),
    Column("timezone", String(64), nullable=False),
    ts("created_at", nullable=False, server_default=text("now()")),
    CheckConstraint("status in ('test','live','paused')", name="agents_status"),
)

agent_config_versions = Table(
    "agent_config_versions", metadata,
    Column("agent_id", String(64), ForeignKey("agents.id"), primary_key=True),
    Column("version", Integer, primary_key=True),
    Column("body", Text, nullable=False),
    Column("valid", Boolean, nullable=False),
    Column("problems", JSONB),
    ts("created_at", nullable=False, server_default=text("now()")),
)

leads = Table(
    "leads", metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("agent_id", String(64), ForeignKey("agents.id"), nullable=False),
    Column("token", String(32), nullable=False, unique=True),
    Column("name", Text),
    Column("email", Text),
    Column("phone_e164", String(20)),
    Column("zip", String(10)),
    Column("tz", String(64)),
    Column("source_id", String(64), nullable=False),
    Column("state", String(20), nullable=False, server_default="NEW"),
    ts("opted_out_at"),
    Column("reminders_paused", Boolean, nullable=False, server_default=text("false")),
    ts("created_at", nullable=False, server_default=text("now()")),
    ts("last_activity_at", nullable=False, server_default=text("now()")),
    CheckConstraint("state in ('NEW','CONTACTED','CONSULT_BOOKED','AWAITING_SEND','SENT','BUYER_SIGNED',"
                    "'SIGNED','EXPIRED','DECLINED','CLOSED')", name="leads_state"),
)

consent_events = Table(  # consent log, append-only (CL-1 to CL-9)
    "consent_events", metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("lead_id", BigInteger, ForeignKey("leads.id"), nullable=False),
    Column("channel", String(8), nullable=False),
    Column("kind", String(8), nullable=False),            # grant | revoke
    Column("basis", String(32)),
    Column("method", String(32)),                         # for revokes: keyword, ai_label, unsubscribe_link...
    ts("captured_at", nullable=False, server_default=text("now()")),
    Column("wording_version", String(32)),
    Column("source_detail", Text),
    Column("ip", String(64)),
    Column("user_agent", Text),
    Column("evidence_ref", BigInteger),                   # inbound_events.id
    CheckConstraint("channel in ('email','text')", name="consent_channel"),
    CheckConstraint("kind in ('grant','revoke')", name="consent_kind"),
)

inbound_events = Table(
    "inbound_events", metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("event_key", String(200), nullable=False, unique=True),  # IP-2: duplicates can't be saved twice
    Column("source", String(32), nullable=False),
    ts("received_at", nullable=False, server_default=text("now()")),
    Column("payload", JSONB, nullable=False),             # raw body, kept 30 days (DS-10)
    ts("processed_at"),
    Column("lead_id", BigInteger, ForeignKey("leads.id")),
    Column("outcome", Text),
)

outbound_messages = Table(
    "outbound_messages", metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("dedupe_key", String(200), nullable=False, unique=True),  # IP-4
    Column("lead_id", BigInteger, ForeignKey("leads.id")),
    Column("agent_id", String(64), ForeignKey("agents.id"), nullable=False),
    Column("template_id", String(16), nullable=False),
    Column("template_version", Integer, nullable=False),
    Column("channel", String(8), nullable=False),
    Column("to_address", Text, nullable=False),
    Column("status", String(12), nullable=False, server_default="queued"),
    Column("provider_id", Text),
    Column("subject", Text),
    Column("body_masked", Text),
    Column("error", Text),
    ts("created_at", nullable=False, server_default=text("now()")),
    ts("sent_at"),
    CheckConstraint("status in ('queued','sent','failed','unknown','skipped')", name="outbound_status"),
)

jobs = Table(
    "jobs", metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("job_key", String(200), nullable=False, unique=True),     # IP-6
    Column("kind", String(32), nullable=False),
    Column("lead_id", BigInteger, ForeignKey("leads.id")),
    Column("agent_id", String(64), ForeignKey("agents.id")),
    ts("run_at", nullable=False),
    Column("status", String(12), nullable=False, server_default="pending"),
    Column("attempts", Integer, nullable=False, server_default=text("0")),
    ts("locked_until"),
    Column("args", JSONB),
    Column("result", Text),
    ts("created_at", nullable=False, server_default=text("now()")),
    CheckConstraint("status in ('pending','running','done','skipped','failed','cancelled')", name="jobs_status"),
)

template_versions = Table(
    "template_versions", metadata,
    Column("template_id", String(16), primary_key=True),
    Column("version", Integer, primary_key=True),
    Column("channel", String(8), nullable=False),
    Column("subject", Text),
    Column("body", Text, nullable=False),
    Column("sha256", String(64), nullable=False),
    ts("created_at", nullable=False, server_default=text("now()")),
)

template_approvals = Table(
    "template_approvals", metadata,
    Column("agent_id", String(64), ForeignKey("agents.id"), primary_key=True),
    Column("template_id", String(16), primary_key=True),
    Column("version", Integer, primary_key=True),
    Column("sha256", String(64), nullable=False),
    ts("approved_at", nullable=False),
    Column("method", String(16), nullable=False),        # esign | email_reply
    Column("approver", Text, nullable=False),
)

audit_log = Table(  # append-only (AU-3, CR-15)
    "audit_log", metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    ts("at", nullable=False, server_default=text("now()")),
    Column("agent_id", String(64)),
    Column("lead_id", BigInteger),
    Column("actor_type", String(12), nullable=False),     # system, agent, buyer, operator, provider
    Column("actor_id", Text),
    Column("action", String(64), nullable=False),
    Column("details", JSONB),
    Column("trigger_event_id", BigInteger),
    Column("state_before", String(20)),
    Column("state_after", String(20)),
)


def _append_only_sql(schema: str) -> str:
    # Rejects UPDATE and DELETE. Only the retention job may delete, by setting
    # app.allow_audit_purge='on' inside its own transaction (AU-3).
    return f"""
    create or replace function {schema}.forbid_change() returns trigger language plpgsql as $$
    begin
      if tg_op = 'DELETE' and current_setting('app.allow_audit_purge', true) = 'on' then
        return old;
      end if;
      raise exception '% on %.% is not allowed (append-only)', tg_op, tg_table_schema, tg_table_name;
    end $$;
    drop trigger if exists append_only on {schema}.audit_log;
    create trigger append_only before update or delete on {schema}.audit_log
      for each row execute function {schema}.forbid_change();
    drop trigger if exists append_only on {schema}.consent_events;
    create trigger append_only before update or delete on {schema}.consent_events
      for each row execute function {schema}.forbid_change();
    """


def make_engine(url: str, schema: str = SCHEMA) -> Engine:
    """Engine whose "app" tables land in `schema` (for example "app_test")."""
    return create_engine(url, pool_pre_ping=True,
                         execution_options={"schema_translate_map": {SCHEMA: schema}})


def schema_of(engine: Engine) -> str:
    return engine.get_execution_options().get("schema_translate_map", {}).get(SCHEMA, SCHEMA)


def create_all(engine: Engine) -> None:
    schema = schema_of(engine)
    with engine.begin() as conn:
        conn.execute(text(f'create schema if not exists "{schema}"'))
        metadata.create_all(conn)
        conn.execute(text(_append_only_sql(schema)))


def drop_schema(engine: Engine) -> None:
    schema = schema_of(engine)
    if schema == SCHEMA:
        raise RuntimeError("refusing to drop the working schema; only test schemas can be dropped")
    with engine.begin() as conn:
        conn.execute(text(f'drop schema if exists "{schema}" cascade'))
