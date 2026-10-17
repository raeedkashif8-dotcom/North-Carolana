# Test Plan

Version 0.1, 2026-10-16. Status: draft, not approved.

**Current result of every test below: not run.** No code exists yet. Results get recorded in section 9 as checkpoints finish.

Built on the Stage 0 defaults. [Depends on Q1 to Q7] Q6 decides whether the manual script uses a real phone.

## 0. How tests run

- **Framework:** pytest. A fake clock (time-machine) for anything with time. HTTP mocks (respx) for outside services.
- **Database:** a real local Postgres in Docker, so locks and unique keys behave as in production.
- **Fixtures:** a `fixtures/` folder of redacted real samples: ShowingTime emails, lead emails, DocuSign webhook bodies, Cal.com payloads, iCal files.
- **Test agent:** "test-agent", Eastern time, window 9:00 to 20:00, reminders at 24, 72 and 168 hours, maximum 3, default term 30 days, alert hours 7:00 to 22:00. Jitter is 0 in tests unless a test says otherwise.
- **CI:** GitHub Actions runs everything on each push. A failing test blocks the merge.
- **Times:** every expected time below is in the buyer's local time unless marked otherwise.

## 1. Unit tests

### 1.1 State machine

| ID | Given | When | Then |
|---|---|---|---|
| TP-U-SM-01 | No leads | Web form lead: "Test Buyer", buyer@example.com, no phone | Lead goes NEW then CONTACTED after M-01 sends. One M-01 row. Consent event (email, own_form). Audit rows: lead created, message sent, state changed. |
| TP-U-SM-02 | Lead L1 created 3 days ago with buyer@example.com | Same email submits the form again | No new lead. Event logged as attached to L1. No new message. |
| TP-U-SM-03 | L1 CONTACTED, token t1, trigger on_booking | Booking created with metadata lead=t1 | L1 CONSULT_BOOKED then AWAITING_SEND. M-06 to buyer, M-20 to agent, one DocuSign draft (mock). TM-2 cancelled, TM-5 set. |
| TP-U-SM-04 | L1 AWAITING_SEND, nothing sent | Booking cancelled | L1 CONTACTED. M-07 once. A second cancellation later sends no second M-07. |
| TP-U-SM-05 | L1 SENT | Booking cancelled | L1 stays SENT. Reminders unchanged. Audit "booking cancelled after send". |
| TP-U-SM-06 | L1 AWAITING_SEND | DocuSign "sent" webhook for L1's draft | L1 SENT. Reminder jobs for 24, 72, 168 hours. TM-5 cancelled. |
| TP-U-SM-07 | L1 SENT, reminders 2 and 3 pending | DocuSign "completed" | L1 SIGNED. Pending reminders cancelled. M-22 to agent, M-16 to buyer. End date = completed date plus 30 days. TM-8 and TM-9 set. |
| TP-U-SM-08 | L1 AWAITING_SEND | "completed" arrives, then "sent" | L1 SIGNED after the first. The late "sent" is logged as ignored. No reminders created. |
| TP-U-SM-09 | L1 SENT, template has Buyer and Agent signers | Buyer recipient completed | L1 BUYER_SIGNED. Reminders cancelled. M-23. TM-7 set. |
| TP-U-SM-10 | L1 SENT | Envelope declined | L1 DECLINED. Reminders cancelled. M-24. |
| TP-U-SM-11 | L1 in each of NEW, CONTACTED, CONSULT_BOOKED, AWAITING_SEND, SENT | Inbound text "STOP" | State unchanged. FL-1 set. All buyer jobs cancelled. M-14 once. M-30. Consent revocation event. |
| TP-U-SM-12 | L1 CLOSED (stale) | Booking created with L1's token | L1 CONSULT_BOOKED (reopened), audit "reopened by booking". A timer firing for a CLOSED lead does nothing. |
| TP-U-SM-13 | L1 SIGNED, end date 2026-11-19 | Clock moves to 2026-11-20 0:00 agent time | L1 EXPIRED, M-33. M-32 was sent 2026-11-16 at 9:00. |
| TP-U-SM-14 | L1 SENT, reminder 2 due in 5 hours | Reply sorted legal_question; later the agent sends RESUME at time R | M-10 to buyer, M-25 to agent, FL-2 set, reminder 2 skipped "paused". After RESUME, next reminder at R plus 24 hours, inside the window. |
| TP-U-SM-15 | L1 CONTACTED, no booking | Clock plus 30 days | L1 CLOSED. No message. Listed in the next weekly summary. |
| TP-U-SM-16 | L1 CONTACTED | The same Cal.com webhook arrives twice | One booking row, one state change, one M-06. |
| TP-U-SM-17 | L1 SENT, agent on a non-DocuSign tool | Agent texts "SIGNED Test Buyer" | L1 SIGNED. Reminders cancelled. M-22. Confirmation to the agent. |
| TP-U-SM-18 | No leads | Lead with no email and an invalid phone | L1 CLOSED (no contact). No buyer message. M-38 to agent. |

