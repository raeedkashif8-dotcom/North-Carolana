# Build Plan: Checkpoints

Version 0.1, 2026-10-16. Status: draft, not approved.

Built on the Stage 0 defaults: Python core (D-01), the agent presses Send (D-02), email first (D-05). [Depends on Q1 to Q6]

Test IDs point to TEST_PLAN.md. Other IDs point to PRD.md, ARCHITECTURE.md and DECISIONS.md.

## Rules for every checkpoint

1. Order goes from the thinnest working path to the full flow: first a lead gets a reply (CP1), last the tour alert (CP8).
2. Every task is half a day or less. Many will take less with me writing the code.
3. "Done" means the listed tests ran and you saw the real output. Anything not run is written as "not run".
4. Every checkpoint has an on/off switch (an environment flag), so a broken part can be turned off without a redeploy.
5. Every checkpoint ends with a git tag (`cp1-done` and so on) and a DECISIONS.md entry if anything changed.
6. Database changes go through migrations that can be undone.

## Overview

| CP | Goal | Half-day tasks | In the demo cut | Risk |
|---|---|---|---|---|
| CP0 | Spikes: test the risky unknowns; start slow approvals | 6 | 5 of 6 | Lowers risk |
| CP1 | A lead creates a record and gets an email reply | 9 | 8 of 9 | Low |
| CP2 | Texts, STOP, quiet hours, unsubscribe, pause | 7 | 4 of 7 | Medium |
| CP3 | Consult booking | 5 | 4 of 5 | Low |
| CP4 | Agreement prompt, sent and signed detection | 7 | 4 of 7 | Medium |
| CP5 | Reminders that stop when signed | 5 | 5 of 5 | Medium |
| CP6 | Reply sorter and legal questions | 5 | 4 of 5 | Medium |
| CP7 | Alerts, escalation, operator page, approvals | 6 | 1 of 6 | Low |
| CP8 | Tour alert. **RISKIEST** | 7 | 5 of 7 | High |
| CP9 | Pilot readiness, end-to-end test, demo video | 6 | 1 of 6 | Medium |
| | **Total** | **63** | **41** | |

**Honest timeline.** 63 half-day tasks is at most about 32 working days for the full pilot build. The demo cut is at most about 21 days. Your plan has about 10 build days. With me writing most of the code, many tasks will take an hour or two, so the demo cut may fit in 10 to 15 days, but I can't promise your pace. We re-estimate after CP1 using the real time it took. [Depends on Q1, Q2]

**Demo cut.** Enough to show a full flow on a call, email only: CP0 (T1, T3a, T3b, T4, T5), CP1 (all but T8), CP2 (T3, T5, T6, T7), CP3 (T1 to T4), CP4 (T1 to T4), CP5 (all), CP6 (T1 to T4), CP7 (T1), CP8 (T1, T3 to T6), CP9 (T4).

---

## CP0. Spikes and slow approvals

**Goal:** Prove or disprove the riskiest unknowns with throwaway scripts, and start the approvals that take weeks.

This spike is placed first because CP8 (tour alert) is the riskiest checkpoint, and CP4 (DocuSign) is second.

**Tasks**
- **CP0-T1. Calendar spike (S-1, for CP8).** Create an event in your own Google Calendar. A 20-line script fetches the private iCal link every minute. Record how many minutes until the new event appears, and until an edit appears. Parse it with the icalendar package.
- **CP0-T2. ShowingTime spike (S-2, for CP8).** Get 2 or 3 redacted ShowingTime emails from your interviews (I2). Write down which fields exist: status, time, address, buyer name. If none arrive by day 10, record "blocked" and keep the risk open.
- **CP0-T3a. DocuSign sandbox setup.** Developer account, integration key, a SAMPLE agreement uploaded as a template with a Buyer role (and an Agent role if you want countersigning).
- **CP0-T3b. DocuSign spike (S-3, for CP4).** A script creates a draft from the template with only the buyer's name and email, gets the sending link, you press Send, and a temporary public URL receives the "sent" and "completed" webhooks.
- **CP0-T4. Start the slow approvals.** Buy the inbound email domain and set up Postmark. Create the Google app with only gmail.send, publish a privacy policy and homepage, submit for Google review. Open the Twilio account and submit AutoM8X's business profile. [Depends on Q5] Contact a lawyer for the section 13 review (PRD OQ-10).
- **CP0-T5. Sorter spike (S-4).** A throwaway script runs the 30 TP-AI-01 replies through `gemini-3.1-flash-lite` and `gemini-3.8-flash` with a draft prompt, using a free-tier key (fake replies only). Record scores and misses for both.

