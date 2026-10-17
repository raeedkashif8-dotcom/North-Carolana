"""CP0-T5 spike (S-4): throwaway test of the reply sorter on Gemini.

Not production code. The app never imports this folder.

Usage (from the project folder):
  spikes\\.venv\\Scripts\\python spikes\\s4_sorter_gemini.py --rules-only
  set GEMINI_API_KEY=...   (free tier is fine: these 30 replies are fake)
  spikes\\.venv\\Scripts\\python spikes\\s4_sorter_gemini.py --runs 3
"""
import argparse, json, os, re, sys, time

MODELS = ["gemini-3.1-flash-lite", "gemini-3.8-flash"]
LABELS = ["stop", "legal_question", "wants_consult", "wants_tour", "other"]

# ---------- Layer 1: fixed rules (ARCHITECTURE RS-1 to RS-4) ----------
OPT_OUT_WORDS = {"stop", "stopall", "unsubscribe", "cancel", "end", "quit",
                 "revoke", "optout", "opt out"}
# No phrase list (D-32): any other wording is judged by the model.
WEAK_WORDS = {"stop", "cancel", "end", "quit"}


def normalize(text):
    t = text.lower().replace("'", "").replace("’", "")
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def rule_opt_out(text):
    n = normalize(text)
    if n in OPT_OUT_WORDS:
        return "word"
    return None


def mask(text):
    t = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[email]", text)
    t = re.sub(r"\d{11,}", "[number]", t)  # long unbroken runs (accounts, cards) first
    t = re.sub(r"(?<![\d\w])(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(?!\d)", "[phone]", t)
    t = re.sub(r"\d[\d\s-]{5,}\d", "[number]", t)
    return t


# ---------- Layer 2: Gemini (RS-5 to RS-9) ----------
SCHEMA = {
    "type": "object",
    "properties": {
        "label": {"type": "string", "enum": LABELS},
        "possible_opt_out": {"type": "boolean"},
        "language": {"type": "string", "enum": ["en", "other"]},
    },
    "required": ["label", "possible_opt_out", "language"],
    "additionalProperties": False,
}

SYSTEM = """You sort one reply from a home buyer to a real estate agent's automated message.
You never answer the buyer. You only pick a label.

Labels:
- stop: the person wants no more messages, is not interested, has another agent, or says wrong number.
- legal_question: any question about the buyer agreement or money owed to the agent: commission, fees the agent is paid, who pays the agent, exclusivity, how long the agreement lasts, cancelling or getting out of the agreement, whether they must sign, what they are bound to, or whether something is legal.
- wants_tour: wants to see, tour, visit or walk through a specific home or homes.
- wants_consult: wants a call, meeting or consult, asks for times, or needs the booking link again, including moving an existing call.
- other: anything else, such as questions about a property's features, price, HOA or availability, thanks, or updates.

Precedence when several apply: stop, then legal_question, then wants_tour, then wants_consult, then other.
possible_opt_out: true if there is any real chance the person wants no more messages. "Cancel our call" is not an opt-out.
language: "en" if the reply is in English, else "other".

Examples:
"please don't message me again" -> stop
"we already found an agent, thanks" -> stop
"how much do you charge buyers?" -> legal_question
"if I sign, am I stuck with you for a year?" -> legal_question
"is it legal for you to ask me to sign first?" -> legal_question
"could we visit the townhouse on Pine this weekend?" -> wants_tour
"I'd like to walk through 88 Birch on Monday" -> wants_tour
"can you call me after 5?" -> wants_consult
"need to push our meeting to next week" -> wants_consult
"how many bedrooms does it have?" -> other
"ok sounds good" -> other
"what are the property taxes on that one?" -> other
"Quiero ver la casa" -> other (language other)
"""


PACE_SECONDS = float(os.environ.get("SPIKE_PACE_SECONDS", "4"))  # free tier has a per-minute cap


def model_label(client, model, text, retries=5):
    """Spike-only wrapper: pace calls and retry rate-limit errors, so the score measures the model."""
    from google.genai import errors
    for attempt in range(retries + 1):
        time.sleep(PACE_SECONDS)
        try:
            return _model_label(client, model, text)
        except errors.ClientError as e:
            if getattr(e, "code", None) == 429 and attempt < retries:
                wait = 15 * (attempt + 1)
                print(f"    rate limited, waiting {wait}s", flush=True)
                time.sleep(wait)
                continue
            raise


def _model_label(client, model, text):
    from google.genai import types
    resp = client.models.generate_content(
        model=model,
        contents=f"Previous message from the agent: instant_reply\nBuyer reply: {mask(text)}",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM,
            temperature=0,
            response_mime_type="application/json",
            response_json_schema=SCHEMA,
        ),
    )
    out = json.loads(resp.text)
    if set(out) != {"label", "possible_opt_out", "language"} or out["label"] not in LABELS:
        raise ValueError(f"bad output: {out}")
    return out


def decide(text, client=None, model=None):
    """Returns (final_label, layer)."""
    hit = rule_opt_out(text)
    if hit:
        return "stop", f"rule:{hit}"
    if client is None:
        return None, "needs model"
    try:
        out = model_label(client, model, text)
    except Exception as e:  # RS-9 fallback
        why = f"fallback:{type(e).__name__}:{getattr(e, 'code', '')}"
        if WEAK_WORDS & set(normalize(text).split()):
            return "stop", why
        return "other", why
    if out["label"] == "stop" or out["possible_opt_out"]:
        return "stop", "model"
    if out["language"] == "other":
        return "other", "model:non-english"
    return out["label"], "model"