### 1.2 Reminder timing

| ID | Given | When | Then |
|---|---|---|---|
| TP-U-RM-01 | Sent Tue 2026-10-20 10:00, buyer Eastern | Schedule | Reminder 1 Wed 10:00, 2 Fri 10:00, 3 Tue Oct 27 10:00 |
| TP-U-RM-02 | Sent Tue 19:30 | Schedule reminder 1 | Wed 19:30 (inside window) |
| TP-U-RM-03 | Sent Tue 22:30 | Schedule reminder 1 | Thu between 9:00 and 9:20 (jitter on) |
| TP-U-RM-04 | Sent Tue 9:30 Eastern, buyer Pacific | Schedule reminder 1 | Wed between 9:00 and 9:20 Pacific |
| TP-U-RM-05 | Sent Sat 2026-10-31 10:00 EDT | Schedule reminder 1 | Sun 2026-11-01 9:00 EST (24 real hours later; clocks fell back) |
| TP-U-RM-06 | Maximum 3 | Reminder 3 sent | No reminder 4 job. M-31 to agent. |
| TP-U-RM-07 | Signed between reminders 1 and 2 | Reminder 2 time | Reminders 2 and 3 skipped "signed". No buyer message. |
| TP-U-RM-08 | Opted out between reminders 1 and 2 | Reminder 2 time | Skipped "opted out". |
| TP-U-RM-09 | Paused before reminder 2; RESUME two days later at 14:00 | Resume | Next reminder the following day at 14:00, then reminder 3 per spacing. No burst of reminders. |
| TP-U-RM-10 | Offsets 24 and 45 hours; sent Tue 21:00 | Schedule | Reminder 1 Thu 9:00 (window shift). Reminder 2 due Thu 18:00 is under 20 hours after reminder 1, so it moves to Fri 9:00. |
| TP-U-RM-11 | Config offsets 12 and 72, or 24 and 30 | Load config | Rejected: "offset under 20 hours" or "offsets under 20 hours apart". Agent blocked. M-52. |
| TP-U-RM-12 | Sundays excluded; reminder 1 due Sun 10:00 | Schedule | Mon between 9:00 and 9:20 |

### 1.3 Time zones and windows

| ID | Given | When | Then |
|---|---|---|---|
| TP-U-TZ-01 | Lead zip 27601 | Resolve zone | America/New_York |
| TP-U-TZ-02 | No zip, phone +1 213 555 0123 | Resolve zone | America/Los_Angeles |
| TP-U-TZ-03 | No zip, an area code mapped to Eastern and Central (test fixture) | Compute window | 10:00 to 20:00 Eastern (the overlap of both 9:00 to 20:00 windows) |
| TP-U-TZ-04 | No zip, no phone | Resolve zone | America/New_York |
| TP-U-TZ-05 | Text consent, buyer Eastern, lead at 21:30 | Instant reply | M-01 email now. M-02 text at 9:00 to 9:20 next day. |
| TP-U-TZ-06 | Config window 7:00 to 22:00 | Load config | Rejected: outside the 8:00 to 21:00 hard limit |

### 1.4 Templates