**What you can see:** a file `SPIKES.md` with real outputs: minutes of calendar delay, a table of ShowingTime fields, excerpts of the DocuSign webhook bodies, sorter scores and misses per model.

**Tests that must pass:** none permanent. These scripts are throwaway and live in a `spikes/` folder the app never imports.

**Done when**
- [ ] S-1 to S-4 each have a written result: works, doesn't work, or unknown with the reason.
- [ ] Any design change caused by a spike is logged in DECISIONS.md.
- [ ] Google review, Postmark domain and Twilio business profile are submitted, with dates.
- [ ] A lawyer has been contacted.

**Rollback:** nothing to undo. Delete the sandbox objects and the `spikes/` folder.

---

## CP1. A lead creates a record and gets an email reply

**Goal:** A test lead submitted on the demo form creates a lead record and gets the approved instant reply email within 60 seconds.

**Tasks**
- **CP1-T1.** Project skeleton: FastAPI app, worker entry point, settings, Postgres in Docker, Alembic, pytest, GitHub Actions running tests on every push.
- **CP1-T2.** First tables: agents, agent_config_versions, leads, consent_events, inbound_events, outbound_messages, jobs, template_versions, template_approvals, audit_log with the append-only trigger (AU-3).
- **CP1-T3.** Config loader and validator (ARCHITECTURE section 15), the demo agent config. Invalid config blocks the agent (FR-50).
- **CP1-T4.** Template store and renderer: approved versions only, allowed fill-ins only, fails closed. Starter M-01 and M-03, marked DRAFT until approved.
- **CP1-T5.** Intake: demo web form with consent wording, POST endpoint, lead creation, duplicate rule (FR-4), consent events, audit rows.
- **CP1-T6.** Email adapter interface and the demo mailer through Postmark (D-27). Outbound keys (IP-4).
- **CP1-T7.** Worker loop and jobs (IP-6, IP-7). Instant reply job. Unknown-send sweep (TM-15).
- **CP1-T8.** Gmail send adapter for real agents: Google sign-in for one test Gmail account, encrypted token, send as that account. Not needed for the demo.
- **CP1-T9.** Deploy to the Railway demo environment. Health endpoint. Secrets in Railway variables.

**What you can see:** fill the demo form with your email. Within a minute an email "from Demo Agent" arrives with the explainer and a booking link. The lead and its audit rows are in the database. (The operator page comes in CP7.)

**Tests that must pass:** TP-U-SM-01, TP-U-SM-02, TP-U-SM-18, TP-U-TPL-01 to 05, TP-U-CFG-01, TP-U-IDEM-01 to 03, TP-I-01, TP-CMP-09, TP-CMP-10, TP-CMP-18, TP-CMP-19.

**Done when**
- [ ] On the demo environment, the reply email goes out within 60 seconds of the form submit (time read from the audit log).
- [ ] Submitting the same form twice gives one lead and one email.
- [ ] An unapproved template refuses to send.
- [ ] All listed tests pass in GitHub Actions.
- [ ] The health check is green on Railway.

**Rollback:** redeploy the previous build in Railway. Undo the migration. `OUTBOUND_ENABLED=false` stops all sends while still recording leads.

---

## CP2. Texts, STOP, quiet hours, unsubscribe and pause

**Goal:** Leads with text consent get the reply by text inside their window, and an opt-out from any channel stops everything within a minute.

**Tasks**
- **CP2-T1.** Twilio adapter: send, delivery status webhook, signature check (SMS-3, SMS-4). Per-agent sub-account in config. Test credentials in demo.
- **CP2-T2.** Texting permission FL-3 (FR-30): consent basis, registration flag, lawyer gate flag, valid US mobile check.
- **CP2-T3.** Time zones and windows: zip and area-code lookup, default Eastern, window calculator with hard limits (RR-5), daylight-saving tests.
- **CP2-T4.** Inbound text webhook: save by MessageSid, match the lead by phone, audit.
- **CP2-T5.** Exact opt-out words (RS-2) and the outage rule (RS-9), the opt-out flow (FR-32), suppression list, M-14, M-30, START handling (T-24).
- **CP2-T6.** Email side: unsubscribe page (M-18) with one button; inbound buyer email replies through Postmark (EM-4) with matching; capture of the Gmail forwarding confirmation (S-7).
- **CP2-T7.** Global and per-agent pause (OPS-2, OPS-3). Test-mode allowlist (FR-57). Masking of stored text (RS-4) and attachment handling (SMS-6).

