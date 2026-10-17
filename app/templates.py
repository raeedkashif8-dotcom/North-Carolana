"""Template rendering (C-6). Approved versions only, fixed fill-ins, fails closed.

Fill-ins look like {buyer_first_name}. Anything not on ALLOWED_FIELDS is an error.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

import yaml

ALLOWED_FIELDS = {
    "buyer_first_name", "agent_name", "firm_name", "firm_address",
    "booking_link", "unsubscribe_link", "explainer",
}
FIELD_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")
MAX_TEXT_SEGMENTS = 3  # TP-U-TPL-05


class RenderError(Exception):
    """Rendering failed. The message must not be sent (fail closed)."""


class NotApproved(Exception):
    """This exact template version has no approval for this agent (CR-10)."""


@dataclass(frozen=True)
class Template:
    template_id: str          # for example "M-01"
    version: int
    channel: str              # email | text | block
    body: str
    subject: Optional[str] = None
    fallbacks: dict = field(default_factory=dict)

    @property
    def sha256(self) -> str:
        return sha256(self.body)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_template(path: str | Path) -> Template:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return Template(
        template_id=raw["id"], version=int(raw["version"]), channel=raw["channel"],
        body=raw["body"], subject=raw.get("subject"), fallbacks=raw.get("fallbacks") or {},
    )


def fields_in(text: str) -> set[str]:
    return set(FIELD_RE.findall(text))


def check_fields(t: Template) -> None:
    unknown = (fields_in(t.body) | fields_in(t.subject or "")) - ALLOWED_FIELDS
    if unknown:
        raise RenderError(f"{t.template_id} v{t.version}: unknown fill-ins {sorted(unknown)}")


def require_approved(t: Template, approvals: Iterable[tuple[str, int, str]]) -> None:
    """approvals: (template_id, version, sha256) tuples approved for this agent."""
    if (t.template_id, t.version, t.sha256) not in set(approvals):
        raise NotApproved(f"{t.template_id} v{t.version} is not approved for this agent")


def _fill(text: str, values: dict, fallbacks: dict, where: str) -> str:
    def sub(m):
        name = m.group(1)
        if name not in ALLOWED_FIELDS:
            raise RenderError(f"{where}: unknown fill-in {{{name}}}")
        v = values.get(name)
        if v is None or v == "":
            if name in fallbacks:
                return str(fallbacks[name])
            raise RenderError(f"{where}: missing value for {{{name}}} and no fallback")
        return str(v)
    return FIELD_RE.sub(sub, text)


@dataclass(frozen=True)
class Rendered:
    subject: Optional[str]
    body: str


def render(t: Template, values: dict, approvals, explainer: Optional[Template] = None) -> Rendered:
    """Render an approved template. The explainer, if used, must itself be approved
    and is inserted byte for byte (CR-3, FR-9)."""
    check_fields(t)
    require_approved(t, approvals)
    values = dict(values)
    if "explainer" in fields_in(t.body):
        if explainer is None:
            raise RenderError(f"{t.template_id}: needs an explainer block")
        require_approved(explainer, approvals)
        if fields_in(explainer.body):
            raise RenderError("explainer must be fixed text with no fill-ins")
        values["explainer"] = explainer.body
    where = f"{t.template_id} v{t.version}"
    body = _fill(t.body, values, t.fallbacks, where)
    subject = _fill(t.subject, values, t.fallbacks, where) if t.subject else None
    return Rendered(subject=subject, body=body)


# ---- text length (segments) ----
_GSM7 = set("@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "ÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà")
_GSM7_EXT = set("^{}\\[~]|€")  # these count as two characters


def text_segments(text: str) -> int:
    if all(c in _GSM7 or c in _GSM7_EXT for c in text):
        n = sum(2 if c in _GSM7_EXT else 1 for c in text)
        return 1 if n <= 160 else -(-n // 153)
    n = len(text.encode("utf-16-le")) // 2
    return 1 if n <= 70 else -(-n // 67)


def check_text_length(t: Template, sample_values: dict) -> int:
    """Called at approval time for text templates, using longest realistic values."""
    body = _fill(t.body, sample_values, t.fallbacks, t.template_id)
    segs = text_segments(body)
    if segs > MAX_TEXT_SEGMENTS:
        raise RenderError(f"{t.template_id}: {segs} segments, over the {MAX_TEXT_SEGMENTS} limit "
                          f"({len(body)} characters)")
    return segs
