"""Ramil's daily gold direction calls ("BUY GOLD" / "SELL GOLD" at the top of his group welcome post) against the gold price.
Calls come from data/raw/telegram/toptarget/relevant.jsonl (git-ignored); prices are H1 XAUUSD bars read read-only from the
running demo terminal (attach only, no login, no orders). A call holds until the next call.
For each call: gold's move over the next 4 / 24 hours and until the next call, signed toward the call, in dollars.
Also the share of hours in which the called side is the losing side of a 10-dollar adverse run (the deep-basket situation).
Usage: python research/telegram/ramil_calls.py OUT_CSV"""
import json, re, sys, datetime as dt
from zoneinfo import ZoneInfo
import MetaTrader5 as mt5
import pandas as pd

SRC = "data/raw/telegram/toptarget/relevant.jsonl"
RAMIL = 1708204414
SERVER = ZoneInfo("Europe/Athens")

C = []
for l in open(SRC, encoding="utf-8"):
    r = json.loads(l)
    m = re.search(r"(BUY|SELL)\s+GOLD", r["text"], re.I) if r["from"] == RAMIL else None
    if m: C.append((pd.Timestamp(r["date"]), 1 if m.group(1).upper() == "BUY" else -1))
c = pd.DataFrame(C, columns=["t", "dir"]).sort_values("t").reset_index(drop=True)
c = c[c["dir"] != c["dir"].shift()].reset_index(drop=True)             # repeats of the same call are one call

if not mt5.initialize(path=r"C:\MT5_JEV_DEMO\terminal64.exe"): sys.exit(f"attach failed {mt5.last_error()}")
r = mt5.copy_rates_range("XAUUSD", mt5.TIMEFRAME_H1, dt.datetime(2026, 1, 1), dt.datetime(2026, 11, 8))
mt5.shutdown()
b = pd.DataFrame(r)
b["t"] = [dt.datetime.utcfromtimestamp(x).replace(tzinfo=SERVER).astimezone(dt.timezone.utc) for x in b["time"]]
b = b.set_index("t")

def px(t):                                                              # open of the first bar at or after t
    i = b.index.searchsorted(t)
    return b["open"].iloc[i] if i < len(b) else None

out = []
for k, row in c.iterrows():
    t0 = row["t"]; t1 = c["t"].iloc[k + 1] if k + 1 < len(c) else b.index[-1]
    p0 = px(t0)
    if p0 is None: continue
    seg = b[(b.index >= t0) & (b.index < t1)]
    d = row["dir"]
    adverse = (p0 - seg["low"].min()) if d == 1 else (seg["high"].max() - p0)
    out.append({"t": t0, "dir": d, "hours": round((t1 - t0).total_seconds() / 3600, 1),
                "r4": d * (px(t0 + pd.Timedelta(hours=4)) - p0), "r24": d * (px(t0 + pd.Timedelta(hours=24)) - p0),
                "rnext": d * (px(t1) - p0), "adverse": adverse})
o = pd.DataFrame(out); o.to_csv(sys.argv[1], index=False)
print("calls (direction changes):", len(o), o["t"].min().date(), "->", o["t"].max().date())
for col in ("r4", "r24", "rnext"):
    s = o[col].dropna()
    print(f"{col}: hit {(s > 0).mean():.0%}  mean {s.mean():+.1f}$  median {s.median():+.1f}$  n={len(s)}")
print(f"adverse run against the call >= 30$: {(o['adverse'] >= 30).mean():.0%} of calls; median adverse {o['adverse'].median():.1f}$")
# placebo: the call reversed (if the calls carried no information, both sides look alike)
print("reversed calls, rnext mean:", f"{(-o['rnext']).mean():+.1f}$")