**What you can see:** with Twilio test credentials, a lead with text consent shows a "sent" text record at once. A lead submitted at 21:30 buyer time shows the text waiting for 9:00 and the email already sent. A test script posts a signed fake "STOP": within a minute the lead is opted out, pending jobs are cancelled and the confirmation is logged. Clicking unsubscribe in the demo email does the same. Global pause: a new lead gets no message. With a real US phone, you see the real text. [Depends on Q6]

**Tests that must pass:** TP-U-SM-11, TP-U-TZ-01 to 06, TP-U-KW-01 to 07, TP-U-KW-10, TP-U-MASK-01 to 05, TP-I-02, TP-I-03, TP-I-04, TP-I-13, TP-CMP-05, TP-CMP-06, TP-CMP-07, TP-CMP-12 to 16, TP-F-02, TP-F-07, TP-F-18.

**Done when**
- [ ] STOP by text and unsubscribe by email each stop everything within 60 seconds on the demo environment.
- [ ] No text is ever sent without FL-3 (test proves it).
- [ ] Window and daylight-saving tests pass.
- [ ] Pause takes effect within 60 seconds.

**Rollback:** `SMS_ENABLED=false` (email only). Redeploy the previous build.

---

## CP3. Consult booking

**Goal:** A buyer who books the consult from the link is matched to their lead and moves to Consult booked; the nudge and rebook messages work.

**Tasks**
- **CP3-T1.** Cal.com demo event type. Booking link with name and email prefill and `metadata[lead]` token. Confirm the token reaches the webhook and that the free plan allows webhooks (S-5).
- **CP3-T2.** Booking webhook: signature check; created, rescheduled, cancelled; matching by token, then email, then phone (FR-12); unmatched list.
- **CP3-T3.** Transitions T-4, T-6, T-7. Templates M-06 and M-07.
- **CP3-T4.** Timers TM-2 (nudge, M-05) and TM-3 (stale).
- **CP3-T5.** Calendly adapter (token in `utm_content`). Only if a pilot agent uses Calendly; otherwise skipped.

**What you can see:** book a consult from the reply email. Within a minute the lead shows Consult booked and you get M-06. Cancel it: the lead goes back to Contacted and M-07 arrives once.

**Tests that must pass:** TP-U-SM-03, TP-U-SM-04, TP-U-SM-05, TP-U-SM-12, TP-U-SM-15, TP-U-SM-16, TP-U-MT-01, TP-U-MT-02, TP-I-05, TP-F-03, TP-F-04, TP-F-12. TP-I-14 only if CP3-T5 is built.

**Done when**
- [ ] A booking is matched by token on the demo environment.
- [ ] A duplicate booking webhook causes one state change.
- [ ] Cancellation follows T-6.
- [ ] The nudge fires once at 24 hours (fake clock).

**Rollback:** `BOOKING_ENABLED=false`. Remove the webhook in Cal.com.

---

## CP4. Agreement prompt, sent and signed detection

**Goal:** When a consult is booked, the agent gets a one-click prompt to a DocuSign draft from their own template addressed to the buyer, and the system detects "sent" and "signed".

**Tasks**
- **CP4-T1.** DocuSign connect flow for an agent, encrypted token, daily refresh (ES-1, TM-16).
- **CP4-T2.** DocuSign wrapper with exactly four functions (ES-8). Draft creation (ES-3). Confirm page and sending link (ES-4).
- **CP4-T3.** DocuSign webhook with HMAC check (ES-5). Status ranks (DL-2). Transitions T-8 to T-11.
- **CP4-T4.** Alert email basics through Postmark: M-20, M-22, M-23, M-24. Signed one-click links with confirm pages (AL-5).
- **CP4-T5.** Other-tool path: "I sent it" and "Signed" buttons. First notice-email parser (DocuSign "completed" email) as the email fallback (ES-7).
- **CP4-T6.** Agreement end date, TM-8 and TM-9, end-date correction button (the ENDS text command comes in CP6).
- **CP4-T7.** Send re-prompt TM-5 (M-21) and countersign nudge TM-7.

**What you can see:** book a consult. Your "agent" inbox gets M-20. Click, confirm, and land in the DocuSign sandbox draft addressed to the test buyer. Press Send. The buyer inbox gets DocuSign's email and the lead shows Agreement sent within a minute. Sign: the lead shows Signed and M-22 arrives.

**Tests that must pass:** TP-U-SM-06 to 10, TP-U-SM-13, TP-U-SM-17, TP-I-06, TP-I-07, TP-I-12, TP-CMP-08, TP-F-01, TP-F-12, TP-F-14.

