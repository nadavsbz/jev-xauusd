"""Scheduled releases with the ACTUAL NFP dates for account 1's period (Nov 2025 - Oct 2026), the
input of research/crash/event_pause.py: NFP dates from research/bd1/news_test.py (BLS schedule),
08:30 New York; FOMC from events.csv (federalreserve.gov, last day of each scheduled meeting).
Usage: python research/crash/events_actual.py EVENTS_CSV OUT_CSV"""
import re, sys
import pandas as pd

src = open("research/bd1/news_test.py", encoding="utf-8").read()
nfp = re.findall(r'"(\d{4}-\d\d-\d\d)"', src.split("NFP = [")[1].split("]")[0])
ev = pd.read_csv(sys.argv[1])
rows = [(pd.Timestamp(f"{d} 08:30").tz_localize("America/New_York").tz_convert("UTC").strftime("%Y-%m-%d %H:%M"), "NFP") for d in nfp]
rows += [(u, "FOMC") for u, k in zip(ev.utc, ev.kind) if k == "FOMC" and "2025-11" <= u[:7] <= "2026-10"]
pd.DataFrame(sorted(rows), columns=["utc", "kind"]).to_csv(sys.argv[2], index=False)
print(len(rows), "events")
