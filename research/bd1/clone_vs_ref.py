"""Basket match between two tester reports (clone vs original BD, same ticks) or vs account 1 live.
Usage: python research/bd1/clone_vs_ref.py REF FROM TO REPORT [REPORT ...]
REF = a report name in C:\MT5_JEV_TEST (e.g. val_sep26_bdreal) or 'live' (account 1 deals snapshot)."""
import os, sys, json
import pandas as pd
sys.path[:0] = [os.path.join(os.path.dirname(__file__), "..", "btc"), os.path.dirname(__file__)]
import guardian_sim as g
from clone_vs_live import live_pos, table

LIVE = "data/raw/black_dragon_1/20261023T211719Z/deals.csv"

def load(name, lo, hi):
    p = live_pos(LIVE) if name == "live" else g.pair(g.deals(f"C:/MT5_JEV_TEST/{name}.htm"))[0]
    return table(p[(p.t0 >= lo) & (p.t0 < hi)])

def match(R, C):
    j = R.join(C, rsuffix="_c", how="inner")
    return {"ref": len(R), "test": len(C), "same_bar": round(len(j) / len(R), 3), "same_side": round(float((j.side == j.side_c).mean()), 3),
            "same_levels": round(float((j.n == j.n_c).mean()), 3), "exit_60s": round(float(((j.t1 - j.t1_c).abs() <= 60).mean()), 3),
            "net": round(float(C.net.sum())), "worst": round(float(C.net.min()))}

if __name__ == "__main__":
    ref, f, t = sys.argv[1:4]; lo = pd.Timestamp(f).value // 10**9; hi = pd.Timestamp(t).value // 10**9
    R = load(ref, lo, hi)
    print(json.dumps({r: match(R, load(r, lo, hi)) for r in sys.argv[4:]}, indent=1))
