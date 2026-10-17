# PRD: AutoM8X Buyer Agreement Agent (v1)

Version 0.1, 2026-10-16. Status: draft, not approved.

Built on the Stage 0 defaults, because Q1 to Q7 are not answered yet (STAGE0_QUESTIONS.md). Decisions are in DECISIONS.md.

Tags: [Lawyer] a lawyer should review. [Unverified] not confirmed yet. [Depends on Qn] changes with your Stage 0 answer.

We are not lawyers. This file is not legal advice. Every [Lawyer] point is collected in section 13.

---

## 1. Problem

Since August 17, 2024, agents need a written agreement with a buyer before touring a home with them (an MLS rule; your plan cites the NC Real Estate Commission bulletin on it). New buyer leads often go quiet when asked to sign, and busy agents reply late, chase by hand, or tour with nothing signed. That costs agents leads, time spent chasing, and the risk of breaking their own broker's rules.

**Who has it:** solo North Carolina agents and teams of 5 or fewer (Charlotte, Raleigh, Durham, Greensboro, Wilmington) who get buyer leads online (website forms, Zillow, Realtor.com, ads) and use an e-sign tool.

**What it costs them:** we have no numbers yet. Your 10 interviews and each pilot's 30-day baseline will give them: share of leads who sign before a tour, time to first reply, tours with nothing signed. Do not quote numbers to agents until we have real ones.

## 2. Users

| User | Who | Wants | Does in v1 | Sees |
|---|---|---|---|---|
| Agent | NC licensed broker, solo or team lead | Fast replies, a signed agreement before every tour, less chasing | Approves templates once, confirms the form checklist, presses Send on agreements, answers legal questions, acts on alerts | Alert emails and texts, morning list, weekly summary |
| Buyer | A person who filled a form or wrote in about buying a home | A quick answer, a clear next step, no pressure, an easy way out | Books a consult, signs in the agent's e-sign tool, replies, can STOP | Approved messages in the agent's name, the e-sign tool's own emails |
| Operator (you) | Runs AutoM8X and sets up each agent | Fast setup, early warning of problems, one switch to stop everything | Configures agents, watches health, fixes problems, runs tests | Operator page, daily summary, error alerts |

## 3. Goals and non-goals

**Goals**
- **G-1.** Every new buyer lead gets a first reply within 60 seconds (email; text when allowed).
- **G-2.** More buyers sign before their first tour than in the agent's baseline.
- **G-3.** Every tour we can see, booked for an unsigned buyer, raises an alert before it happens.
- **G-4.** Every hard rule holds, and we can prove it with tests and the audit log.
- **G-5.** A new agent is set up in about a week with config changes only, no code changes.

**Non-goals for v1**
- **NG-1.** Writing, editing, filling or checking agreements.
- **NG-2.** Answering buyer questions beyond approved templates. No chatbot.
- **NG-3.** An agent login or dashboard.
- **NG-4.** Teams with lead routing between members. States other than NC.
- **NG-5.** Old-lead reactivation. Seller and rental leads.
- **NG-6.** CRM integrations (Follow Up Boss and others). Reading the agent's mailbox.
- **NG-7.** Languages other than English.
- **NG-8.** Sending agreements without the agent pressing Send. [Depends on Q4]
- **NG-9.** Single-home touring agreements.
- **NG-10.** Billing and invoicing agents.
- **NG-11.** Voice AI, website chat widgets.
- **NG-12.** Sending buyer email from Outlook or Microsoft 365. v1 sends from Gmail and Google Workspace only. If your first pilot agent uses Outlook, this moves into v1.

## 4. User stories

Each story has acceptance criteria (a, b, c...). Each criterion is a yes or no check.

**US-1. Instant reply.** As an agent, I want every new buyer lead to get my approved reply within a minute, so I don't lose them while I'm busy.
- a. The email reply arrives within 60 seconds of the lead reaching us.
- b. If texting is allowed and it is inside the buyer's window, the text arrives within 60 seconds. Otherwise it waits for the window to open.
- c. The reply contains the approved explainer and a booking link.
- d. The reply and its trigger are in the audit log.

**US-2. Approve once, nothing else goes out.** As an agent, I want to approve every message before go-live and know nothing else is sent in my name.
- a. A template version that is not approved never sends.
- b. Each approval stores who, when, how, and which version.
- c. Editing a template creates a new version that needs approval.

