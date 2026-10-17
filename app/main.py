"""Web app entry point (C-1). Run: .venv\\Scripts\\uvicorn app.main:app --reload"""
from __future__ import annotations

import html
import uuid
from functools import lru_cache
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import text

from app import db
from app.agent_config import AgentConfig, ConfigError, load_agent_config
from app.intake import CONSENT_WORDING, FormSubmission, intake_form
from app.settings import get_settings

app = FastAPI(title="AutoM8X Buyer Agreement Agent")


@lru_cache
def engine():
    s = get_settings()
    if not s.database_url:
        raise RuntimeError("DATABASE_URL is not set")
    return db.make_engine(s.database_url, schema=s.db_schema)


def get_conn():
    """One transaction per request: everything a request writes commits together or not at all."""
    with engine().begin() as conn:
        yield conn


def agent_config(agent_id: str) -> AgentConfig:
    path = Path(get_settings().agents_dir) / f"{agent_id}.yaml"
    if not path.is_file() or not agent_id.replace("-", "").isalnum():
        raise HTTPException(404, "unknown agent")
    try:
        return load_agent_config(path)
    except ConfigError:
        raise HTTPException(503, "this agent is not available right now")  # FR-50: blocked, not crashed


@app.get("/healthz")
def healthz():
    """Health check for the uptime monitor (ENV-6)."""
    s = get_settings()
    dbstate = "not configured"
    if s.database_url:
        try:
            with engine().connect() as conn:
                conn.execute(text("select 1"))
            dbstate = "ok"
        except Exception as e:  # report, don't crash the health check
            dbstate = f"error: {type(e).__name__}"
    return {"status": "ok" if dbstate in ("ok", "not configured") else "degraded", "database": dbstate,
            "environment": s.environment}


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title>
<style>body{{font-family:system-ui,sans-serif;max-width:32rem;margin:2rem auto;padding:0 1rem;color:#1a1a1a}}
label{{display:block;margin:.8rem 0 .2rem}}input[type=text],input[type=email],input[type=tel]{{width:100%;padding:.5rem;font-size:1rem}}
.consent{{display:flex;gap:.5rem;font-size:.85rem;margin-top:1rem}}button{{margin-top:1rem;padding:.6rem 1.2rem;font-size:1rem}}
.demo{{background:#fff3cd;padding:.5rem;font-size:.85rem}}</style></head><body>{body}</body></html>"""


@app.get("/f/{agent_id}/{source_id}", response_class=HTMLResponse)
def form_page(agent_id: str, source_id: str):
    cfg = agent_config(agent_id)
    e = html.escape
    consent = e(CONSENT_WORDING.format(agent_name=cfg.display_name, firm_name=cfg.firm_name))
    demo = '<p class="demo">Demo agent. Not a real person or firm.</p>' if cfg.status == "test" else ""
    body = f"""{demo}<h1>Start your home search with {e(cfg.display_name)}</h1>
<form method="post">
<input type="hidden" name="submission_id" value="{uuid.uuid4()}">
<label for="name">Name</label><input type="text" id="name" name="name" autocomplete="name">
<label for="email">Email</label><input type="email" id="email" name="email" autocomplete="email">
<label for="phone">Mobile phone (optional)</label><input type="tel" id="phone" name="phone" autocomplete="tel">
<label for="zip">Zip code (optional)</label><input type="text" id="zip" name="zip" autocomplete="postal-code">
<div class="consent"><input type="checkbox" id="text_consent" name="text_consent" value="yes">
<label for="text_consent">{consent}</label></div>
<button type="submit">Send</button></form>
<p style="font-size:.8rem">{e(cfg.firm_name)}, {e(cfg.firm_address)}</p>"""
    return PAGE.format(title=e(cfg.display_name), body=body)


@app.post("/f/{agent_id}/{source_id}", response_class=HTMLResponse)
def form_submit(agent_id: str, source_id: str, request: Request, submission_id: str = Form(...),
                name: str = Form(""), email: str = Form(""), phone: str = Form(""), zip: str = Form(""),
                text_consent: str = Form(""), conn=Depends(get_conn)):
    cfg = agent_config(agent_id)
    sub = FormSubmission(submission_id=submission_id[:64], name=name[:200], email=email[:254], phone=phone[:32],
                         zip=zip[:10], text_consent=text_consent == "yes",
                         ip=request.client.host if request.client else None,
                         user_agent=request.headers.get("user-agent", "")[:300], page_url=str(request.url))
    result = intake_form(conn, cfg, source_id, sub)
    if result.outcome in ("ignored_source",):
        raise HTTPException(404, "unknown form")
    # Same answer for new, attached and duplicate submits: don't reveal whether someone is already a lead.
    msg = (f"Thanks! {html.escape(cfg.display_name)} will be in touch shortly. Check your email for next steps."
           if result.outcome != "no_contact" else
           f"Thanks! Please add an email address so {html.escape(cfg.display_name)} can reach you.")
    return PAGE.format(title="Thanks", body=f"<h1>Thanks</h1><p>{msg}</p>")
