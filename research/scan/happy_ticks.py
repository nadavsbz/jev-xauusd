"""Happy News (conservative: RF entry = last tick of the account's entry second) (Grok t230) feasibility at RoboForex: for each of the account's trades in the last N months, pull RF real ticks
around the trade (read-only, demo terminal) and measure (a) RF spread at entry, (b) the same-direction move on RF from the
account's entry second to its exit second (bid/ask aware), vs the account's own pips. Descriptive only.
Usage: py -3.12 research/scan/happy_ticks.py [months]"""
import sys, datetime as dt
import numpy as np, pandas as pd
import MetaTrader5 as mt5
sys.path.insert(0, "tools")
from collect_history import load_account
TERM = r"C:\MT5_JEV_TEST\terminal64.exe"
MON = int(sys.argv[1]) if len(sys.argv) > 1 else 6
d = pd.read_csv("docs/agents/grok_data/t230_happy/1864588.history.csv", sep=";", encoding="utf-8-sig")
d.columns = ["t0", "type", "vol", "sym", "p0", "sl", "tp", "t1", "p1", "comm", "swap", "profit", "comment"]
t = d[d.type.isin(["Buy", "Sell"])].copy()
for c in ("vol", "p0", "p1", "profit", "comm"): t[c] = pd.to_numeric(t[c].astype(str).str.replace(" ", ""), errors="coerce")
t["t0"] = pd.to_datetime(t.t0); t["t1"] = pd.to_datetime(t.t1); t["q"] = np.where(t.type == "Buy", 1, -1)
t = t[t.t0 >= t.t0.max() - pd.DateOffset(months=MON)]
acc = load_account("accounts.json", "Bots ECN demo")
if not mt5.initialize(path=TERM, login=int(acc["login"]), password=acc["password"], server=acc["server"], timeout=240000, portable=True):
    sys.exit(f"init failed {mt5.last_error()}")
if mt5.account_info().trade_mode != 0: mt5.shutdown(); sys.exit("not demo")
out = []
for _, r in t.iterrows():
    s = r.sym.split(".")[0]; mt5.symbol_select(s, True); pip = 0.01 if "JPY" in s else 0.0001
    a = dt.datetime(*r.t0.timetuple()[:6]) - dt.timedelta(seconds=30); b = dt.datetime(*r.t1.timetuple()[:6]) + dt.timedelta(seconds=5)
    k = mt5.copy_ticks_range(s, a.replace(tzinfo=dt.timezone.utc), b.replace(tzinfo=dt.timezone.utc), mt5.COPY_TICKS_INFO)
    if k is None or not len(k): out.append({"t": r.t0, "sym": s, "ok": False}); continue
    k = pd.DataFrame(k); k["ts"] = pd.to_datetime(k.time_msc, unit="ms")
    e = k[k.ts < r.t0 + pd.Timedelta(seconds=1)]; x = k[k.ts <= r.t1]   # end of the entry second: no in-second look-ahead
    if not len(e) or not len(x): out.append({"t": r.t0, "sym": s, "ok": False}); continue
    e, x = e.iloc[-1], x.iloc[-1]
    rf = ((x.bid - e.ask) if r.q > 0 else (e.bid - x.ask)) / pip
    acct = r.q * (r.p1 - r.p0) / pip
    out.append({"t": r.t0, "sym": s, "ok": True, "hold": (r.t1 - r.t0).total_seconds(), "acct_pips": acct, "rf_pips": rf,
                "rf_spread_entry": (e.ask - e.bid) / pip, "rf_ticks": len(k), "acct_fill_vs_rf_mid": r.q * ((e.bid + e.ask) / 2 - r.p0) / pip})
mt5.shutdown()
o = pd.DataFrame(out); o.to_csv("data/derived/scan/happy_rf_ticks.csv", index=False)
v = o[o.ok]
print(f"trades {len(o)}, with RF ticks {len(v)}")
print(v[["acct_pips", "rf_pips", "rf_spread_entry", "acct_fill_vs_rf_mid", "hold"]].describe().round(2).to_string())
print("sum acct pips", round(v.acct_pips.sum()), "| sum RF pips (same seconds, bid/ask)", round(v.rf_pips.sum()))
print(v.groupby("sym")[["acct_pips", "rf_pips", "rf_spread_entry"]].mean().round(2).to_string())
