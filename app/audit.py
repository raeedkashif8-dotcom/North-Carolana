"""Audit log writer (C-14, AU-1, FR-56). Every action goes through here."""
from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.engine import Connection

from app import db


def audit(conn: Connection, action: str, *, actor_type: str = "system", actor_id: Optional[str] = None,
          agent_id: Optional[str] = None, lead_id: Optional[int] = None,
          trigger_event_id: Optional[int] = None, state_before: Optional[str] = None,
          state_after: Optional[str] = None, **details: Any) -> None:
    conn.execute(db.audit_log.insert().values(
        action=action, actor_type=actor_type, actor_id=actor_id, agent_id=agent_id, lead_id=lead_id,
        trigger_event_id=trigger_event_id, state_before=state_before, state_after=state_after,
        details=details or None))
