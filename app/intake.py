"""Lead intake from the agent's web form (C-2, CP1-T5).

FR-1 to FR-4, FR-6, CR-5, CR-7. Leads are only ever created here, from a real submission.
"""
from __future__ import annotations

import re
import secrets
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

import phonenumbers
from sqlalchemy import or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection

from app import db
from app.agent_config import AgentConfig
from app.audit import audit

DUPLICATE_WINDOW = timedelta(days=30)  # FR-4

# [Lawyer] L-2: text-consent wording shown on the agent's own form. Version it whenever it changes.
CONSENT_WORDING_VERSION = "form-text-consent-v1"
CONSENT_WORDING = ("I agree to receive text messages from {agent_name} at {firm_name} about my home search. "
                   "Message and data rates may apply. Reply STOP to opt out at any time. "
                   "Consent is not required to get help.")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


@dataclass
class FormSubmission:
    submission_id: str          # hidden field, one per page load: blocks double submits (IP-2)
    name: str = ""
    email: str = ""
    phone: str = ""
    zip: str = ""
    text_consent: bool = False
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    page_url: Optional[str] = None


@dataclass
class IntakeResult:
    outcome: str                # created | attached | duplicate_submit | ignored_source | no_contact
    lead_id: Optional[int] = None


def clean_email(v: str) -> Optional[str]:
    v = (v or "").strip().lower()
    return v if EMAIL_RE.match(v) else None


def clean_us_phone(v: str) -> Optional[str]:
    """E.164 for a valid US number, else None. Whether it is a mobile is checked later (CP2)."""
    if not (v or "").strip():
        return None
    try:
        n = phonenumbers.parse(v, "US")
    except phonenumbers.NumberParseException:
        return None
    if n.country_code != 1 or not phonenumbers.is_valid_number(n):
        return None
    return phonenumbers.format_number(n, phonenumbers.PhoneNumberFormat.E164)


def ensure_agent(conn: Connection, cfg: AgentConfig) -> None:
    conn.execute(insert(db.agents).values(id=cfg.agent_id, timezone=cfg.timezone, status=cfg.status)
                 .on_conflict_do_update(index_elements=["id"],
                                        set_={"timezone": cfg.timezone, "status": cfg.status}))


