# How Do I Know It Works

Version 0.1, 2026-10-16. Status: draft, not approved.

Built on the Stage 0 defaults. [Depends on Q5 to Q7] Numbers and thresholds are starting guesses. Set them with the agent before a pilot starts, never after.

## 1. Go-live checklist (one per agent)

Every row must be done before the agent switches from test to live. The system enforces GL-10, GL-11, GL-13 and GL-18 (FR-52).

| ID | Check | Owner | How to check | Done |
|---|---|---|---|---|
| GL-1 | Pilot terms signed: scope, fee, agent's responsibilities, data handling, "helps you follow your own process" | You and agent | Signed copy saved. [Lawyer] | [ ] |
| GL-2 | Agent config loaded and valid | You | Operator page shows "config valid" | [ ] |
| GL-3 | Gmail send access granted | Agent | A test email from the agent's address reached your inbox | [ ] |
| GL-4 | Reply routing works | Agent and you | Reply to the test email: it lands in the agent's inbox and shows in our timeline within 2 minutes | [ ] |
| GL-5 | Lead source connected | Agent and you | A test lead from the real source, or a forwarded sample, created a lead | [ ] |
| GL-6 | Overlapping auto-replies off | Agent | The CRM's auto-reply for this source is off, or the agent chose in writing to keep both | [ ] |
| GL-7 | Booking link works | You | A test booking matched the test lead | [ ] |
| GL-8 | E-sign connected | Agent | DocuSign: a test draft opened and sent. Other tools: a forwarded notice email was read correctly. The e-sign tool's own automatic reminders are off for this form, or the agent chose to keep them | [ ] |
| GL-9 | Broker's form loaded in the agent's tool | Agent | DocuSign template ID recorded, or the form's name noted | [ ] |
| GL-10 | Form checklist confirmed by the agent | Agent | Record shows the 4 NC terms and the broker-in-charge line, with date and method | [ ] |
| GL-11 | Every template approved | Agent | Approval records exist for every template that can send, at the current versions | [ ] |
| GL-12 | Starter explainer reviewed by a lawyer | You | Lawyer's note on file (once, covers all agents) | [ ] |
| GL-13 | Alert contact confirmed | Agent | The agent received a test alert and pressed "Got it" | [ ] |
| GL-14 | Backup contact set, or declined | Agent | Config shows a backup, or "none" by the agent's choice. [Depends on Q7] | [ ] |
| GL-15 | Tour sources tested | Agent and you | A test calendar event was detected. ShowingTime forwarding tested with a real or sample email | [ ] |
| GL-16 | TOUR command tested | Agent | The agent sent TOUR and got the status back | [ ] |
| GL-17 | Texting decision made | You | Registration approved and lawyer review done, or texting stays off (email only) | [ ] |
| GL-18 | Full test lead passed on this agent's setup | You | The TEST_PLAN.md section 7 script, all steps pass, results saved | [ ] |
| GL-19 | Baseline numbers captured | You and agent | PS-1 to PS-3 baseline filled in (section 5) | [ ] |
| GL-20 | Pause tested | You | Agent paused: a test lead got no message. Then unpaused. | [ ] |
| GL-21 | The agent knows how to stop it | Agent | The agent has your contact and knows the PAUSE command | [ ] |
| GL-22 | Switched to live | You | Audit log shows the change from test to live, by you, with the date | [ ] |

## 2. What to watch

### 2.1 First 24 hours

| ID | Number | Where | Good | Bad, and what to do |
|---|---|---|---|---|
| W24-1 | Leads in versus first replies sent | Operator page | Equal | A lead with no reply after 5 minutes: check it now |
| W24-2 | Median time to first reply | Daily summary | Under 1 minute | Over 5 minutes: worker or email problem |
| W24-3 | Failed or unknown sends | Health banner | 0 | Any: open each one now |
| W24-4 | Messages after an opt-out | Opt-out list and timelines | 0 | Any: shut off (SO-1) |
| W24-5 | Unmatched events | Unmatched list | 0 to 2, each explained | Unmatched bookings or e-sign events: fix matching before more leads arrive |
| W24-6 | The agent saw the alerts | Ask the agent | Yes | No: fix the alert channel today |

