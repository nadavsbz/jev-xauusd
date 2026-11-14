"""Diagnostic for round 44/45 (not a new test, no parameter choice): does our 44a simulator reproduce Happy News' real book
(MQL5 1864588, Eightcap, Grok export t230) on the SAME events? Matches each filled book trade to the cached RF tick file of
that release (server time, +-3 min) and compares direction and pips. If the sim tracks the book -> the 2019-22 failure is the
period, not the clone. If the book is much better on the same events -> the clone misses something (rules or fills).
Usage: py -3.12 research/scan/r44_book_match.py"""
import sys, glob, os
import numpy as np, pandas as pd
sys.argv = sys.argv[:1] + ["test"]
sys.path.insert(0, "research/scan")
from r44_sim import sim

b = pd.read_csv("docs/agents/grok_data/t230_happy/1864588.history.csv", sep=";", encoding="utf-8-sig")
b.columns = ["ot", "type", "vol", "sym", "op", "sl", "tp", "ct", "cp", "comm", "swap", "profit", "comment"]
b = b[b.type.isin(["Buy", "Sell"])].copy()
b["sym"] = b.sym.str.replace(".i", "", regex=False)
b = b[b.sym.isin(["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"])]
b["ot"] = pd.to_datetime(b.ot, format="%Y.%m.%d %H:%M:%S"); b["ct"] = pd.to_datetime(b.ct, format="%Y.%m.%d %H:%M:%S")
b["pip"] = np.where(b.sym.str.contains("JPY"), 0.01, 0.0001); b["q"] = np.where(b.type == "Buy", 1, -1)
b["bpips"] = b.q * (b.cp - b.op) / b.pip
idx = []
for f in glob.glob("data/derived/scan/news_ticks/*.csv"):
    s = os.path.basename(f).split("_")[0]
    try: T = pd.Timestamp(pd.read_csv(f, nrows=1).srv_T.iloc[0])
    except Exception: continue
    idx.append((s, T, f))
ix = pd.DataFrame(idx, columns=["sym", "T", "f"])
rows = []
for r in b.itertuples():
    c = ix[(ix.sym == r.sym) & ((r.ot - ix["T"]).dt.total_seconds().between(-180, 180))]
    if not len(c): rows.append({"ot": r.ot, "sym": r.sym, "bq": r.q, "bpips": r.bpips, "match": False}); continue
    f = c.iloc[0].f; s = sim(f, "a", 0.0)
    d = pd.read_csv(f); T = c.iloc[0]["T"]
    rows.append({"ot": r.ot, "sym": r.sym, "T": T, "bq": r.q, "bpips": r.bpips, "hold_s": (r.ct - r.ot).total_seconds(),
                 "match": True, "skind": s[1] if s else None, "spips": (s[0] + 0.6) if s else np.nan})  # sim pips gross of our 0.6 commission
o = pd.DataFrame(rows)
print("book filled trades on 4 majors:", len(o), "| matched to an RF tick file:", o.match.sum())
m = o[o.match].copy()
m["sdir"] = m.skind.map({"long": 1, "short": -1}).fillna(0)
print("sim fill on same event:", (m.sdir != 0).mean().round(3), "| same direction:", (m.sdir == m.bq).mean().round(3))
both = m[m.sdir == m.bq]
print(f"same-direction n={len(both)}: book mean {both.bpips.mean():.2f} median {both.bpips.median():.2f} | sim mean {both.spips.mean():.2f} median {both.spips.median():.2f} | corr {both[['bpips','spips']].corr().iloc[0,1]:.2f}")
print(f"all matched: book mean {m.bpips.mean():.2f} | sim mean (filled) {m[m.sdir!=0].spips.mean():.2f}")
print("by year book/sim mean:", m.groupby(m.ot.dt.year).apply(lambda g: (round(g.bpips.mean(), 2), round(g[g.sdir != 0].spips.mean(), 2), len(g))).to_dict())
print("unmatched book trades by year:", o[~o.match].groupby(o.ot.dt.year).size().to_dict(), "| book mean pips unmatched:", round(o[~o.match].bpips.mean(), 2))
print("book hold seconds median:", m.hold_s.median(), "| book pips quantiles:", m.bpips.quantile([.1, .25, .5, .75, .9]).round(1).to_dict())
o.to_csv("data/derived/scan/r44_book_match.csv", index=False)
