# Stage 0: Questions and Assumptions

Version 1.1, 2026-10-16. Status: questions not answered yet. Every other file uses the defaults below.

How to answer: reply by ID, for example "Q3: a" or "Q6: default". "Default" is a fine answer to any question.

Tags used in all files:
- [Lawyer]: a lawyer should review this.
- [Unverified]: I am not sure. We check it in a spike or before go-live.
- [Depends on Qn]: this changes if your answer to Qn differs from my default.

## Changes since the chat version

1. A28 corrected. In chat I said your plan names Claude Haiku 4.5. It does not. Your plan only says "Claude API". New default: Claude Opus 5 at low effort. (Changed again on 2026-10-17: you chose Gemini. See D-31 and A28.)
2. A13 detail. Twilio's built-in STOP words are STOP, STOPALL, UNSUBSCRIBE, CANCEL, END, QUIT, REVOKE and OPTOUT. Twilio does not catch "OPT OUT" with a space, so our own check must.
3. A15 checked. Google rates "send email" access as sensitive: it needs Google's app review, but no paid audit. Reading Gmail is restricted: it adds a yearly paid security assessment. That part is no longer [Unverified].
4. A21 checked. Dotloop's public API has no way to send a document for signing and no signature status. SkySlope's API is only for approved partners. So for Dotloop and SkySlope agents, the agent sends, and we learn about it from forwarded emails or the agent's text.
5. A24 detail. ShowingTime lets an agent attach a buyer to a showing. If the agent does that, the buyer's name may appear in the emails. [Unverified] until we see real emails.
6. Q5 detail. Twilio lets "sole proprietor" senders (no tax ID) register only with a US or Canadian mobile number. A business outside the US can register as a standard brand.

## Questions

**Q1. Your level.** What can you build and fix on your own? My guess from your past projects on this laptop: comfortable with Python, FastAPI and APIs, some n8n. Decides code or no-code, and how much I explain versus build.
- Default: the guess above.
- Your answer:

**Q2. Time and budget.** Your plan gives about 10 build days (days 6 to 15). What monthly tool budget do you have for the demo?
- Default: 10 days, under $50 a month for the demo.
- Your answer:

**Q3. Stack.** I recommend one small Python app (FastAPI and Postgres) for the core, with no n8n or Make in v1. Why: your hard rules must be automated tests; one codebase plus one config record per agent; I can run the tests here and show you real output; and n8n is not free for this (its docs say hidden-backend use is covered on paid plans, and say nothing clear about the free self-hosted version).
- (a) Python core. My pick.
- (b) n8n only.
- (c) Python core, with n8n only for reading emails.
- Default: (a).
- Your answer:

**Q4. Who presses Send on the agreement in v1?** The form has blanks that change per buyer (names, end date, usually compensation). Filling them is the agent's job. If we fill them, that is very close to editing the agreement (Hard Rule 1).
- (a) The agent presses Send in their own tool. We prompt, detect "sent" and "signed", and chase. My pick.
- (b) We send automatically where the tool allows it and the form has no blanks beyond the buyer's name and email.
- (c) (a) by default, (b) per agent where possible.
- Default: (a). For DocuSign agents we prepare a draft from their own template so Send is one click (see D-03).
- Your answer:

**Q5. Texting setup.**
- (a) Is AutoM8X a registered business, and in which country?
- (b) Who owns the Twilio account and numbers: you (one account, a sub-account per agent) or each agent?
- Default: you own one account with a sub-account per agent. Each agent is registered as their own sender.
- Your answer:

**Q6. Your test phone.** Is it a US number?
- Default if not: you test email end to end yourself. Texts get tested with Twilio's test mode, then on a US phone later.
- Your answer:

**Q7. Alert backup and your hours.** If the agent ignores an urgent alert, who gets it next: a backup the agent names, you, or nobody? What time zone do you work in?
- Default: alert the agent again after 30 minutes, then their named backup at 60 minutes. You get a daily summary, not live alerts.
- Your answer:

## Two questions for your agent interviews

- **I1.** "Which e-sign tool do you use, and which blanks do you fill in for each buyer?"
- **I2.** "How do you book showings: ShowingTime, your calendar, or by text?" If ShowingTime, ask for one confirmation email with names blacked out.

## Assumptions

**Scope**
- **A1.** North Carolina only. Solo agents. On a team, the team lead is "the agent": one form, one calendar, one alert phone. NC-specific items (form checklist, quiet hours) live in config.
- **A2.** New leads only, from go-live on. We never message old leads.
- **A3.** Buyer leads only. We act only on sources the agent marks as buyer sources.
- **A4.** English only. A reply in another language goes straight to the agent.
- **A5.** No agent login or dashboard in v1. Agents get alerts and a weekly summary. You get an operator page.
- **A6.** The demo uses a clearly fake agent ("Demo Agent, Example Realty"), your own test lead, and a placeholder agreement marked SAMPLE. No real NC REALTORS form. [Unverified] whether a real one may be shown in a video.