**Done when**
- [ ] The draft request body holds only the template ID and the recipient (test passes).
- [ ] "Sent" and "completed" webhooks change the state within 60 seconds.
- [ ] "Completed" before "sent" ends in Signed.
- [ ] The wrapper has exactly four public functions.

**Rollback:** `AGREEMENT_PROMPTS_ENABLED=false` (agents get a plain "send it from your tool" note). Remove the app from the DocuSign sandbox.

---

## CP5. Reminders that stop when signed

**Goal:** After the agreement is sent, reminders go out on schedule inside the buyer's window and stop at once on signed, declined, paused or STOP.

**Tasks**
- **CP5-T1.** Reminder scheduler (RR-1 to RR-6, RR-10, RR-11): offsets, maximum, spacing, window shift, jitter, excluded days.
- **CP5-T2.** Guarded send (RR-7) under the lead lock. Skip reasons logged.
- **CP5-T3.** DocuSign resend for DocuSign leads (ES-6). M-08 and M-09 for others. LINK reply: M-17 plus an agent alert.
- **CP5-T4.** Last reminder: M-31. NUDGE as a button for now (the text command comes in CP6).
- **CP5-T5.** Fast clock for the demo environment (ENV-2) and the fake-clock test harness.

**What you can see:** on the demo environment with the fast clock, three reminders go out on schedule inside the window. Sign after the first: the second never sends, and the timeline shows "skipped: signed".

**Tests that must pass:** TP-U-RM-01 to 12, TP-U-IDEM-04, TP-U-IDEM-05, TP-F-05, TP-F-11, TP-F-19.

**Done when**
- [ ] All reminder unit tests pass.
- [ ] The sign-after-queue test passes.
- [ ] A 7-day fast-clock run sends no reminder outside the window.
- [ ] The crash test leaves an "unknown" row, never a double send.

**Rollback:** `REMINDERS_ENABLED=false` (jobs stay, their guard skips them). An operator action deletes pending reminder jobs.

---

## CP6. Reply sorter and legal questions

**Goal:** Buyer replies are sorted into the five labels, legal questions go to the agent with the fixed holding reply and paused reminders, and the sorter passes the 30-reply test.

**Tasks**
- **CP6-T1.** Sorter module (RS-4 to RS-12): masking, Gemini call with the fixed schema, timeout, fallback. Import-boundary test.
- **CP6-T2.** Label handlers FR-34 to FR-39. Templates M-10 to M-13. Pause on legal question (T-15) and RESUME (T-16).
- **CP6-T3.** Agent commands by text and by email reply (ARCHITECTURE section 14), with phone and DKIM checks (AL-6).
- **CP6-T4.** Eval script for TP-AI-01 and TP-AI-02: runs the 30 replies 3 times, prints score and misses. Choose the model. Log the result in DECISIONS.md.
- **CP6-T5.** Sorter records (DS-11) and the weekly sample report used in VERIFY.md.

**What you can see:** reply "what's your commission?" to the demo email. Within a minute the buyer gets the holding reply, the agent inbox gets the exact question, and the timeline shows reminders paused. Reply "can we see 12 Oak St Saturday?": the agent gets a tour alert. Run the eval script and see the real score and misses.

**Tests that must pass:** TP-U-KW-08, TP-U-KW-09, TP-U-SM-14, TP-I-10, TP-I-11, TP-CMP-01 to 04, TP-CMP-20, TP-AI-01, TP-AI-02, TP-F-09.

**Done when**
- [ ] TP-AI-01 meets its pass bar in 3 runs in a row, with the real output saved.
- [ ] A legal question never gets anything except M-10.
- [ ] With the sorter switched off, replies go to the agent as "other" and opt-out words still work.

**Rollback:** `SORTER_ENABLED=false`: every reply that is not an opt-out goes to the agent as "other".

---

## CP7. Alerts, escalation, operator page and approvals

**Goal:** Every alert reaches the agent with one-click actions, unacknowledged urgent alerts escalate, and you can see health, approve templates and pause everything from one page.

**Tasks**
- **CP7-T1.** Alert service: alert rows, alert hours (AL-3), escalation TM-10 and TM-11, M-28, M-29, ACK.
- **CP7-T2.** Morning list (M-34) and weekly summary (M-35).
- **CP7-T3.** Operator page part 1: login with 2FA, agents, leads, lead timeline.
- **CP7-T4.** Operator page part 2: messages, alerts, unmatched events, errors, health banner, pause switches.
- **CP7-T5.** Daily operator summary (M-50), error alerts (M-51, M-52), uptime monitor and Sentry.
- **CP7-T6.** Template pack and approvals: render every template with version numbers for the agent; record approvals; go-live gate (FR-52); banned-word check (CR-9).