| ID | Given | When | Then |
|---|---|---|---|
| TP-U-TPL-01 | Template has a misspelled fill-in `{buyer_fist_name}` | Render | Fails. No send. M-51. Audit "render failed". |
| TP-U-TPL-02 | No buyer first name | Render a template with fallback "there" | "Hi there," is used. Without a defined fallback, render fails closed. |
| TP-U-TPL-03 | Config points to M-08 version 4, only version 3 approved | Send | Refused. M-51. |
| TP-U-TPL-04 | Approved explainer with hash H | Render M-01 | Explainer block is byte-identical (sha256 = H) |
| TP-U-TPL-05 | A text template over 3 segments (459 plain characters, or 201 with special characters) | Approval attempt | Rejected at approval time, length shown |

### 1.5 Opt-out rules

| ID | Input | Expected |
|---|---|---|
| TP-U-KW-01 | "STOP" | Opt-out by rule RS-2. Sorter not called. |
| TP-U-KW-02 | "stop." | Opt-out by rule |
| TP-U-KW-03 | "  Stop  " | Opt-out by rule |
| TP-U-KW-04 | "UNSUBSCRIBE" | Opt-out by rule |
| TP-U-KW-05 | "opt out" | Opt-out by rule (Twilio would not catch this one) |
| TP-U-KW-06 | "Revoke" | Opt-out by rule |
| TP-U-KW-07 | "please stop texting me" | Not caught by rules (no phrase list, D-32). Goes to the sorter; with the sorter down, treated as opt-out because it contains "stop" (FR-39). |
| TP-U-KW-08 | "I need to cancel our call tomorrow" | Not caught by rules. Goes to the sorter. |
| TP-U-KW-09 | Same as 08, sorter unavailable | Treated as opt-out (FR-39) |
| TP-U-KW-10 | After a text opt-out, inbound "START" | Text opt-out cleared, consent event, agent told, reminders stay off |

### 1.6 Masking

| ID | Input | Expected stored and sorter text |
|---|---|---|
| TP-U-MASK-01 | "my card is 4111 1111 1111 1111" | "my card is [number]" |
| TP-U-MASK-02 | "SSN 123-45-6789" | "SSN [number]" |
| TP-U-MASK-03 | "routing 021000021 account 123456789012" | "routing [number] account [number]" |
| TP-U-MASK-04 | "call me at 919-555-0142 or test@example.com" | "call me at [phone] or [email]" |
| TP-U-MASK-05 | Inbound picture message | No media stored in our database or files. Twilio media delete called (mock). Agent gets the attachment note. |

### 1.7 Matching

| ID | Given | Expected |
|---|---|---|
| TP-U-MT-01 | Booking with token t1 | Matched to L1 |
| TP-U-MT-02 | Booking without token, attendee email equals L1's email | Matched to L1 |
| TP-U-MT-03 | Calendar event with L1's email as attendee | High confidence match to L1 |
| TP-U-MT-04 | Event "Showing - Jane Doe - 12 Oak St", one active lead named Jane Doe, unsigned | Medium match; M-26 |
| TP-U-MT-05 | Event "Showing - Smith", two active leads named Smith | Low; one M-27 listing both |
| TP-U-MT-06 | Email reply from a different address, In-Reply-To equals our M-01 Message-ID for L1 | Matched to L1 |

### 1.8 Idempotency

| ID | Given | Expected |
|---|---|---|
| TP-U-IDEM-01 | The same Twilio MessageSid posted twice | One event row. Second post answers 200 and logs "duplicate". |
| TP-U-IDEM-02 | Two send attempts with the same outbound key | One provider call (mock counts 1) |
| TP-U-IDEM-03 | Job key `L1:reminder:2` scheduled twice | One job row |
| TP-U-IDEM-04 | Worker killed after the outbound row is "queued", before the provider call | After 2 minutes the row is "unknown". No provider call ever made for that key. M-51. |
| TP-U-IDEM-05 | Two workers poll for one due job at the same moment | Exactly one runs it |

### 1.9 Config

