# CP0 Spike Results

Throwaway tests from CHECKPOINTS.md CP0. Scripts live in `spikes/`, which the app never imports. Setup: `python -m venv spikes\.venv` then `spikes\.venv\Scripts\pip install -r spikes\requirements.txt`.

| Spike | Task | Status | Result |
|---|---|---|---|
| S-1 Calendar link delay | CP0-T1 | Script ready, not run | Needs your calendar's secret iCal link |
| S-2 ShowingTime contents | CP0-T2 | Blocked | Needs 2 to 3 redacted emails from interviews (I2) |
| S-3 DocuSign | CP0-T3a, T3b | Not started | Needs your DocuSign developer account |
| S-4 Sorter (Gemini) | CP0-T5 | **Done** | `gemini-3.1-flash-lite` 30/30 in 3 of 3 runs |
| Approvals | CP0-T4 | Not started | Your accounts and money |

## S-4. Reply sorter on Gemini (D-31)

Script: `spikes/s4_sorter_gemini.py`. Models: `gemini-3.1-flash-lite` (default), `gemini-3.8-flash` (option).

**Run 2026-10-17, rules layer only (`--rules-only`, no key needed):** 30/30 as expected. Before D-32 the rules caught AI-S01, S02, S04, S05, S06; after D-32 removed the phrase list, they catch only AI-S01 (rerun, 30/30 as expected). The two "cancel" samples (AI-S12, AI-S19) correctly passed through to the model.

**Masking check 2026-10-17:** first run had a bug: `account 123456789012` became `account 12[phone]`. Fixed by masking long digit runs first. After the fix, all 6 cases masked correctly (card with spaces, SSN, routing and account, phone and email, `+1 (919)` phone, 16-digit card).

**Model layer, run 2026-10-17 (free-tier key, fake replies only).**
- First attempt: invalid as a score. After about 20 calls, almost every call failed with a client error (the free tier's per-minute limit). Every failed call fell back safely: the two "cancel" replies became stops, everything else went to "other", and no reply was automated. Fix: 4 s pacing plus retry on HTTP 429 (spike only).
- Second attempt (still with the old phrase list): `gemini-3.1-flash-lite` 30/30 in 3 of 3 runs. Stopped before `gemini-3.8-flash` finished, because D-32 removed the phrase list.
- **Final, after D-32 (no phrase list):** `gemini-3.1-flash-lite` **30/30 in 3 of 3 runs**, stop 6/6 and legal 8/8 every run. The 4 opt-outs the phrase list used to catch were all caught by the model. Raw output: `spikes/s4_run_2026-10-17_no_phrases.txt`.
- **Result: TP-AI-01 and TP-AI-02 bar met in the spike. Keep `gemini-3.1-flash-lite` as the default.** `gemini-3.8-flash` not needed. The official run is still CP6-T4, on the production prompt and a paid-tier key.
- Limit of this result: 30 replies written by us, not real buyers. The weekly review in VERIFY.md is what tests real wording.

## S-1. Calendar link delay

Script: `spikes/s1_calendar_ics.py`. Parsing tested on a sample event: it read the title and start time correctly. Real timing: not run.