**US-3. Prompt to send the agreement.** As an agent, I want a one-click prompt when a buyer books a consult, so I send my broker's form from my own e-sign tool quickly.
- a. The prompt arrives within 60 seconds of the booking.
- b. DocuSign agents: the link opens a draft from my own template, addressed to the buyer, with nothing else filled in.
- c. Other tools: the prompt shows the buyer's name and email and an "I sent it" button.
- d. The system never fills any agreement field.

**US-4. Chase until signed.** As an agent, I want reminders to go out until the buyer signs, then stop.
- a. Reminders follow my schedule and only go out inside the buyer's window.
- b. No reminder goes out more than 60 seconds after we learn the buyer signed.
- c. No reminder ever goes out after STOP.
- d. After the last reminder, I get a "still unsigned, over to you" note.

**US-5. Tour alert.** As an agent, I want an alert as soon as a tour is booked for a buyer with nothing signed.
- a. Alert within 5 minutes of a ShowingTime email or a TOUR text, and within 15 minutes of a calendar event being created.
- b. The alert names the buyer, the time, the address if known, and the agreement status.
- c. The alert has a "Got it" button. Unacknowledged urgent alerts escalate (FR-42).

**US-6. Legal questions come to me.** As an agent, I want legal questions sent to me, never answered by the system.
- a. The buyer gets only the fixed holding reply.
- b. I get the buyer's exact words within 60 seconds.
- c. Reminders to that buyer pause until I resume them.

**US-7. Ready to tour.** As an agent, I want to know the moment a buyer is fully signed, so I can book tours.
- a. "Ready to tour" alert within 60 seconds of the e-sign tool reporting completion.

**US-8. Morning list.** As an agent, I want one short list each morning of unsigned buyers and today's known tours.
- a. Arrives at 7:30 my time, every day with at least one active lead.

**US-9. Check a buyer by text.** As an agent who books tours by text, I want to text "TOUR Jane Doe" and get the buyer's status at once.
- a. Reply within 60 seconds with signed, not signed, or "not found".
- b. If not signed, the reply offers NUDGE to send the buyer an approved reminder.

**US-10. Clear next step.** As a buyer, I want a fast reply that tells me what happens next and lets me book a call.
- a. First reply within 60 seconds with a booking link that works on a phone.

**US-11. STOP means stop.** As a buyer, I want STOP to end all messages at once.
- a. Within 60 seconds of STOP, nothing more is queued or sent on any channel.
- b. I get one confirmation text, and nothing after it.
- c. The opt-out is in the consent log with time and wording.

**US-12. A plain reason, and answers from a person.** As a buyer, I want a short, plain explanation of why I'm asked to sign, and my questions answered by the agent.
- a. The explainer is the agent's approved text, word for word.
- b. Any question about terms, money or obligations is answered by the agent, never by the system.

**US-13. Setup by config.** As the operator, I want to set up a new agent with config only.
- a. A new agent needs a config file, secrets, template approvals and a passing test lead. No code change.
- b. A config error blocks that agent's sending and alerts me. Other agents keep running.

**US-14. See health, stop fast.** As the operator, I want to see health at a glance and stop everything in one click.
- a. The operator page shows errors, overdue jobs, unmatched events and unacknowledged urgent alerts.
- b. Global pause and per-agent pause stop all buyer messages within 60 seconds.

**US-15. Explain any message.** As the operator, I want to answer "what did we send this buyer, and why" in under 2 minutes.
- a. A lead's timeline shows every message, state change and trigger, in order, with times.

## 5. Functional requirements

Every requirement is a yes or no check. Times are measured from the moment the event reaches our server.

**Intake**
- **FR-1.** A new lead from a configured buyer source (web form or forwarded lead email) creates a lead record within 30 seconds.
- **FR-2.** The lead record stores source, received time, contact details given, consent evidence, and a link to the raw payload.
- **FR-3.** A lead from a source not marked as a buyer source gets no messages and is logged as ignored.
- **FR-4.** A new inquiry from the same email or phone for the same agent within 30 days is attached to the existing lead. It creates no second lead and no second instant reply.
- **FR-5.** A lead marked as a tour request by its source config also creates a tour signal (FR-45 to FR-49).
- **FR-6.** A lead with no valid email and no textable US mobile gets no messages, is closed, and the agent gets M-38.

**Instant reply**
- **FR-7.** If the lead has an email and is not opted out, M-01 goes out within 60 seconds of lead creation.
- **FR-8.** If texting is allowed for the lead (FR-30), M-02 goes out within 60 seconds, or at the next window start if the buyer's window is closed.
- **FR-9.** The explainer inside any message is byte-for-byte the agent's approved version.
- **FR-10.** Every booking link in a message carries the lead's token.