| ID | Given | Expected |
|---|---|---|
| TP-U-CFG-01 | Config missing firm_address | Validation fails. That agent's sending blocked. Another agent unaffected. M-52. |
| TP-U-CFG-02 | Reminder offsets 12 and 72 | Rejected (same as TP-U-RM-11) |
| TP-U-CFG-03 | Window 7:00 to 22:00 | Rejected (same as TP-U-TZ-06) |
| TP-U-CFG-04 | Status "live" with M-08 unapproved | Rejected by the go-live gate |

## 2. Integration tests (outside services mocked)

| ID | Setup | Action | Expected |
|---|---|---|---|
| TP-I-01 | Gmail API mocked | Submit the demo form | One Gmail send call. From is the agent, Reply-To is the agent's plus address, List-Unsubscribe present, approved explainer present, booking link carries the token. |
| TP-I-02 | Twilio test credentials (real API, no real texts) | Send to +15005550006, +15005550001, +15005550004 | First accepted, provider ID stored. Second: error 21211, marked failed, email still sent. Third: error 21610, lead's texting marked opted out, no retry. |
| TP-I-03 | Inbound text webhook | Post with a valid Twilio signature, then a bad one | Valid: 200, event saved. Bad: 403, nothing saved. |
| TP-I-04 | Postmark inbound fixture: buyer replies to M-01 | Post to the webhook | Matched to L1. Sorter (mocked) called once. Label handled. |
| TP-I-05 | Cal.com fixture with metadata lead=t1 | Post with a valid signature, then a bad one | Valid: L1 CONSULT_BOOKED. Bad: 401, nothing saved. |
| TP-I-06 | DocuSign API mocked | Send trigger fires | Exactly one create-envelope call. Body holds templateId, the Buyer role with name and email, status "created", and our webhook settings. Body holds no documents, no tabs, no field values. |
| TP-I-07 | DocuSign webhook fixtures | "completed" with a valid HMAC, then one with a bad HMAC | Valid: SIGNED. Bad: 401, ignored. |
| TP-I-08 | Local server serves an iCal file, then a new version with "Showing - Test Buyer" added | Two reads | One new tour signal. Unchanged events produce nothing. A removed event closes its signal. |
| TP-I-09 | Redacted ShowingTime fixture from CP0-T2 | Post to the Postmark webhook | Tour signal with status, start time, address, and buyer name if the fixture has one |
| TP-I-10 | Gemini mocked: `{"label": "legal_question", "possible_opt_out": false, "language": "en"}` | Buyer reply | M-10 and M-25 queued. FL-2 set. |
| TP-I-11 | Gemini mocked: timeout | Reply "is it still available?" | Label "other". M-39 to the agent. Only M-13 to the buyer, if turned on. |
| TP-I-12 | Gmail mocked: `invalid_grant` on send | Send M-01 | Email paused for the agent. M-40 to the agent through Postmark. M-51 to you. No retry loop. |
| TP-I-13 | Global pause on | New lead, and a reminder comes due | Lead recorded. No provider calls. After unpause, jobs re-check; the reminder sends only if still valid. |
| TP-I-14 | Calendly fixture, invitee.created with utm_content t1 | Post | L1 CONSULT_BOOKED. Only if Calendly is built (CP3-T5). |

## 3. End-to-end tests (sandbox accounts)

**Setup:** demo environment; demo agent in test mode; agent inbox is your second email; buyer is your main email (plus your phone if it is a US number [Depends on Q6]); DocuSign sandbox template; Cal.com test event; your test Google calendar link; fast clock (1 day = 2 minutes); calendar read every minute in demo.

**TP-E2E-01. A fake lead through all 5 steps of your build order**

| Step | Your build step | Action | Expected | Max time |
|---|---|---|---|---|
| E1 | 1. Lead in, instant reply | Submit the demo form | M-01 in the buyer inbox. Lead CONTACTED. | 60 s |
| E2 | 2. Booking | Book from the link | Lead AWAITING_SEND. M-06 to buyer. M-20 to agent. | 60 s |
| E3 | 3. Agreement out | Agent opens M-20, confirms, presses Send in the DocuSign draft | Lead SENT | 60 s after DocuSign's webhook |
| E4 | 4. Reminders (part 1) | Wait for reminder 1 | DocuSign resend email arrives (and a text if a US phone is used) | Per fast clock |
| E5 | 5. Tour alert | Create "Showing - Test Buyer" tomorrow 10:00 in the test calendar | M-26 in the agent inbox | 3 min |
| E6 | 4. Stop when signed (part 2) | Sign as buyer (and as agent if the template has an agent signer) | Lead SIGNED. M-22 and M-16. Reminder 2 never sends. A second tour event for the same buyer gives no alert. | 60 s |
| E7 | Audit | Open the lead timeline | Every step present with times. No duplicate messages. Every message an approved version. | |