**What you can see:** trigger an urgent alert and ignore it. With the fast clock, the second notice comes at 30 minutes and the backup notice at 60. On the operator page, press global pause and submit a lead: no message goes out. Try to switch the demo agent to live with one template unapproved: refused.

**Tests that must pass:** TP-CMP-11, TP-CMP-17, TP-U-CFG-02 to 04, TP-F-08, TP-F-10, TP-F-20.

**Done when**
- [ ] Escalation stops after two levels.
- [ ] The go-live gate refuses each missing item, one at a time.
- [ ] The operator page requires 2FA.
- [ ] The morning list arrives at 7:30 agent time in a fast-clock run.

**Rollback:** `ESCALATION_ENABLED=false`. Revert the deploy.

---

## CP8. Tour alert (RISKIEST)

**Goal:** When a tour is booked for a buyer with no valid signed agreement, the agent is alerted within minutes, from any of the five signal sources.

**Why it is the riskiest:** it depends on data we don't control (what ShowingTime emails contain, how fast the calendar link updates, whether agents log tours at all). Its spikes run first, in CP0-T1 and CP0-T2.

**Tasks**
- **CP8-T1.** tour_signals table, merge rule (TD-6), cancellation handling (DL-8).
- **CP8-T2.** ShowingTime parser built from the CP0-T2 samples, with saved redacted test files.
- **CP8-T3.** Calendar reader (TD-3): read every 10 minutes, compare snapshots, tour-like test (TD-4), privacy rule (TD-9).
- **CP8-T4.** Matcher with confidence levels (TD-5). M-27 "Who is this tour for?" with buyer buttons.
- **CP8-T5.** Alert decision (TD-7), end-date check, alert-hours override (FR-44), M-26 through the alert service.
- **CP8-T6.** TOUR and NUDGE commands (M-36). Tour-request leads (FR-5). wants_tour hook (FR-37).
- **CP8-T7.** "Today's tours" in the morning list. Per-agent "last ShowingTime email received" indicator (FC-13).

**What you can see:** create a calendar event "Showing - Test Buyer - 12 Oak St" for tomorrow. Within about 12 minutes the agent inbox gets M-26. Forward a sample ShowingTime email: alert within 2 minutes. Send "TOUR Test Buyer": status reply within a minute. Sign the agreement: the next tour signal for that buyer gives no alert.

**Tests that must pass:** TP-U-MT-03 to 06, TP-I-08, TP-I-09, TP-F-06, TP-F-13, TP-F-15.

**Done when**
- [ ] Each of the five sources produces the right alert, or no alert, on the demo environment.
- [ ] An unmatched tour gives exactly one M-27.
- [ ] A signed buyer with a valid end date gives no alert.
- [ ] An expired agreement gives an alert.

**Rollback:** `TOUR_ALERTS_ENABLED=false`. The morning list still lists unsigned buyers.

---

## CP9. Pilot readiness, end-to-end test and demo video

**Goal:** The full flow passes end to end on sandbox accounts, the first real lead source works, and the go-live checklist can be run for one agent.

**Tasks**
- **CP9-T1.** Parser for the first pilot's lead source (Zillow or other), built from saved redacted samples, with its tour-request marker. (PRD OQ-11)
- **CP9-T2.** Run TP-E2E-01 and TP-E2E-02 on the demo environment. Fix what breaks.
- **CP9-T3.** You run the 15-minute manual script (TP-M-01 to TP-M-10) and save the results.
- **CP9-T4.** Record the 2-minute demo video using the fast clock.
- **CP9-T5.** Retention job (TM-17), backups, a restore test (ENV-5).
- **CP9-T6.** Onboarding kit: the go-live checklist (VERIFY.md section 1), filter instructions with screenshots, the template pack, the form checklist, draft pilot terms for the lawyer.

**What you can see:** the 2-minute video and your filled-in manual test sheet.

**Tests that must pass:** TP-E2E-01, TP-E2E-02, TP-M-01 to TP-M-10, TP-F-16, TP-F-17, and the full automated suite.

**Done when**
- [ ] TP-E2E-01 passes twice in a row.
- [ ] Every manual step passes.
- [ ] The video is recorded.
- [ ] A restore from backup worked.
- [ ] The onboarding kit is ready to send.

**Rollback:** set any pilot agent back to test mode. Global pause.