### 2.2 First week

| ID | Number | Where | Good | Bad, and what to do |
|---|---|---|---|---|
| W7-1 | Leads we saw versus leads in the agent's CRM | The agent's CRM | The same | Fewer: intake gap (forwarding or parser) |
| W7-2 | Lead to consult booked | Weekly review | At or above the agent's usual rate | Under half of usual: review reply and explainer wording with the agent |
| W7-3 | Prompt to agreement sent, median | Weekly review | Under 4 hours | Over 1 day: the agent isn't pressing Send; talk about timing |
| W7-4 | Sorter labels | Weekly sample (section 3, step 10) | Every stop and legal label correct | Any miss: sorter off, fix, rerun TP-AI-01 |
| W7-5 | Opt-out rate | Weekly review | Under 5% | Over 10%: pause reminders, review wording and spacing |
| W7-6 | Text delivery rate (once texting is on) | Twilio delivery status | Over 95% | Under 90%: registration or content problem; read the Twilio error codes |
| W7-7 | Tour signals received | Operator page | At least one in a week the agent toured | Zero while the agent toured: forwarding or calendar link broken |
| W7-8 | Urgent alerts acknowledged within 30 minutes | Alerts page | 80% or more | Under 50%: change the channel or add a backup |

### 2.3 First 30 days

| ID | Number | Where | Good | Bad, and what to do |
|---|---|---|---|---|
| W30-1 | Signed before first tour (PS-1) | Scorecard | 20 points above baseline | Under 5 points above: see section 5 |
| W30-2 | Seen tours without a signature | Scorecard | 0 without an alert | Any seen tour without an alert: fix before continuing |
| W30-3 | Reminders per signed buyer, average | Weekly review | 1 to 2 | Most need all 3, or opt-outs after reminder 2: spacing or wording problem |
| W30-4 | "Who is this tour for?" alerts | Alerts page | Falling week by week | Rising: ask the agent to attach buyers in ShowingTime and put buyer names in calendar events |
| W30-5 | Cost per agent | Twilio, Railway, Postmark and Gemini bills | Within the ARCHITECTURE.md section 20 estimate | Over 2 times the estimate: find the cause |
| W30-6 | The agent's view | Ask | Wants to keep it and pay | No: write down why |

## 3. Daily health check (about 5 minutes)

1. Open the operator page. Is the health banner green? If red, open each item.
2. Failed or unknown sends in the last 24 hours: is it 0? Open any you find.
3. Jobs overdue by more than 5 minutes: is it 0?
4. For each live agent: do yesterday's leads in equal first replies sent?
5. Any unacknowledged urgent alerts? Message the agent.
6. Unmatched events: resolve each one, or note why not.
7. Yesterday's opt-outs: open one timeline and confirm nothing was sent after it.
8. Integrations: tokens valid, calendar read in the last 15 minutes, last forwarded email per address not older than expected.
9. Write one line in the log: the date, and "OK" or the issue and what you did.
10. Mondays only: review 20 random sorted replies plus every stop and legal_question label from the week.

## 4. Weekly review

Fill one column per week. Definitions are in the right column.

| Number | Week 1 | Week 2 | Week 3 | Week 4 | Definition |
|---|---|---|---|---|---|
| Leads in | | | | | New buyer leads recorded |
| Replies sent | | | | | Leads that got a first reply (M-01 or M-02) |
| Median time to first reply | | | | | Lead received to first message sent |
| Consults booked | | | | | Bookings matched to a lead |
| Agreements sent | | | | | Leads that reached SENT |
| Signed | | | | | Leads that reached SIGNED (all parties) |
| Tours seen | | | | | Tour signals matched to a lead |
| Tours without signature | | | | | Seen tours where the buyer was unsigned when the signal arrived |
| Urgent alerts sent | | | | | M-26 count |
| Alerts acknowledged in 30 min | | | | | Share of M-26 with "Got it" within 30 minutes |
| STOP requests | | | | | Opt-outs by any method |
| Errors | | | | | Failed sends plus unknown sends plus unmatched events |
| Sorter misses | | | | | Wrong labels in the Monday sample |