Pass: every step within its time, zero duplicates, zero unapproved messages.

**TP-E2E-02. STOP in the middle**

Lead in, booked, agreement sent. The buyer replies STOP by text, or clicks unsubscribe. Expected within 60 seconds: opted out, no reminder ever sends, M-30 to the agent. A later tour signal for this buyer still alerts the agent (agent alerts are not buyer messages). The buyer receives nothing more.

## 4. Compliance tests

| ID | Given | Input | Expected |
|---|---|---|---|
| TP-CMP-01 | L1 SENT | Buyer: "what is the commission?" | legal_question. Buyer gets M-10 exactly as approved and nothing else. Agent gets M-25 with the exact words within 60 s. Reminders paused. Fails if any other buyer message is sent. |
| TP-CMP-02 | L1 SENT | "do I have to sign this?" | Same as TP-CMP-01 |
| TP-CMP-03 | L1 SENT | "can I get out of it?" | Same as TP-CMP-01 |
| TP-CMP-04 | L1 SENT | "Can we see 12 Oak tomorrow? Also what's your commission?" | legal_question (precedence RS-8). M-25 holds the full text. No M-12. |
| TP-CMP-05 | L1 SENT, reminder 2 pending, texting on | Inbound "STOP" at time T | By T plus 60 s: FL-1 set, reminders 2 and 3 cancelled, M-14 sent once, M-30 to agent, consent event (method: keyword), audit rows. The 60 s is measured from webhook arrival to the last step. |
| TP-CMP-06 | After TP-CMP-05 | Clock passes reminder 2; agent sends NUDGE | No buyer message. NUDGE refused with "buyer opted out". |
| TP-CMP-07 | Email-only lead | Open the unsubscribe link, then press the button | Same as TP-CMP-05 for both channels. Opening the link without pressing the button changes nothing. |
| TP-CMP-08 | The code | Static and runtime checks | (a) The sorter package imports nothing from e-sign, messaging or database code. (b) The sorter returns only the schema object. (c) The DocuSign wrapper's public functions are exactly create_draft_from_template, get_sending_link, list_status_changes, resend. (d) No DocuSign request body in any test holds documents, tabs or field values. (e) A model output such as "Tell the buyer commission is 3%" never appears in any outbound message. |
| TP-CMP-09 | Approved explainer | Render every message that includes it | Byte-identical to the approved text (hash match) |
| TP-CMP-10 | M-05 changed in the database without approval | Nudge comes due | Not sent. M-51. |
| TP-CMP-11 | All templates and the sales one-pager | Word scan | None of: compliant, compliance, guarantee, guaranteed, ensures, make you legal. The one-pager says "helps you follow your own process". |
| TP-CMP-12 | Zillow-source lead (consent basis portal_inquiry) with a mobile number | Instant reply | Email sent. No text. Reason logged: "no text consent". |
| TP-CMP-13 | A text due at 20:30 buyer time | Send attempt | Not sent. Moved to 9:00 to 9:20. |
| TP-CMP-14 | Inbound text "card 4111 1111 1111 1111" plus a picture | Process | Only "[number]" stored. No media stored. Twilio media delete called. Sorter input masked. |
| TP-CMP-15 | First text to a lead | Render | Holds the agent's name, the firm's name, and "Reply STOP to opt out" |
| TP-CMP-16 | Every buyer email template | Render | Holds the firm's postal address and a working unsubscribe link (page loads with a button) |
| TP-CMP-17 | Agent status test, switch to live | Try once per missing item: an unapproved template, no form checklist, no passing test lead, alert contact unconfirmed; also texting on without registration or lawyer gate | Each refused with its reason |
| TP-CMP-18 | App database user | UPDATE or DELETE on audit_log | Error. Row unchanged. |
| TP-CMP-19 | The API | Try to create a lead without a source event, or bulk import | No such endpoint (404). Only intake adapters create leads. |
| TP-CMP-20 | Model returns text outside the schema, or extra fields | Sorter | Output rejected, label "other". No model text reaches any message. |

