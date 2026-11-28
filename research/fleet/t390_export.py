"""t390: export BD-original MaxSpred=50 tester deals per Lars segment, normalized to the deposit (no balances), for Grok's
t389 machine (virtual floor on M1). Same layout as t384_tester/{seg_id}_b.csv.gz. Usage: py -3.12 research/fleet/t390_export.py"""
import os, sys
import pandas as pd
sys.path.insert(0, "research/btc"); from guardian_sim import deals
S = pd.read_csv("data/derived/lars/segments_t384.csv", parse_dates=["start", "start_live", "cut_live", "end_live"])
OUT = "docs/agents/grok_data/t390_tester"; os.makedirs(OUT, exist_ok=True); n = 0
for i, r in enumerate(S.itertuples(), 1):
    rep = f"C:/MT5_JEV_TEST/t390_b50_{r.acct}_{i:02d}.htm"
    if not os.path.exists(rep): continue
    d = deals(rep); d = d[d.symbol == "XAUUSD"].copy(); d["ts"] = pd.to_datetime(d.t, unit="s")
    e = d[["ts", "dir", "type", "price", "comment"]].copy(); e["vol_per_100k"] = d.volume / r.e_start_live * 1e5
    for c in ("profit", "swap", "commission"): e[c + "_pct"] = 100 * d[c] / r.e_start_live
    e.to_csv(f"{OUT}/A{r.acct}_{r.start:%Y%m%d}_b50.csv.gz", index=False); n += 1
print(n, "segments exported")