def intake_form(conn: Connection, cfg: AgentConfig, source_id: str, sub: FormSubmission) -> IntakeResult:
    source = next((s for s in cfg.lead_sources if s.id == source_id), None)
    ensure_agent(conn, cfg)

    # Save the raw submission once (IP-1, IP-2). A double submit of the same page is dropped.
    payload = {"source_id": source_id, "name": sub.name, "email": sub.email, "phone": sub.phone,
               "zip": sub.zip, "text_consent": sub.text_consent, "page_url": sub.page_url}
    event_id = conn.execute(insert(db.inbound_events).values(
        event_key=f"form:{cfg.agent_id}:{sub.submission_id}", source="web_form", payload=payload)
        .on_conflict_do_nothing().returning(db.inbound_events.c.id)).scalar()
    if event_id is None:
        audit(conn, "duplicate_event", agent_id=cfg.agent_id, submission_id=sub.submission_id)
        return IntakeResult("duplicate_submit")

    def finish(outcome, lead_id=None):
        conn.execute(db.inbound_events.update().where(db.inbound_events.c.id == event_id)
                     .values(processed_at=db.now(), lead_id=lead_id, outcome=outcome))
        return IntakeResult(outcome, lead_id)

    if source is None or not source.buyer_source:  # FR-3
        audit(conn, "lead_ignored", agent_id=cfg.agent_id, trigger_event_id=event_id,
              reason="not a buyer source", source_id=source_id)
        return finish("ignored_source")

    email = clean_email(sub.email)
    phone = clean_us_phone(sub.phone)

    # FR-4: same email or phone for this agent within 30 days attaches to the existing lead.
    if email or phone:
        match = [db.leads.c.email == email] if email else []
        match += [db.leads.c.phone_e164 == phone] if phone else []
        row = conn.execute(select(db.leads.c.id, db.leads.c.state, db.leads.c.email).where(
            db.leads.c.agent_id == cfg.agent_id, or_(*match),
            db.leads.c.created_at >= db.now() - DUPLICATE_WINDOW).order_by(db.leads.c.id).limit(1)).first()
        existing = row.id if row else None
        if row and row.state == "CLOSED" and not row.email and email:
            # Closed only because we had no way to reach them; now we do (T-20: buyer action reopens).
            conn.execute(db.leads.update().where(db.leads.c.id == existing)
                         .values(email=email, state="NEW", last_activity_at=db.now()))
            audit(conn, "state_changed", agent_id=cfg.agent_id, lead_id=existing, trigger_event_id=event_id,
                  state_before="CLOSED", state_after="NEW", reason="buyer added an email")
            conn.execute(db.consent_events.insert().values(
                lead_id=existing, kind="grant", channel="email", basis=source.consent_basis,
                source_detail=sub.page_url, ip=sub.ip, user_agent=sub.user_agent, evidence_ref=event_id))
            schedule(conn, f"L{existing}:instant:email", "send_instant_reply", cfg.agent_id, existing,
                     {"channel": "email", "template": "M-01"})
            return finish("reopened", existing)
        if existing:
            conn.execute(db.leads.update().where(db.leads.c.id == existing).values(last_activity_at=db.now()))
            audit(conn, "inquiry_attached", agent_id=cfg.agent_id, lead_id=existing, trigger_event_id=event_id)
            return finish("attached", existing)

    lead_id = conn.execute(db.leads.insert().values(
        agent_id=cfg.agent_id, token=secrets.token_urlsafe(12), name=sub.name.strip() or None,
        email=email, phone_e164=phone, zip=(sub.zip or "").strip()[:10] or None, source_id=source_id,
    ).returning(db.leads.c.id)).scalar()
    audit(conn, "lead_created", agent_id=cfg.agent_id, lead_id=lead_id, trigger_event_id=event_id,
          state_after="NEW", source_id=source_id, has_email=bool(email), has_phone=bool(phone))

    # Consent log (CR-7, CL-1 to CL-8). Email: they wrote in. Text: only if the box was ticked
    # on the agent's own form. Whether texts may actually go out is decided later (FR-30).
    consent_common = dict(lead_id=lead_id, kind="grant", source_detail=sub.page_url, ip=sub.ip,
                          user_agent=sub.user_agent, evidence_ref=event_id)
    if email:
        conn.execute(db.consent_events.insert().values(channel="email", basis=source.consent_basis,
                                                       **consent_common))
    if phone and sub.text_consent and source.consent_basis == "own_form":
        conn.execute(db.consent_events.insert().values(channel="text", basis="own_form",
                                                       wording_version=CONSENT_WORDING_VERSION,
                                                       **consent_common))

    if not email and not (phone and cfg.sms.enabled):  # FR-6: nothing we can send to
        conn.execute(db.leads.update().where(db.leads.c.id == lead_id).values(state="CLOSED"))
        audit(conn, "state_changed", agent_id=cfg.agent_id, lead_id=lead_id, trigger_event_id=event_id,
              state_before="NEW", state_after="CLOSED", reason="no usable contact")
        schedule(conn, f"L{lead_id}:alert:M-38", "agent_alert", cfg.agent_id, lead_id, {"template": "M-38"})
        return finish("no_contact", lead_id)

    if email:  # FR-7: the worker sends M-01 (CP1-T7)
        schedule(conn, f"L{lead_id}:instant:email", "send_instant_reply", cfg.agent_id, lead_id,
                 {"channel": "email", "template": "M-01"})
    return finish("created", lead_id)


def schedule(conn, job_key, kind, agent_id, lead_id, args, run_at=None):
    conn.execute(insert(db.jobs).values(job_key=job_key, kind=kind, agent_id=agent_id, lead_id=lead_id,
                                        run_at=run_at or db.now(), args=args).on_conflict_do_nothing())
