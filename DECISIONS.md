# Decisions Log

Running list. Newest entries go at the bottom. Never delete an entry: mark it "Changed" and add a new one.

Each entry: decision, why, date, what we rejected, status.
- Status "Default": my pick, waiting on your answer to the named Stage 0 question.
- Status "Decided": you set it, or you approved it.
- Status "Changed by D-xx": replaced by a later entry.

---

### D-00. Draft all stage files at once, before Stage 0 answers
- Date: 2026-10-16
- Status: Decided (your request: "create .mds for all").
- Why: you wanted every file now. They are drafts built on the Stage 0 defaults. Anything that changes with your answers is tagged [Depends on Qn].
- Rejected: one stage at a time with an "approved" gate (your original process; we can go back to it for revisions).

### D-01. The core is one small Python app, not n8n or Make
- Date: 2026-10-16
- Status: Default. Waiting on Q1 to Q3.
- Decision: FastAPI web app, a background worker, one Postgres database.
- Why: (1) the hard rules must be automated tests, and code gets real tests; (2) one codebase plus one config record per agent, instead of copied flows that drift; (3) I can run the tests here and show you the output; (4) n8n's docs say using it as a hidden backend is covered on paid plans and say nothing clear about the free self-hosted version, so it is not free for this.
- Rejected: n8n only (hard to test, per-agent copies drift, license unclear for many clients' logins). Make (same testing problem, priced per operation). Python plus n8n for email parsing (two systems to run; Postmark already turns emails into JSON).

### D-02. The agent presses Send on the agreement. The system never fills, edits or checks agreement content
- Date: 2026-10-16
- Status: Default. Waiting on Q4.
- Why: blanks that change per buyer are the agent's job (Hard Rule 1). The same flow works for every e-sign tool. Dotloop and SkySlope don't let us send anyway.
- Rejected: automatic sending (crosses Rule 1 when the form has blanks; impossible on Dotloop and SkySlope).

### D-03. DocuSign agents get a draft from their own template, addressed to the buyer
- Date: 2026-10-16
- Status: Default. [Lawyer] see PRD L-8.
- Decision: we create a draft envelope from the agent's own DocuSign template. We set only the buyer's name and email as the recipient. The agent opens it, fills any blanks, and presses Send.
- Why: one click for the agent. DocuSign sends status webhooks for envelopes created through the API on all plans, so we learn "sent" and "signed" within seconds. If the agent sends from scratch instead, we would have to poll (DocuSign allows one status check per envelope per 15 minutes) or read emails.
- Rejected: polling only (slow, rate limits). Embedded signing links that we text to the buyer (we would control the signing session, which is more than we want to touch).

### D-04. Dotloop, SkySlope and other tools: the agent sends, we detect
- Date: 2026-10-16
- Status: Default.
- Decision: we learn "sent" and "signed" from the tool's notice emails forwarded to us, or from the agent's click ("I sent it", "Signed") or text (SENT, SIGNED).
- Why: Dotloop's public API has no signing functions and no signature status. SkySlope's API is partner-only.
- Rejected: screen scraping (fragile and likely against their terms).

### D-05. Email first; texts to buyers wait for registration and a lawyer
- Date: 2026-10-16
- Status: Decided (email-first is in your prompt; the lawyer gate is in your plan).
- Decision: buyer texts for an agent start only when that agent's texting registration is approved and a lawyer has reviewed the texting setup.

### D-06. Twilio: one AutoM8X account, a sub-account per agent, each agent registered as their own sender
- Date: 2026-10-16
- Status: Default. Waiting on Q5.
- Why: texts go out in the agent's voice. Sub-accounts keep each agent's billing and numbers apart and can be shut off one at a time.
- Rejected: one shared AutoM8X sender for all agents' buyer texts ([Unverified] carriers expect the business named in the text to be the sender). Each agent owning a Twilio account (more work for the agent; easy to switch to if you prefer).

### D-07. Agent alerts come from one AutoM8X alerts number once registered; email until then
- Date: 2026-10-16
- Status: Default. Waiting on Q5.
- Decision: one alerts number under AutoM8X's own texting registration. Agents save it once and send commands (TOUR, SIGNED) to it. Before that: email (the agent marks it VIP), plus an optional automated call for urgent alerts.
- Why: one place for alerts and commands, separate from the buyer number.
- Rejected: alerts from the agent's own buyer number (confusing; mixes uses in one registration). This is the fallback if AutoM8X cannot register.

### D-08. Buyers only ever get approved templates
- Date: 2026-10-16
- Status: Default (follows Hard Rules 2, 3 and 7).
- Decision: every buyer message is an approved template with fill-in fields. The AI never writes text a buyer sees.
- Rejected: AI-written replies "in the agent's voice" (we could not prove Rules 2 and 3).

### D-09. Reply sorter: fixed STOP rules first, then Claude with five labels
- Date: 2026-10-16
- Status: Changed by D-31 (Gemini instead of Claude).
- Decision: labels are stop, legal_question, wants_consult, wants_tour, other. Default model `claude-opus-5` at low effort with a fixed output schema. Option: `claude-haiku-4-5` if it passes the 30-reply test. No prompt caching.
- Why: "wants to book" is split because tour intent must trigger the tour alert. Opus 5 costs about $1 a month per agent at our volume. Caching doesn't help: calls are minutes or hours apart.
- Rejected: Groq (your plan names Claude; switching later is a config change). AI-only STOP detection (STOP must work when the AI is down).

### D-10. Texting needs a consent record per buyer; portal leads start on email
- Date: 2026-10-16
- Status: Default. [Lawyer] see PRD L-1.

### D-11. Quiet hours: 9:00 to 20:00 in the buyer's time zone
- Date: 2026-10-16
- Status: Default. [Lawyer] see PRD L-3.
- Decision: buyer texts and all reminders go out only in that window. Instant-reply emails can go any time. Hard limits in code: never before 8:00 or after 21:00, whatever the config says.
- Why: federal rules use 8am to 9pm for telephone solicitations and some states are stricter. 9 to 8 sits inside both. A lawyer should confirm.

### D-12. We never read the agent's mailbox
- Date: 2026-10-16
- Status: Default.
- Decision: Gmail access is "send only". Inbound email reaches us by forwarding to addresses we run. Buyer email replies reach us through a Reply-To plus address (for example jane+buyers@gmail.com) and a Gmail filter. Calendar comes from the private iCal link.
- Why: less access, easy to revoke. Gmail read access needs a yearly paid security assessment; send-only needs an app review only.
- Rejected: Gmail read access. Full Google Calendar API access (more review, more access than we need). Microsoft 365 sending in v1 (added in v2 if a pilot agent uses Outlook).

### D-13. Postmark for inbound email and for alerts
- Date: 2026-10-16
- Status: Default.
- Decision: Postmark receives all forwarded email (Pro plan, about $16.50 a month per third-party pricing pages [Unverified]) and sends alerts to agents and you from an AutoM8X domain. Buyer emails go from the agent's own Gmail.
- Rejected: Cloudflare Email Workers (free, but we would parse raw email ourselves; kept as a fallback).

### D-14. Booking: Cal.com by default, Calendly if the agent already pays for it
- Date: 2026-10-16
- Status: Default. [Unverified] whether Cal.com's free plan includes webhooks.
- Decision: each booking link carries a lead token (Cal.com `metadata[lead]`, Calendly `utm_content`) so bookings match the right lead.
- Why: Cal.com passes `metadata[key]` link values to its webhook. Calendly webhooks need its paid Standard plan and return UTM values in the webhook.

### D-15. Timers live in a Postgres jobs table; a worker checks every 30 seconds
- Date: 2026-10-16
- Status: Default.
- Decision: every timed action (reminder, nudge, escalation) is a job row. Right before sending, the job re-checks the lead's current state.
- Rejected: n8n Wait nodes. Celery with Redis (one more service to run). One cron entry per reminder.

### D-16. At-most-once sending
- Date: 2026-10-16
- Status: Default.
- Decision: every outbound message has a unique key. If we cannot tell whether a message went out, we do not resend; we alert you.
- Why: your rule that a retried webhook must never send two texts. A missed reminder hurts less than a double text.

### D-17. Hosting on Railway, US region
- Date: 2026-10-16
- Status: Default.
- Decision: one web service, one worker, one Postgres database.
- Why: you planned Railway for other projects. The Hobby plan is $5 a month including $5 of usage (third-party pricing pages [Unverified]).
- Rejected: Render or Fly.io (fine, no strong reason to switch). Serverless functions (timers and long jobs are awkward).

### D-18. No agent dashboard in v1; an operator page for you
- Date: 2026-10-16
- Status: Default.

### D-19. Five tour signals plus a morning list
- Date: 2026-10-16
- Status: Default.
- Decision: ShowingTime emails, calendar events, replies sorted as wants_tour, tour-request leads, the agent's TOUR text. Plus a daily list of unsigned buyers.

### D-20. Agreement end date from the agent's default term
- Date: 2026-10-16
- Status: Default.
- Decision: end date = signed date plus the agent's default term (config), correctable per buyer. After it passes, the buyer counts as unsigned for tour checks.

### D-21. Reminder defaults
- Date: 2026-10-16
- Status: Default.
- Decision: 3 reminders, at 1, 3 and 7 days after the agreement is sent. Hard cap 5. At least 20 hours apart. One channel per reminder.

### D-22. Change to your flow: how a reminder "resends the link"
- Date: 2026-10-16
- Status: Default.
- Decision: for DocuSign, the reminder asks DocuSign to resend its own signing email, and we add a short text if texting is allowed. For other tools, the reminder tells the buyer where the agreement is, and "Reply LINK" asks the agent to resend.
- Why: when the agent sends from their own tool, we never hold a signing link.
- Rejected: generating our own signing links (we would control the signing session).

### D-23. A legal question pauses reminders until the agent resumes them
- Date: 2026-10-16
- Status: Default.
- Why: no "please sign" message right after "do I have to sign?".

### D-24. One booking nudge after 24 hours (new message, not in your flow)
- Date: 2026-10-16
- Status: Default.
- Decision: if no consult is booked 24 hours after the first reply, send one approved nudge. Config allows 0 to 2. Turn it off if the agent's CRM already follows up.

### D-25. v1 scope limits
- Date: 2026-10-16
- Status: Default.
- Decision: NC only; solo agents (team lead counts as the agent); new leads only; buyer sources only; English only; agreements that cover any home.

### D-26. Data retention defaults
- Date: 2026-10-16
- Status: Default. [Lawyer] see PRD L-10.
- Decision: consent, opt-outs, approvals and audit log kept 5 years. Lead contact data and message text kept 12 months after last activity. Raw inbound emails kept 30 days.

### D-27. Demo setup
- Date: 2026-10-16
- Status: Default.
- Decision: fake agent ("Demo Agent, Example Realty"), SAMPLE agreement, DocuSign developer sandbox, Cal.com test event, Twilio test credentials, a fast clock. Demo buyer emails come from an AutoM8X demo mailbox, not a real agent's Gmail.
- Why: no fake identity of a real person, no licensed forms in a video, no Google review needed for the demo.

### D-28. Spikes first; the tour alert is the riskiest checkpoint
- Date: 2026-10-16
- Status: Default.
- Decision: CP0 runs throwaway tests on the tour signals (calendar link timing, ShowingTime email contents), DocuSign, and the sorter before the real build. CP8 (tour alert) is marked riskiest.

### D-29. Tour matching confidence
- Date: 2026-10-16
- Status: Default.
- Decision: exact email, phone or lead token = high. Exact full name with only one active lead of that name = medium. Anything else = ask the agent "Who is this tour for?".

### D-30. Alert actions: one-click links that open a confirm page
- Date: 2026-10-16
- Status: Default.
- Decision: agents act by texting commands to the alerts number or by clicking links in alert emails. Every link opens a page with one button. Opening the link alone changes nothing.
- Why: email security scanners open links automatically.

### D-31. The reply sorter uses Gemini, not Claude
- Date: 2026-10-17
- Status: Decided (your instruction: "dont use anthropic key instead use gemini"). Replaces the model part of D-09; the labels, rules and schema in D-09 stay.
- Decision: default `gemini-3.1-flash-lite` ($0.25 in, $1.50 out per million tokens). Option `gemini-3.8-flash` ($0.75 in, $3.75 out until Dec 31, 2026, then $1.50 and $7.50) if flash-lite misses the TP-AI-01 bar. Structured JSON output with the RS-6 schema.
- Why: your choice. Both cost well under $1 a month per agent at our volume.
- Rule that comes with it: real buyer text only ever goes to a paid-tier (billing enabled) key. On the free tier, Google's terms say it may use inputs to improve products, human reviewers may read them, and you should not send personal information. The free tier is fine for spikes with the fake TP-AI-01 replies.
- Rejected: Claude (your instruction). Groq (not asked for).

### D-32. No opt-out phrase list; only the exact official words are fixed rules
- Date: 2026-10-17
- Status: Decided (your feedback: buyers won't always use exact words).
- Decision: the fixed rule fires only when the whole reply is one of STOP, STOPALL, UNSUBSCRIBE, CANCEL, END, QUIT, REVOKE, OPTOUT, OPT OUT. Every other wording ("stop texting me", "take me off your list", "we found another agent") is judged by Gemini, with possible_opt_out biased toward stopping. If Gemini is down, a reply containing stop, cancel, end or quit is still treated as an opt-out.
- Why: a phrase list can never cover every wording, and the model already catches these. The exact words stay because the FCC and carriers name them and they must work with no AI at all.
- Rejected: the RS-3 phrase list (redundant, false sense of coverage). AI-only opt-out detection (fails when the AI is down).
- [Lawyer] L-4 still applies.

### D-33. The database is Supabase (hosted Postgres), not Railway Postgres
- Date: 2026-10-17
- Status: Decided (your instruction). Changes the database part of D-17; the app and worker can still run on Railway.
- Decision: one Supabase project in a US region. Our tables live in a separate `app` schema, never in `public`, so Supabase's automatic web API can't reach buyer data. The app connects with the Session pooler connection string, not the Transaction pooler, because job claiming needs row locks.
- Why: your choice. Supabase is Postgres, so the design (row locks, unique keys, the append-only audit trigger) is unchanged.
- To check at connection time: [Unverified] IPv4 through the session pooler; free-plan pausing after inactivity and backup limits. A live pilot should use a paid plan with backups.
- Rejected: Railway Postgres (replaced by your choice). Supabase's auto-generated API and client keys (not needed; the app talks to the database directly).

### D-34. The current Supabase project (Sydney) is for development and tests only
- Date: 2026-10-17
- Status: Decided (your plan: use it to test, delete the test data, then create production).
- Decision: project `ubvueccnwiwgruarenxb` in ap-southeast-2 (Sydney) holds development data in schema `app` and automated test runs in schema `app_test`, which the tests drop and recreate each run. No real buyer data ever goes here. Before the first real agent goes live, create a new production project in US East (North Virginia), run the migrations there, and point production at it. Then delete this project.
- Why: Sydney breaks our "data stays in the US" assumption (A16, D-33) and adds a round trip to Australia on every query. Fine while all data is fake.
- Rejected: a second Supabase project for tests now (not needed while everything here is test data). Recreating in US East today (you chose to wait).