**Messages and consent**
- **A7.** Every buyer message is an approved template with fill-ins (buyer name, agent name, firm, links). The AI never writes text a buyer sees. Every message names the agent and the firm. [Lawyer] NC ad rules may require the firm name; I don't know if lead replies count as ads.
- **A8.** We write a starter template pack. The explainer describes the agent's process and does not state the law. The agent edits and approves it. [Lawyer] Review the starter explainer once.
- **A9.** The agent approves the whole pack, with version numbers, by e-signing it or replying "approved". Any change needs a new approval before it can send.
- **A10.** Email first. Buyer texts start only after that agent's texting registration clears.
- **A11.** Until then, agent alerts go by email. The agent marks our alert address as VIP so it buzzes their phone. Optional per agent: an automated phone call for urgent alerts. [Unverified] that phone calls don't need the texting registration.
- **A12.** We text a buyer only with a consent record: the agent's own web form with text-consent wording, the buyer texting first, or a consent box on the booking page. Zillow and Realtor.com leads start on email only, unless a lawyer says those forms cover texts from the agent. [Lawyer]
- **A13.** STOP is caught by fixed rules before any AI runs: the message is one of STOP, STOPALL, UNSUBSCRIBE, CANCEL, END, QUIT, REVOKE, OPTOUT, OPT OUT. (Changed 2026-10-17, D-32: no phrase list.) Every other wording, like "stop texting me", "not interested" or "take me off your list", is judged by the AI. When unsure, we stop. STOP on one channel stops both. [Lawyer]
- **A14.** Buyer texts and all reminders go out only from 9am to 8pm in the buyer's time zone. Time zone: buyer's address, else phone area code, else Eastern. Instant-reply emails can go any time. The one STOP confirmation goes right away. [Lawyer]

**Access and data**
- **A15.** We never read the agent's mailbox. Lead emails, ShowingTime emails, e-sign notices and buyer email replies reach us by forwarding. We ask only to send email as the agent, plus a read-only calendar link. Checked: Google's "send" access needs an app review but no paid audit; Gmail read access needs a yearly paid assessment. [Unverified] Some brokerages block forwarding.
- **A16.** We never keep attachments buyers send (an ID photo, a pre-approval letter). We pass them to the agent and delete our copy. We mask long numbers in stored text (Hard Rule 8). All data stays in the US. [Unverified] how long Twilio keeps its own copy.

**Agreement**
- **A17.** The prompt to send the agreement fires when the consult is booked. Per-agent option: after the consult ends.
- **A18.** "Signed" means the e-sign tool says every party signed. Sources, in order: the tool's API, its "completed" email forwarded to us, the agent's SIGNED text or click. If the buyer signed but the agent hasn't, we tell the agent.
- **A19.** Agreements end. We store an end date from the agent's default term (for example 30 days), correctable per buyer. After it passes, the buyer counts as unsigned for tour alerts. The agent gets a warning 3 days before.
- **A20.** An agreement covers any home, not one address. Agents who use one-home touring agreements don't fit v1.
- **A21.** The demo uses DocuSign's free developer sandbox. Checked: Dotloop's public API cannot send for signing or report signatures; SkySlope's API is partner-only. Agents on those tools send themselves, and we detect it by email or their text.
- **A22.** At setup, the agent ticks a checklist of the 4 NC terms you listed, plus: "My broker-in-charge confirmed this form also meets my MLS and REALTOR rules, if I'm a member." We never check the form. [Lawyer] Review the checklist wording.

**Tours**
- **A23.** Tour signals in v1: ShowingTime emails, new events on the agent's calendar, a buyer reply sorted as "wants to see a home", a lead that arrives as a tour request (like Zillow "Request a tour"), and the agent texting "TOUR Jane Doe".
- **A24.** ShowingTime lets agents attach a buyer to a showing; if they do, the name may appear in the emails. If it doesn't, the alert can only say "Tour booked at 12 Oak St. These buyers are unsigned." [Unverified]
- **A25.** The agent also gets a morning list: "Unsigned buyers. Get a signature before you tour them." This covers tours we can't see.

**AI reply sorter**
- **A26.** Labels: stop, legal question, wants a consult, wants to see a home, other. Your "wants to book" is split in two, because "wants to see a home" must trigger the tour alert.
- **A27.** Legal question: the buyer gets the fixed "your agent will answer that" message, the agent gets an alert, and reminders pause until the agent resumes them.
- **A28.** (Changed 2026-10-17, D-31.) The sorter uses Gemini, not Claude. Default model: `gemini-3.1-flash-lite`. Option: `gemini-3.8-flash` if flash-lite misses the 30-reply test bar. Real buyer text goes only to a paid-tier key. The sorter sits behind one function, so a switch is a config change. It sees only the reply text with names and numbers masked. It cannot send anything or touch the e-sign tool (Hard Rule 1). If it fails or is unsure, the reply goes to the agent as "other".

**Operations**
- **A29.** No real texts to buyers until a lawyer reviews the texting setup. [Lawyer]
- **A30.** Sizing: up to 20 agents, up to 100 buyer leads per agent per month. Cost estimates use 40 leads per agent per month until your interviews give real numbers.