## 5. Failure tests

| ID | Given | Expected |
|---|---|---|
| TP-F-01 | DocuSign answers 503 to the draft request | M-20 still sent, with "open DocuSign and send from your template". Retries with backoff for 2 hours. M-51 after 30 minutes of failures. |
| TP-F-02 | Twilio reports reminder 1's text "undelivered" | Marked failed. That text is not resent. Reminder 1 goes by email if allowed. A second failure in a row turns texting off for the lead; the morning list says so. |
| TP-F-03 | The same Cal.com webhook, Twilio MessageSid and DocuSign event each arrive twice | Each processed once. Exactly one message per intent. |
| TP-F-04 | A provider retries one webhook 5 times, 1 second apart | One processed event, one message |
| TP-F-05 | (a) "Signed" is saved before the reminder 2 job takes the lock. (b) The reminder 2 job holds the lock mid-send when "signed" arrives. | (a) Reminder skipped "signed". (b) "Signed" waits for the lock; reminder 2 completes (one message); reminder 3 never sends; logged. |
| TP-F-06 | Alert hours 7:00 to 22:00. At 23:00, a ShowingTime email for an unsigned buyer's tour tomorrow at 10:00; a second one for a tour in 3 days | First: M-26 at once (tour within 12 hours). Second: M-26 at 7:00. |
| TP-F-07 | Buyer in Pacific time | All texts and reminders between 9:00 and 20:00 Pacific |
| TP-F-08 | Urgent alert never acknowledged | M-28 at 30 minutes, M-29 to the backup at 60 minutes if set, nothing more. Listed in the next M-50. |
| TP-F-09 | Gemini answers 500 to every call; three replies arrive, one is "cancel our call" | All labeled "other" and sent to the agent. The "cancel" reply is treated as opt-out. M-51 after 5 failures. |
| TP-F-10 | Database unreachable for 2 minutes while webhooks arrive | Webhooks get 503. Providers retry. Afterwards each event is processed once, no duplicates. |
| TP-F-11 | Worker crashes after an outbound row is queued | After restart the row becomes "unknown" within 2 minutes. No resend. M-51. |
| TP-F-12 | DocuSign "completed" before "sent"; Cal.com "rescheduled" before "created" | Final states SIGNED, and CONSULT_BOOKED with the newer time |
| TP-F-13 | Tour signal for yesterday | Logged, no alert |
| TP-F-14 | Agent's Google and DocuSign access revoked | That feature pauses. M-40 to the agent, M-51 to you. Other agents fine. No crash loop. |
| TP-F-15 | Calendar link returns 404 for an hour | Retries every 10 minutes. After 1 hour the agent and you are told. The morning list says calendar checks are paused. |
| TP-F-16 | A lead email in an unknown format | No lead created. Raw email kept 30 days. M-51. |
| TP-F-17 | Gmail answers 429 (rate limit) | Back off and retry later. M-51 if it lasts over 30 minutes. |
| TP-F-18 | Twilio answers 21610 to a send | Texting marked opted out for that lead (method: carrier). No retry. |
| TP-F-19 | Reminders scheduled across the end of daylight saving (Nov 1, 2026) | Correct local times (example RE-5) |
| TP-F-20 | Agent A's config edited into an invalid state | Agent A blocked, Agent B keeps sending, M-52 |

## 6. Wrong-output test for the reply sorter

**TP-AI-01. 30 sample replies.** Each runs through the full sorter (rules first, then Gemini), with "previous message: instant reply" as context. The samples are never used as examples in the prompt (RS-5).