**Booking**
- **FR-11.** A booking webhook for the consult moves the lead to Consult booked within 60 seconds and stores the time.
- **FR-12.** Bookings match leads in this order: lead token, then email, then phone. No match goes to the operator's unmatched list.
- **FR-13.** A reschedule updates the stored time. A cancellation before the agreement is sent moves the lead back to Contacted and sends M-07 once.
- **FR-14.** If no booking exists 24 hours after the first reply, M-05 goes out once (config: 0 to 2 nudges).

**Agreement**
- **FR-15.** When the send trigger fires (default: consult booked), the agent gets M-20 within 60 seconds.
- **FR-16.** For DocuSign agents, M-20 links to a draft envelope created from the agent's chosen template. The draft request sets only the recipient name, recipient email and role. It sets no document field.
- **FR-17.** For other e-sign tools, M-20 shows the buyer's name and email and an "I sent it" button.
- **FR-18.** The lead moves to Agreement sent on any of: a DocuSign "sent" webhook, a matched e-sign notice email, the agent's "I sent it" click, or the agent's SENT text.
- **FR-19.** If the agreement is not sent 4 business hours after M-20, the agent gets M-21 once. After that, the lead stays on the morning list until sent.
- **FR-20.** The lead moves to Signed when the e-sign tool reports all parties signed or the agent confirms SIGNED. Within 60 seconds all pending reminders are cancelled and the agent gets M-22.
- **FR-21.** If the buyer signed but the agent has not countersigned, reminders to the buyer stop and the agent gets M-23.
- **FR-22.** If the buyer declines or the envelope is voided, reminders stop and the agent gets M-24.
- **FR-23.** Each signed agreement gets an end date (signed date plus the agent's default term; the agent can correct it). The agent gets M-32 three days before and M-33 on the day. After the end date the lead counts as unsigned for tour checks.

**Reminders**
- **FR-24.** After Agreement sent, reminders follow the agent's schedule (default: 24, 72 and 168 hours after sending). Default maximum 3. Hard cap 5.
- **FR-25.** A reminder sends only if, at send time: the lead is in Agreement sent, is not opted out, is not paused, the buyer's window is open, and the count is below the maximum.
- **FR-26.** For DocuSign envelopes, the email part of a reminder is DocuSign's own resend, and we add M-08 if texting is allowed. For other tools, the reminder is M-08 (text) or M-09 (email). "Reply LINK" gets M-17 and alerts the agent to resend.
- **FR-27.** A reminder due outside the buyer's window moves to the next window start.
- **FR-28.** After the last reminder, the agent gets M-31 and no more reminders send.

**Buyer replies**
- **FR-29.** Every inbound buyer text and forwarded buyer email is matched to a lead and logged.
- **FR-30.** Texting is allowed for a lead only when all are true: a text consent record exists, the agent's texting registration is approved, the lawyer gate is set for that agent, the number is a valid US mobile, and the lead is not opted out.
- **FR-31.** A reply that is exactly an opt-out word (STOP, STOPALL, UNSUBSCRIBE, CANCEL, END, QUIT, REVOKE, OPTOUT, OPT OUT; any case, punctuation ignored) is an opt-out. This check runs before any AI. Every other wording is judged by the sorter (FR-33, FR-39).
- **FR-32.** On opt-out: all pending buyer jobs are cancelled, no buyer message on any channel sends again, one M-14 goes out if the opt-out came by text, the agent gets M-30, and the consent log is updated. All within 60 seconds.
- **FR-33.** Any other reply is sorted into exactly one label: stop, legal_question, wants_consult, wants_tour, other.
- **FR-34.** stop: same as FR-32.
- **FR-35.** legal_question: the buyer gets M-10 (at most once per 24 hours), the agent gets M-25 with the buyer's exact words within 60 seconds, and reminders pause until the agent resumes.
- **FR-36.** wants_consult: the buyer gets M-11.
- **FR-37.** wants_tour: if the lead is not signed, the buyer gets M-12 and a tour signal is created. If signed, the agent gets M-39.
- **FR-38.** other: the agent gets M-39. The buyer gets M-13 if the agent turned it on (at most once per 24 hours).
- **FR-39.** If sorting fails, takes over 10 seconds, or is refused, the label is "other". If that reply also contains any opt-out word anywhere, it is treated as an opt-out instead.

**Agent commands**
- **FR-40.** The agent can send SENT, SIGNED, TOUR, NUDGE, PAUSE, RESUME, LOST, ACK and HELP by text to the alerts number, or use the matching buttons in alert emails. Each gets a reply or confirmation within 60 seconds. Unknown commands get M-37.

**Alerts**
- **FR-41.** Every alert has an ID, a reason, the buyer, and buttons. A button opens a confirm page; opening a link alone changes nothing.
- **FR-42.** An urgent alert not acknowledged in 30 minutes is sent again (M-28). Not acknowledged in 60 minutes, it goes to the backup contact (M-29) if one is set. [Depends on Q7]
- **FR-43.** The morning list (M-34) goes out at 7:30 agent time and lists unsigned active buyers and today's and tomorrow's known tours.
- **FR-44.** Agent alerts outside the agent's alert hours (default 7:00 to 22:00) wait until 7:00, unless they are urgent and the tour starts within 12 hours.

**Tours**
- **FR-45.** A ShowingTime email forwarded to the agent's tour address becomes a tour signal (time, address, buyer name if present) within 2 minutes.
- **FR-46.** The agent's calendar link is read every 10 minutes. New or changed events in the next 14 days are checked against active leads.
- **FR-47.** A tour signal matched to a lead that is not Signed, or whose agreement ends before the tour, sends M-26 within 2 minutes of matching.
- **FR-48.** A tour-like signal that matches no lead, or matches more than one, sends M-27 once, listing up to 10 unsigned active buyers to pick from.
- **FR-49.** The TOUR command returns the buyer's status (M-36) and creates a tour signal.

**Setup and operations**
- **FR-50.** Each agent's config is validated on load. An invalid config blocks that agent's sending and sends you M-52. Other agents are unaffected.
- **FR-51.** Templates are versioned. Only approved versions send.
- **FR-52.** Go-live is blocked unless: all templates approved, form checklist confirmed, a test lead passed, alert contact confirmed.
- **FR-53.** Global pause and per-agent pause stop all buyer messages within 60 seconds. Held messages re-check every rule when unpaused.
- **FR-54.** The operator page shows: leads by state per agent, the last 50 messages, errors, unmatched events, overdue jobs, unacknowledged urgent alerts, pending approvals.
- **FR-55.** You get M-50 every day at 8:00 your time. [Depends on Q7]
- **FR-56.** Every outbound message, inbound event, state change, config change, approval and alert is written to the audit log with the actor and the trigger.
- **FR-57.** An agent in test mode can only message addresses and numbers on that agent's allowlist, and texts use Twilio test credentials.

## 6. Compliance requirements

Hard rules rewritten as checkable requirements. Each has tests in TEST_PLAN.md section 4.

- **CR-1 (Rule 1).** No code path can create, edit or fill agreement content. The only e-sign actions allowed are: read status, create a draft from the agent's template with recipient name and email only (DocuSign), get the agent's sending link, and resend. The AI module has no access to e-sign code or credentials.
- **CR-2 (Rule 2).** The system never sends a buyer any text that is not an approved template. A legal question gets only M-10, and the agent is alerted.
- **CR-3 (Rule 3).** The explainer is stored once per agent as an approved version and inserted word for word. No per-buyer changes.
- **CR-4 (Rule 4).** Go-live is blocked until the agent ticks the form checklist (definite end date, broker license number, termination clause, Fair Housing language, plus the broker-in-charge line) and we store the record. The system never reads, checks or comments on the form. [Lawyer]
- **CR-5 (Rule 5, who).** We message only people who asked: every lead comes from a buyer-source submission or an inbound message. No list imports. No old leads.
- **CR-6 (Rule 5, STOP).** An opt-out on any channel stops all buyer messages on all channels within 60 seconds and is logged.
- **CR-7 (Rule 5, consent log).** Every lead has consent events: source, time, basis, consent wording version (our forms), page and IP (our forms), channel permissions, and any revocation. Kept 5 years. [Lawyer]
- **CR-8.** Texts go out only with a text consent record (FR-30) and only inside the buyer's window.
- **CR-9 (Rule 6).** No template, page or sales material uses "compliant", "compliance", "guarantee", "ensures" or "makes you legal". Claims use "helps you follow your own process".
- **CR-10 (Rule 7).** No message sends unless the agent approved its exact current version. Approval records keep version, date, method and approver.
- **CR-11 (Rule 8).** No government ID numbers, card numbers or bank details are stored. Buyer attachments are never stored. Long digit strings are masked before storage and before the AI sees text. No form asks for these.
- **CR-12.** The first text to a buyer names the agent and the firm and says "Reply STOP to opt out". [Lawyer]
- **CR-13.** Every buyer email shows the firm's postal address and a working unsubscribe link. [Lawyer]
- **CR-14.** Buyer texting for an agent stays off until their texting registration is approved and the lawyer gate is set. [Lawyer]
- **CR-15.** The audit log cannot be edited or deleted by the app.
- **CR-16.** Agent alerts carry only what the agent needs: buyer name, contact, status, and the buyer's message when relevant.

## 7. Message templates

Every message the system can send. Starter wording is written at CP1 and CP7 and needs the approvals shown. No message sends unless its current version is approved (CR-10).

| ID | Message | To | Channel | Fires when | Approved by |
|---|---|---|---|---|---|
| M-01 | Instant reply | Buyer | Email | New lead with an email | Agent |
| M-02 | Instant reply | Buyer | Text | New lead, texting allowed, window open | Agent |
| M-03 | Explainer, long (fixed block) | Buyer | Inside M-01 | Always in M-01 | Agent; starter reviewed by lawyer |
| M-04 | Explainer, short (fixed block) | Buyer | Inside M-02 | Always in M-02 | Agent; starter reviewed by lawyer |
| M-05 | Booking nudge | Buyer | Email or text | 24 h after first reply, no booking | Agent |
| M-06 | Consult booked, what's next | Buyer | Email or text | Booking created | Agent |
| M-07 | Rebook | Buyer | Email or text | Booking cancelled before agreement sent (once) | Agent |
| M-08 | Agreement reminder | Buyer | Text | Reminder due | Agent |
| M-09 | Agreement reminder | Buyer | Email | Reminder due (non-DocuSign, or no texting) | Agent |
| M-10 | Legal question holding reply | Buyer | Same as question | legal_question (max once per 24 h) | Agent; [Lawyer] |
| M-11 | Booking link reply | Buyer | Same as question | wants_consult | Agent |
| M-12 | Tour request, sign first | Buyer | Same as question | wants_tour, unsigned | Agent |
| M-13 | Acknowledgment | Buyer | Same as question | other (optional, max once per 24 h) | Agent |
| M-14 | Opt-out confirmation | Buyer | Text | STOP by text (once) | Agent; [Lawyer] |
| M-15 | HELP reply | Buyer | Text | HELP by text | Agent |
| M-16 | Signed, thank you | Buyer | Email or text | Signed | Agent |
| M-17 | Resend acknowledgment | Buyer | Same as request | LINK | Agent |
| M-18 | Unsubscribe page | Buyer | Web page | Unsubscribe link opened | Agent |
| M-20 | Send the agreement | Agent | Email, text | Send trigger fires | Agent |
| M-21 | Send reminder | Agent | Email, text | 4 business hours, not sent | Agent |
| M-22 | Ready to tour | Agent | Email, text | Signed | Agent |
| M-23 | Countersign needed | Agent | Email, text | Buyer signed, agent not | Agent |
| M-24 | Declined or voided | Agent | Email, text | Declined or voided | Agent |
| M-25 | Legal question from buyer | Agent | Email, text | legal_question | Agent |
| M-26 | URGENT: tour booked, nothing signed | Agent | Text, email, optional call | Matched tour signal, unsigned | Agent |
| M-27 | Who is this tour for? | Agent | Email, text | Unmatched tour signal | Agent |
| M-28 | Urgent alert, second notice | Agent | Text, email | Urgent alert unacknowledged 30 min | Agent |
| M-29 | Urgent alert to backup | Backup person | Text, email | Unacknowledged 60 min | Agent; backup agrees to receive |
| M-30 | Buyer opted out | Agent | Email | Opt-out | Agent |
| M-31 | Reminders used up | Agent | Email | Last reminder sent, still unsigned | Agent |
| M-32 | Agreement ends in 3 days | Agent | Email | End date minus 3 days | Agent |
| M-33 | Agreement ended | Agent | Email | End date | Agent |
| M-34 | Morning list | Agent | Email | 7:30 agent time | Agent |
| M-35 | Weekly summary | Agent | Email | Monday 8:00 agent time | Agent |
| M-36 | TOUR status reply | Agent | Text or email | TOUR command | Agent |
| M-37 | Command help | Agent | Text | Unknown command or HELP from agent | Agent |
| M-38 | Lead can't be contacted | Agent | Email | No usable contact details | Agent |
| M-39 | Buyer message forwarded | Agent | Email, text | other, or wants_tour when signed | Agent |
| M-40 | Reconnect needed | Agent | Email | Google or DocuSign access revoked or expired | Agent |
| M-50 | Daily operator summary | You | Email | 8:00 your time | You |
| M-51 | Error alert | You | Email | Send failed or unknown; an integration down 30 min | You |
| M-52 | Config invalid | You | Email | Config validation failed | You |

Agent alerts go by email until AutoM8X's alerts number is registered (D-07). [Depends on Q5]

## 8. Data we store

| ID | Data | Why | How long |
|---|---|---|---|
| DS-1 | Agent profile and config | Run the service | Until offboarding plus 90 days |
| DS-2 | Agent access tokens (Google send, DocuSign), encrypted | Send email as the agent, read agreement status | Until revoked or offboarding |
| DS-3 | Lead contact data (name, email, phone, source, zip if given) | Message and match the buyer | 12 months after last activity [Lawyer] |
| DS-4 | Consent events (section 8.2) | Prove permission | 5 years after last message [Lawyer] |
| DS-5 | Suppression list (hashed email or phone plus agent) | Keep honoring STOP after lead data is deleted | While the service runs [Lawyer] |
| DS-6 | Message log: metadata | Audit, metrics | 5 years |
| DS-7 | Message log: text of messages | Audit, debugging | 12 months, then removed |
| DS-8 | Agreement status records (envelope ID, sent, signed, end date) | Reminders, tour checks, metrics | 12 months after last activity |
| DS-9 | Tour signals (time, address, source, match) | Alerts, metrics | 12 months |
| DS-10 | Raw inbound emails and webhook bodies | Debug parsers | 30 days |
| DS-11 | Sorter runs (masked input, label, model, prompt version) | Accuracy checks | 90 days |
| DS-12 | Template versions and approvals | Prove Rule 7 | 5 years |
| DS-13 | Form checklist confirmations | Prove Rule 4 reminder was done | 5 years |
| DS-14 | Audit log | Explain every action | 5 years |
| DS-15 | Operator login records | Security | 1 year |

**8.1 Never stored**
- **NS-1.** Government ID numbers (SSN, driver's license).
- **NS-2.** Card numbers, bank account or routing numbers.
- **NS-3.** Attachments buyers send (photos, PDFs, pre-approval letters).
- **NS-4.** Agreement documents. We never download them.
- **NS-5.** Agents' passwords.

**8.2 Consent log**

One append-only event per change. Fields:
- **CL-1.** Lead ID and agent ID.
- **CL-2.** Channel: email or text.
- **CL-3.** Basis: own_form, inbound_text, booking_checkbox, portal_inquiry, lawyer_approved_portal.
- **CL-4.** Time captured (UTC).
- **CL-5.** Source detail: form URL, portal lead ID, or inbound message ID.
- **CL-6.** Consent wording version shown (our forms and booking page only).
- **CL-7.** IP address and browser (our forms only).
- **CL-8.** Link to the raw evidence (kept 30 days; the parsed fields above are kept 5 years).
- **CL-9.** Revocation: time, channel, method (keyword, AI label, unsubscribe link, agent), and the message ID.

## 9. Failure cases

| ID | Failure | What the system does |
|---|---|---|
| FC-1 | E-sign tool API is down | Retry with backoff for 2 hours. The agent still gets M-20, with "send from your tool" fallback text. Status falls back to forwarded emails and agent commands. You get M-51 after 30 minutes. |
| FC-2 | A text fails to deliver | Mark it failed. Do not resend that text. Send that message by email if not already sent. After 2 failures in a row, texting stops for that lead and the morning list says so. |
| FC-3 | Email send fails | Retry 3 times over 10 minutes. If access was revoked: pause email for that agent, send M-40 and M-51. |
| FC-4 | Duplicate webhook | Ignored by its event key and logged as a duplicate. |
| FC-5 | Buyer signs after a reminder is queued | The reminder re-checks state right before sending and is skipped. Logged as "skipped: signed". |
| FC-6 | Tour booked at 11pm | If the tour starts within 12 hours, the urgent alert goes now. Otherwise it waits for 7:00 agent time. Buyer messages wait for the buyer's window. |
| FC-7 | Buyer in another time zone | The buyer's window uses their time zone (address, else area code, else Eastern). |
| FC-8 | Agent never responds to an alert | Second notice at 30 minutes, backup at 60 minutes, listed in your next daily summary. No more automatic escalation. |
| FC-9 | Sorter is down or slow | Label "other": the agent gets the message. Opt-out words still work without AI (FR-39). You get M-51 after 5 failures in a row. |
| FC-10 | Reply from an unknown sender | Logged as unmatched. No reply. Listed for you. |
| FC-11 | Lead email can't be parsed (format changed) | Raw email kept 30 days, no message sent, you get M-51. The agent already has the original lead email. |
| FC-12 | Calendar link unreachable | Retry every 10 minutes. After 1 hour, you and the agent are told calendar tour checks are paused. The morning list says so. |
| FC-13 | Forwarding stops working (no ShowingTime or e-sign emails) | The operator page shows "last email received" per address. Over 14 days with active leads means you check the filter. |
| FC-14 | Google or DocuSign access expires | That feature pauses for the agent. M-40 to the agent, M-51 to you. Manual commands still work. |
| FC-15 | Texting registration rejected or suspended | Texting off for that agent, email only, you get M-51. |
| FC-16 | Database down | Webhooks answer "try again later" so providers retry. When it returns, each event is processed once. |
| FC-17 | Crash in the middle of a send | The message is marked "unknown" and not resent. You get M-51 and decide. |
| FC-18 | STOP arrives during a send | One message may already be in flight. Nothing after the opt-out is saved. Logged. |
| FC-19 | Agent config invalid after an edit | That agent's sending stops. M-52 to you. Others unaffected. |
| FC-20 | Buyer opted out, then books a consult | Booking recorded, agent told. No automatic buyer messages. The agent follows up personally. |
| FC-21 | Agent sends an unknown command | M-37 help reply. |
| FC-22 | "Signed" arrives before "sent" | The lead moves to Signed. A later "sent" is ignored. |
| FC-23 | Tour signal for a date in the past | Logged, no alert. |
| FC-24 | Same buyer is a lead for two agents | Two separate leads. Each agent's messages, consent and STOP are separate. |
| FC-25 | Agent paused or leaves mid-flow | Messages are held. On offboarding, data follows the retention table. |
| FC-26 | Daylight saving change | All times stored in UTC. Windows use the time zone database. Tested (TP-U-RM-05). |

## 10. Success metrics

| ID | Metric | Definition | Target | Source |
|---|---|---|---|---|
| SM-1 | Signed before first tour | Of leads with a known tour, the share signed before the first tour started | At least 20 points above baseline | Agreement records, tour signals |
| SM-2 | Time to first reply | Median and 95th percentile, lead received to first message sent | Median under 1 min, 95th under 5 min | Message log |
| SM-3 | Tours without a signature | Known tours where the buyer was unsigned at tour time | 0 without an alert; fewer than baseline overall | Tour signals, agent confirmation |
| SM-4 | Alerts acted on | Share of urgent alerts acknowledged within 30 minutes | 80% or more | Alerts |
| SM-5 | Lead to consult | Share of leads that book a consult within 14 days | Above baseline | Bookings |
| SM-6 | Consult to sent | Share of consults where the agreement was sent within 1 day | 80% or more | Agreement records |
| SM-7 | Sent to signed | Share signed within 7 days of sending; median time to sign | Above baseline | Agreement records |
| SM-8 | Opt-out rate | Opt-outs divided by buyers messaged | Under 5% | Consent log |
| SM-9 | Sorter safety | Misrouted stop or legal messages in the weekly sample | 0 | Sorter runs, weekly review |
| SM-10 | Send errors | Failed or unknown sends divided by all sends | Under 2% | Message log |

Targets are starting guesses. VERIFY.md section 5 says what counts as "it worked".

## 11. Open questions

Questions OQ-1 to OQ-9 are copies of the Stage 0 and interview questions (STAGE0_QUESTIONS.md).

- **OQ-1.** Q1: your level.
- **OQ-2.** Q2: time and budget.
- **OQ-3.** Q3: stack.
- **OQ-4.** Q4: who presses Send on the agreement.
- **OQ-5.** Q5: texting setup and account ownership.
- **OQ-6.** Q6: your test phone.
- **OQ-7.** Q7: alert backup and your hours.
- **OQ-8.** I1: which e-sign tool agents use, and which blanks they fill per buyer.
- **OQ-9.** I2: how agents book showings, plus a ShowingTime sample email.
- **OQ-10.** Who is your lawyer, and when can they review the items in section 13? Texting cannot go live without it.
- **OQ-11.** Which lead source will the first pilot use? The parser for it is built at CP9.
- **OQ-12.** Does the first pilot agent use Gmail or Outlook? Outlook moves NG-12 into v1.
- **OQ-13.** Which DocuSign plan qualifies for going live with an integration, and what does it cost? DocuSign requires a paid production account (no trial) to go live. [Unverified] which plan.
- **OQ-14.** Does Cal.com's free plan include webhooks? [Unverified]
- **OQ-15.** Who pays texting costs: inside your monthly fee, or passed through?

## 12. Risks

| ID | Risk | Likelihood | Impact | What we do |
|---|---|---|---|---|
| R-1 | Texting registration slow or rejected | High | Medium | Email first. Start registration on day 6. |
| R-2 | Lawyer says portal leads can't be texted | Medium | Medium | Email first. Consent box on the booking page. |
| R-3 | Tour signals miss tours (text bookings, no buyer names) | High | High | TOUR command, morning list, "we flag what we can see" in all sales talk. |
| R-4 | Dotloop and SkySlope agents need manual steps | High | Medium | Forwarded notice emails plus one-click "I sent it" and "Signed". |
| R-5 | Agent doesn't press Send | Medium | High | Re-prompt, morning list. Measured by SM-6. |
| R-6 | Google app review takes weeks | Medium | Medium | Submit at CP0. Demo doesn't need it (D-27). |
| R-7 | DocuSign go-live needs a paid account | High | Low | Buy the cheapest plan that qualifies when the first DocuSign agent signs. |
| R-8 | Agent's CRM also auto-replies, buyers get two replies | Medium | Medium | Setup checklist turns off the overlap (VERIFY GL-6). |
| R-9 | Sorter mislabels a legal question | Low | High | 30-reply test with zero-miss bar for legal and stop. Unknown goes to the agent. |
| R-10 | Leak of buyer data or tokens | Low | High | Encryption, send-only access, 2FA on the operator page, secrets outside git. |
| R-11 | Build takes longer than 10 days | High | Medium | Demo cut in CHECKPOINTS.md; re-estimate after CP1. |
| R-12 | Agent blames us for a tour that happened unsigned | Medium | High | Pilot terms: "helps you follow your own process"; the agent is responsible. [Lawyer] |
| R-13 | You are asleep during NC hours | Medium | Medium | Automatic alerts, one-click pause, agent can text PAUSE. [Depends on Q7] |
| R-14 | Zillow changes its email format | Medium | Medium | Parser tests on saved samples; failed parses alert you. |
| R-15 | Brokerage blocks email forwarding | Medium | Medium | Ask early in setup. Fall back to the agent's commands and the unsubscribe link. |
| R-16 | Brokerage disables the private calendar link | Medium | Medium | Ask early. Fall back to ShowingTime emails and TOUR. |
| R-17 | Carriers filter texts with shortened links | Medium | Medium | Full links on the agent's or our domain. No public link shorteners. |

## 13. Lawyer review list

| ID | Item | Where it appears |
|---|---|---|
| L-1 | Can we text Zillow and Realtor.com leads under the agent's registration, given consent was collected on the portal's form? | A12, D-10, FR-30 |
| L-2 | Text-consent wording on the agent's own web form and on the booking page | CL-6, FR-30 |
| L-3 | Quiet hours and allowed days (9:00 to 20:00 buyer time, every day) | D-11, FR-27 |
| L-4 | Opt-out handling: exact words, AI-judged wording, both-channel scope, confirmation wording (M-14) | FR-31, FR-32, CR-6 |
| L-5 | Do replies to leads count as advertising under NC rules (firm name needed)? | A7, CR-12 |
| L-6 | Starter explainer wording (M-03, M-04) | A8 |
| L-7 | Form checklist wording (4 NC terms plus broker-in-charge line) | A22, CR-4 |
| L-8 | Is a DocuSign draft addressed to the buyer (name and email only) consistent with "never edits the agreement"? | D-03, FR-16 |
| L-9 | Are buyer emails "commercial" under CAN-SPAM; address and unsubscribe needs | CR-13 |
| L-10 | Retention periods | Section 8 |
| L-11 | Pilot terms with agents: roles, data handling, limits of liability, no promise of compliance | VERIFY GL-1 |
| L-12 | Sales claims and the "helps you follow your own process" wording | CR-9 |
| L-13 | Legal question holding reply (M-10) | FR-35 |
| L-14 | Automated phone calls to agents for urgent alerts | A11 |

## 14. Glossary

- **Lead:** one buyer who asked one agent about buying.
- **Consult:** the first call or meeting between agent and buyer.
- **Agreement:** the broker's written buyer agreement, in the agent's e-sign tool.
- **Tour:** visiting a home with the agent, in person or live video. Open houses are not tours here.
- **Tour signal:** anything that tells us a tour is booked or wanted.
- **Window:** the hours when we may text or remind a buyer.
- **10DLC:** the US registration for business texting from normal 10-digit numbers.
- **Opt-out:** a buyer's request to stop messages (STOP, unsubscribe, or plain words).