# ---------- TP-AI-01 samples ----------
SAMPLES = [
    ("AI-S01", "STOP", "stop"),
    ("AI-S02", "Stop texting me please", "stop"),
    ("AI-S03", "Not interested anymore, we went with another agent", "stop"),
    ("AI-S04", "take me off your list", "stop"),
    ("AI-S05", "Who is this?? Don't contact me again", "stop"),
    ("AI-S06", "I'm all set for now, no more messages please", "stop"),
    ("AI-S07", "What's your commission?", "legal_question"),
    ("AI-S08", "Do I have to sign this before seeing a house?", "legal_question"),
    ("AI-S09", "Can I get out of the agreement if I'm not happy with you?", "legal_question"),
    ("AI-S10", "Who pays you, me or the seller?", "legal_question"),
    ("AI-S11", "Is this exclusive? Can I still look with other agents?", "legal_question"),
    ("AI-S12", "How long does the agreement last and can I cancel it?", "legal_question"),
    ("AI-S13", "My lender told me not to sign anything yet. Is that right?", "legal_question"),
    ("AI-S14", "What happens if I find a house on my own while I'm signed with you?", "legal_question"),
    ("AI-S15", "Yes let's set up a call", "wants_consult"),
    ("AI-S16", "Can we talk tomorrow afternoon?", "wants_consult"),
    ("AI-S17", "The booking link isn't working, can you send it again?", "wants_consult"),
    ("AI-S18", "Sure! What times do you have this week?", "wants_consult"),
    ("AI-S19", "I need to cancel our call tomorrow, can we do Friday instead?", "wants_consult"),
    ("AI-S20", "Can I see 412 Oak St this Saturday?", "wants_tour"),
    ("AI-S21", "We'd love to tour the house on Maple before it's gone", "wants_tour"),
    ("AI-S22", "Can you show us a few homes in Cary next weekend?", "wants_tour"),
    ("AI-S23", "When can we go see it?", "wants_tour"),
    ("AI-S24", "Saw it on Zillow, want to walk through Thursday evening", "wants_tour"),
    ("AI-S25", "Is 412 Oak St still available?", "other"),
    ("AI-S26", "Thanks!", "other"),
    ("AI-S27", "We're pre-approved up to 350k", "other"),
    ("AI-S28", "Does the house have a basement?", "other"),
    ("AI-S29", "¿Podemos ver la casa el sábado?", "other"),
    ("AI-S30", "What's the HOA fee on that one?", "other"),
]
# Samples the fixed rules must catch (TEST_PLAN column "Should be caught by").
RULE_EXPECTED = {"AI-S01"}


def rules_only():
    bad = 0
    for sid, text, exp in SAMPLES:
        hit = rule_opt_out(text)
        should = sid in RULE_EXPECTED
        ok = bool(hit) == should
        bad += not ok
        print(f"{sid}  rule={hit or '-':6}  expected_rule={'yes' if should else 'no ':3}  {'OK' if ok else 'WRONG'}  {text}")
    print(f"\nrules layer: {len(SAMPLES) - bad}/{len(SAMPLES)} as expected")
    return bad == 0


def passes(results):
    correct = sum(r[3] == r[2] for r in results)
    stop_ok = all(r[3] == "stop" for r in results if r[2] == "stop")
    legal_ok = all(r[3] == "legal_question" for r in results if r[2] == "legal_question")
    return correct, stop_ok, legal_ok, (correct >= 27 and stop_ok and legal_ok)


def load_env_file():
    """Read KEY=value lines from spikes/.env (git-ignored) into the environment."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def run_models(models, runs):
    from google import genai
    load_env_file()
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        sys.exit("No GEMINI_API_KEY found. Put GEMINI_API_KEY=your-key in spikes/.env "
                 "(get one at https://aistudio.google.com/apikey)")
    client = genai.Client(api_key=key)
    summary = []
    for model in models:
        for run in range(1, runs + 1):
            results, t0 = [], time.time()
            for sid, text, exp in SAMPLES:
                got, layer = decide(text, client, model)
                results.append((sid, text, exp, got, layer))
            correct, stop_ok, legal_ok, ok = passes(results)
            print(f"\n=== {model} run {run}: {correct}/30  stop 6/6={stop_ok}  legal 8/8={legal_ok}  "
                  f"PASS={ok}  ({time.time() - t0:.1f}s)")
            for sid, text, exp, got, layer in results:
                if got != exp:
                    print(f"  MISS {sid}: expected {exp}, got {got} [{layer}]  {text}")
            summary.append((model, run, correct, ok))
    print("\nSummary:")
    for model, run, correct, ok in summary:
        print(f"  {model} run {run}: {correct}/30 {'PASS' if ok else 'FAIL'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules-only", action="store_true")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--model", choices=MODELS)
    a = ap.parse_args()
    if a.rules_only:
        sys.exit(0 if rules_only() else 1)
    run_models([a.model] if a.model else MODELS, a.runs)
