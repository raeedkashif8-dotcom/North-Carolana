"""Per-agent config loader and validator (C-15, ARCHITECTURE section 15, FR-50).

Hard limits live here in code; no config file can override them.
"""
from __future__ import annotations

from datetime import time
from pathlib import Path
from typing import Literal, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

# Hard limits (D-11, RR-2 to RR-5). Not configurable.
WINDOW_EARLIEST = time(8, 0)
WINDOW_LATEST = time(21, 0)
MIN_REMINDER_GAP_HOURS = 20
MAX_REMINDER_OFFSET_HOURS = 14 * 24
MAX_REMINDERS = 5


class ConfigError(Exception):
    """Config is invalid. That agent's sending stays blocked (FR-50)."""

    def __init__(self, agent_id: str, problems: list[str]):
        self.agent_id = agent_id
        self.problems = problems
        super().__init__(f"{agent_id}: " + "; ".join(problems))


def _parse_hhmm(v):
    if isinstance(v, time):
        return v
    hh, mm = str(v).split(":")
    return time(int(hh), int(mm))


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")  # a typo in a key is an error, not ignored


class Window(Strict):
    start: time
    end: time

    _parse = field_validator("start", "end", mode="before")(classmethod(lambda cls, v: _parse_hhmm(v)))

    @model_validator(mode="after")
    def check(self):
        if self.start < WINDOW_EARLIEST or self.end > WINDOW_LATEST:
            raise ValueError("window must stay inside 08:00 to 21:00 (hard limit, D-11)")
        if self.start >= self.end:
            raise ValueError("window start must be before end")
        return self


class AlertHours(Strict):
    start: time
    end: time
    urgent_override_hours: int = 12

    _parse = field_validator("start", "end", mode="before")(classmethod(lambda cls, v: _parse_hhmm(v)))


class Contacts(Strict):
    alert_phone: Optional[str] = None
    alert_email: str
    backup: Optional[dict] = None


class EmailCfg(Strict):
    sender: Literal["demo-mailbox", "gmail_api"]
    reply_to: str


class SmsCfg(Strict):
    enabled: bool = False
    twilio_subaccount: Optional[str] = None


class LeadSource(Strict):
    id: str
    type: Literal["web_form", "email_parser"]
    parser: Optional[str] = None
    buyer_source: bool
    consent_basis: Literal["own_form", "inbound_text", "booking_checkbox", "portal_inquiry",
                           "lawyer_approved_portal"]
    tour_request_marker: Optional[str] = None


class Booking(Strict):
    provider: Literal["calcom", "calendly"]
    url: str


class Agreement(Strict):
    esign: Literal["docusign", "dotloop", "skyslope", "other"]
    mode: Literal["draft_then_agent_sends", "agent_sends"]
    docusign_template_id: Optional[str] = None
    send_trigger: Literal["on_booking", "after_consult"] = "on_booking"
    default_term_days: int = Field(gt=0, le=365)

    @model_validator(mode="after")
    def check(self):
        if self.mode == "draft_then_agent_sends" and self.esign != "docusign":
            raise ValueError("draft_then_agent_sends only works with DocuSign (D-03, D-04)")
        return self


class Reminders(Strict):
    offsets_hours: list[int]
    max: int
    window: Window
    excluded_days: list[Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"]] = []

    @model_validator(mode="after")
    def check(self):
        offs = self.offsets_hours
        if not 1 <= self.max <= MAX_REMINDERS:
            raise ValueError(f"max must be 1 to {MAX_REMINDERS} (hard cap, RR-3)")
        if len(offs) < self.max:
            raise ValueError("need at least as many offsets as max")
        if any(o < MIN_REMINDER_GAP_HOURS or o > MAX_REMINDER_OFFSET_HOURS for o in offs):
            raise ValueError("offset under 20 hours or over 14 days (RR-2)")
        if offs != sorted(offs) or any(b - a < MIN_REMINDER_GAP_HOURS for a, b in zip(offs, offs[1:])):
            raise ValueError("offsets under 20 hours apart, or out of order (RR-4)")
        return self


class Tours(Strict):
    calendar_ics: Optional[str] = None  # a secret reference, never the link itself
    extra_words: list[str] = []


class AgentConfig(Strict):
    agent_id: str
    display_name: str
    firm_name: str
    firm_address: str
    timezone: str
    status: Literal["test", "live", "paused"]
    contacts: Contacts
    alert_hours: AlertHours
    email: EmailCfg
    sms: SmsCfg = SmsCfg()
    lead_sources: list[LeadSource] = Field(min_length=1)
    booking: Booking
    agreement: Agreement
    reminders: Reminders
    booking_nudges_hours: list[int] = [24]
    acknowledge_other_replies: bool = True
    tours: Tours = Tours()
    form_checklist: dict = {}

    @field_validator("timezone")
    @classmethod
    def tz_exists(cls, v):
        try:
            ZoneInfo(v)
        except ZoneInfoNotFoundError:
            raise ValueError(f"unknown time zone {v!r}")
        return v

    @field_validator("booking_nudges_hours")
    @classmethod
    def nudges(cls, v):
        if len(v) > 2:
            raise ValueError("at most 2 booking nudges (D-24)")
        return v


def load_agent_config(path: str | Path) -> AgentConfig:
    path = Path(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    agent_id = raw.get("agent_id", path.stem)
    try:
        return AgentConfig.model_validate(raw)
    except ValidationError as e:
        problems = [f"{'.'.join(str(x) for x in err['loc']) or '(top)'}: {err['msg']}" for err in e.errors()]
        raise ConfigError(agent_id, problems) from None