**Pass bar (all must hold):**
1. At least 27 of 30 correct (90%).
2. All 6 "stop" samples end as opt-out. Zero misses.
3. All 8 "legal_question" samples end as legal_question. Zero misses.
4. A "false stop" (a non-stop sample treated as opt-out) counts as a miss in item 1, but does not fail items 2 and 3.

**TP-AI-02. Repeatability.** Run TP-AI-01 three times. Pass only if all three runs pass. Models do not always answer the same way twice.

**How it runs:** the eval script from CP6-T4. It prints the score per run and a table of misses: ID, text, expected, got, and which layer decided (rule or model). It runs for `gemini-3.1-flash-lite` and, for comparison, `gemini-3.8-flash`.

| ID | Buyer reply | Expected | Should be caught by |
|---|---|---|---|
| AI-S01 | STOP | stop | Rule RS-2 |
| AI-S02 | Stop texting me please | stop | Model |
| AI-S03 | Not interested anymore, we went with another agent | stop | Model |
| AI-S04 | take me off your list | stop | Model |
| AI-S05 | Who is this?? Don't contact me again | stop | Model |
| AI-S06 | I'm all set for now, no more messages please | stop | Model |
| AI-S07 | What's your commission? | legal_question | Model |
| AI-S08 | Do I have to sign this before seeing a house? | legal_question | Model |
| AI-S09 | Can I get out of the agreement if I'm not happy with you? | legal_question | Model |
| AI-S10 | Who pays you, me or the seller? | legal_question | Model |
| AI-S11 | Is this exclusive? Can I still look with other agents? | legal_question | Model |
| AI-S12 | How long does the agreement last and can I cancel it? | legal_question | Model (has "cancel"; must not be opt-out) |
| AI-S13 | My lender told me not to sign anything yet. Is that right? | legal_question | Model |
| AI-S14 | What happens if I find a house on my own while I'm signed with you? | legal_question | Model |
| AI-S15 | Yes let's set up a call | wants_consult | Model |
| AI-S16 | Can we talk tomorrow afternoon? | wants_consult | Model |
| AI-S17 | The booking link isn't working, can you send it again? | wants_consult | Model |
| AI-S18 | Sure! What times do you have this week? | wants_consult | Model |
| AI-S19 | I need to cancel our call tomorrow, can we do Friday instead? | wants_consult | Model (has "cancel"; must not be opt-out) |
| AI-S20 | Can I see 412 Oak St this Saturday? | wants_tour | Model |
| AI-S21 | We'd love to tour the house on Maple before it's gone | wants_tour | Model |
| AI-S22 | Can you show us a few homes in Cary next weekend? | wants_tour | Model |
| AI-S23 | When can we go see it? | wants_tour | Model |
| AI-S24 | Saw it on Zillow, want to walk through Thursday evening | wants_tour | Model |
| AI-S25 | Is 412 Oak St still available? | other | Model |
| AI-S26 | Thanks! | other | Model |
| AI-S27 | We're pre-approved up to 350k | other | Model |
| AI-S28 | Does the house have a basement? | other | Model |
| AI-S29 | ¿Podemos ver la casa el sábado? | other | Model (not English, so it goes to the agent, A4) |
| AI-S30 | What's the HOA fee on that one? | other | Model ("fee" here is not commission) |

**Results: not run.** Misses table: not run. The first real run happens in CP0-T5 (throwaway) and the official one in CP6-T4. Both get pasted here with the date, model and prompt version.

**In production:** every week, review 20 random sorted replies plus every stop and legal_question label (VERIFY.md). Any misrouted stop or legal question stops the sorter (SORTER_ENABLED=false) until fixed and retested.

## 7. Manual test script (15 minutes, your phone and email)

**Before you start (not counted):** demo environment up; demo agent in test mode; agent email is your second inbox; your main email (and phone, if US) on the allowlist; fast clock on (1 day = 2 minutes); calendar read every minute; a timer running. If your phone is not a US number, skip the text parts. [Depends on Q6]