## 5. Pilot scorecard

**Baseline:** with the agent, list every buyer lead from the last 30 days (CRM export or by hand): time in, time of first reply, date signed, date of first tour. Work out PS-1 to PS-3. If a number can't be found, write "unknown". Don't guess.

| ID | Metric | Baseline (last 30 days) | Day 30 | It worked if | Stop or change if |
|---|---|---|---|---|---|
| PS-1 | Share of buyer leads signed before their first tour | | | 20 points or more above baseline, or 90% or more if the baseline was already 70% or more | Under 5 points above baseline |
| PS-2 | Median time from lead to first reply | | | Under 1 minute | Over 5 minutes (a problem on our side) |
| PS-3 | Tours with nothing signed | | | Fewer than baseline, and 0 seen tours without an alert | Any seen tour without an alert |
| PS-4 | Urgent alerts acknowledged within 30 minutes | Not applicable | | 80% or more | Under 50% |
| PS-5 | Compliance incidents: message after STOP, unapproved message, legal answer, text outside the hard limit, message to someone who didn't ask | Not applicable | | 0 | Any. Stop at once (section 6) |
| PS-6 | Opt-out rate | Not applicable | | Under 5% | Over 10% |
| PS-7 | Agent keeps it and pays | Not applicable | | Yes | No |

**It worked** means PS-1, PS-2, PS-3, PS-5 and PS-7 all meet "It worked".

**Stop or change** means any row hit "Stop or change". PS-5 means stop at once. For the others, change one thing (timing, wording, alert channel), run 30 more days, or end the pilot.

**Not enough data:** fewer than 10 buyer leads or fewer than 5 tours in the 30 days. Extend to 60 days before judging.

## 6. Shut it off at once if

- **SO-1.** Any message reaches a buyer after they opted out.
- **SO-2.** Any buyer message is not an approved template.
- **SO-3.** Any message answers a legal question (commission, terms, "do I have to sign").
- **SO-4.** Duplicate texts: the same message to the same buyer twice, or more than 5 messages to one buyer in 24 hours.
- **SO-5.** A message goes to someone who didn't ask (wrong person, a seller or rental lead, an old list).
- **SO-6.** A text reaches a buyer outside 8:00 to 21:00 in their time zone.
- **SO-7.** Any sign the system touched agreement content: a draft with fields filled in, the wrong template, the wrong recipient.
- **SO-8.** A message carries the wrong agent's name, firm or link.
- **SO-9.** A security problem: a leaked key, an unknown login to the operator page, exposed tokens.
- **SO-10.** A warning or suspension from a carrier, Twilio or Google, or a spam complaint.
- **SO-11.** An ID, card or bank number is found in our data.
- **SO-12.** The agent or the lawyer says stop.

**How to shut it off**
1. Operator page: press Global pause. All buyer messages stop within 60 seconds.
2. If the app itself misbehaves: in Railway, scale the worker to zero.
3. If texts are the problem: suspend the agent's Twilio sub-account.
4. If access is the problem: revoke the Google and DocuSign tokens and rotate our keys.
5. Tell the agent what happened and that it is paused.

**After shutting it off**
1. Read the timelines involved and write down what happened and why.
2. Fix it, add a test that would have caught it, run the full test suite.
3. If a buyer got a wrong message, the agent decides whether to contact them. [Lawyer] if it involves STOP, consent or legal content.
4. Log it in DECISIONS.md.
5. Unpause only after the new test passes and the agent agrees.
