"""CP0-T1 spike (S-1): how fast does a change show up in a Google Calendar private iCal link?

Not production code. The app never imports this folder.

1. Google Calendar > Settings > your calendar > "Secret address in iCal format". Copy it.
   (If that row is missing, a Workspace admin turned it off: record that as a finding.)
2. set CAL_ICS_URL=<that link>      (it is a secret: never commit it)
3. spikes\\.venv\\Scripts\\python spikes\\s1_calendar_ics.py
4. While it runs, create an event "Showing - Test Buyer - 12 Oak St" for tomorrow,
   then edit its time. Note the clock time you did each. Stop with Ctrl+C.
"""
import hashlib, os, sys, time
from datetime import datetime

import httpx
from icalendar import Calendar

URL = os.environ.get("CAL_ICS_URL") or sys.exit("Set CAL_ICS_URL first (see top of file).")
seen = {}  # uid -> (summary, start, last-modified)
start = time.time()
while True:
    t = datetime.now().strftime("%H:%M:%S")
    try:
        r = httpx.get(URL, timeout=30, follow_redirects=True)
        r.raise_for_status()
        cal = Calendar.from_ical(r.content)
    except Exception as e:
        print(f"{t}  fetch failed: {e}")
        time.sleep(60)
        continue
    events = {}
    for ev in cal.walk("VEVENT"):
        uid = str(ev.get("UID"))
        events[uid] = (str(ev.get("SUMMARY", "")), str(ev.decoded("DTSTART", "")), str(ev.get("LAST-MODIFIED", "")))
    if not seen:
        print(f"{t}  first read: {len(events)} events, {len(r.content)} bytes, "
              f"sha={hashlib.sha256(r.content).hexdigest()[:10]}")
    else:
        for uid, v in events.items():
            if uid not in seen:
                print(f"{t}  NEW     {v[0]!r} starts {v[1]}  (+{(time.time() - start) / 60:.1f} min since script start)")
            elif seen[uid] != v:
                print(f"{t}  CHANGED {v[0]!r} starts {v[1]}")
        for uid in seen.keys() - events.keys():
            print(f"{t}  REMOVED {seen[uid][0]!r}")
    seen = events
    time.sleep(60)