| ID | Minute | Do this | Pass if |
|---|---|---|---|
| TP-M-01 | 0:00 | On your phone, submit the demo form: name, main email, and phone with the text box ticked (US only) | Email arrives within 1 minute with the explainer and a booking link (and a text, if US and inside the window) |
| TP-M-02 | 2:00 | Reply to the email: "what's your commission?" | Within 1 minute: the holding reply in your main inbox, and the exact question in your agent inbox |
| TP-M-03 | 3:30 | In the agent email, click "Resume reminders", then press the button | The page confirms reminders resumed |
| TP-M-04 | 4:30 | Tap the booking link and book any slot | Within 1 minute: "consult booked" email to you, "Send the agreement" email to the agent inbox |
| TP-M-05 | 6:00 | In the agent inbox, open the send link, confirm, and press Send in DocuSign | DocuSign's email reaches your main inbox within 2 minutes |
| TP-M-06 | 8:00 | Wait about 2 minutes | Reminder 1 arrives (DocuSign resend; a text too, if US) |
| TP-M-07 | 10:00 | In your test Google calendar, create "Showing - your name" tomorrow at 10:00 | URGENT tour alert in the agent inbox within 3 minutes |
| TP-M-08 | 12:00 | Sign the agreement from DocuSign's email | Within 1 minute: "Ready to tour" in the agent inbox, "thank you" to you |
| TP-M-09 | 13:30 | Reply STOP by text (US), or click unsubscribe in the last email and press the button | A confirmation (text or page). Nothing else arrives afterwards. |
| TP-M-10 | 14:00 | Open the operator page, find your lead, read its timeline | Every step above is there with times. No duplicate messages. Nothing sent after step TP-M-09. |

Write pass or fail and a note per step in section 9.

## 8. Traceability

| Requirement | Tests |
|---|---|
| FR-1 to FR-6 | TP-U-SM-01, 02, 18; TP-I-01; TP-F-16 |
| FR-7 to FR-10 | TP-U-SM-01; TP-U-TZ-05; TP-U-TPL-04; TP-I-01; TP-CMP-09 |
| FR-11 to FR-14 | TP-U-SM-03, 04, 05, 15, 16; TP-U-MT-01, 02; TP-I-05, 14; TP-F-12 |
| FR-15 to FR-23 | TP-U-SM-06 to 10, 13, 17; TP-I-06, 07; TP-CMP-08; TP-F-01, 12 |
| FR-24 to FR-28 | TP-U-RM-01 to 12; TP-F-05, 19 |
| FR-29 to FR-39 | TP-U-KW-01 to 10; TP-U-SM-11, 14; TP-I-03, 04, 10, 11; TP-CMP-01 to 07; TP-F-09; TP-AI-01, 02 |
| FR-40 | TP-U-SM-17; TP-E2E-01 |
| FR-41 to FR-44 | TP-F-06, 08; TP-E2E-01 |
| FR-45 to FR-49 | TP-U-MT-03 to 05; TP-I-08, 09; TP-F-06, 13, 15 |
| FR-50 to FR-57 | TP-U-CFG-01 to 04; TP-I-13; TP-CMP-10, 17, 18; TP-F-20 |
| CR-1 | TP-CMP-08; TP-I-06 |
| CR-2 | TP-CMP-01 to 04, 20 |
| CR-3 | TP-CMP-09; TP-U-TPL-04 |
| CR-4 | TP-CMP-17 |
| CR-5 | TP-CMP-19; TP-U-SM-02 |
| CR-6 | TP-CMP-05 to 07; TP-E2E-02 |
| CR-7 | TP-U-SM-01; TP-CMP-05 |
| CR-8 | TP-CMP-12, 13 |
| CR-9 | TP-CMP-11 |
| CR-10 | TP-CMP-10; TP-U-TPL-03 |
| CR-11 | TP-CMP-14; TP-U-MASK-01 to 05 |
| CR-12 | TP-CMP-15 |
| CR-13 | TP-CMP-16 |
| CR-14 | TP-CMP-17 |
| CR-15 | TP-CMP-18 |
| CR-16 | Manual review of M-20 to M-40 at template approval (CP7-T6) |

## 9. Results log

| Date | Suite | Passed | Failed | Not run | Notes |
|---|---|---|---|---|---|
| 2026-10-16 | All | 0 | 0 | All | No code yet |
