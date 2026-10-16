"""Daily curves of the tools (docs/PORTFOLIO_PLAN.md, step 2). Results are booked on the day they
were realised (basket / trade close), not the day the basket opened.
- account1: real baskets (clusters_strict.csv). Per close day: realised return of the baskets that
  closed that day, compounded in order of opening; trough = the lowest point of the equity path
  through the day, each basket's MAE applied to the equity built up before it (opening order).
  Baskets that open before 2026-06-01 and close on or after it are flagged (purged from both periods).
- bull: Bull Scalper EGlobal M5 tester run (100% real ticks), realised per day as a share of the
  $50,000 deposit, commission and swap rescaled per lot to the RoboForex ECN run (ASSUMED: same
  trades and prices; floating not included).
- btc (optional, a tester report and its deposit): BTC Bot realised per day as a share of the deposit.
Usage: python research/portfolio/curves.py OUT_CSV [BTC_REPORT.htm BTC_DEPOSIT]"""
import re, sys
import numpy as np, pandas as pd

EG = r"C:\MT5_JEV_TEST\bull_ftmo_full_m5.htm"
COMM_PER_LOT_ROBO, SWAP_PER_LOT_ROBO = -538.07 / 2199.2, -4475.43 / 2199.2      # bull_robo_ecn_m5 evidence
COMM_PER_LOT_EG, SWAP_PER_LOT_EG = -12031.49 / 2390.8, -3383.34 / 2390.8        # bull_ftmo_full_m5 evidence (USD)
SPLIT = pd.Timestamp("2026-06-01")


def report_deals(path, cents=False):
    text = open(path, "rb").read().decode("utf-16")
    cells = [[re.sub("<.*?>", "", x).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
             for r in re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S)]
    d = pd.DataFrame([c for c in cells if len(c) == 13 and re.match(r"\d{4}\.\d\d\.\d\d", c[0])],
                     columns=["time", "deal", "symbol", "type", "dir", "volume", "price", "order",
                              "commission", "swap", "profit", "balance", "comment"])
    for c in ["commission", "swap", "profit"]:
        d[c] = pd.to_numeric(d[c].str.replace(" ", "").str.replace(",", ""), errors="coerce") / (100 if cents else 1)
    d = d[(d.type != "balance") & (d.comment != "end of test")].copy()   # tester force-closes are not trades
    d["day"] = pd.to_datetime(d.time, format="%Y.%m.%d %H:%M:%S").dt.normalize()
    return d


def book_entry_costs_at_exit(d):
    """Entry commission is booked with the exit, at the run's average entry commission per lot
    times the volume closed, so a whole trade lands on its close day (a trade open across
    31.5/1.6 then falls entirely in the period it closed in)."""
    d = d.copy(); d["volume"] = pd.to_numeric(d.volume, errors="coerce")
    ins = d.dir == "in"
    per_lot = d.commission[ins].sum() / d.volume[ins].sum()
    d.loc[ins, "commission"] = 0.0
    d.loc[~ins, "commission"] = d.commission[~ins] + per_lot * d.volume[~ins]
    return d


def bull_daily():
    d = book_entry_costs_at_exit(report_deals(EG, cents=True))
    net = d.profit + d.commission * (COMM_PER_LOT_ROBO / COMM_PER_LOT_EG) + d.swap * (SWAP_PER_LOT_ROBO / SWAP_PER_LOT_EG)
    return net.groupby(d.day).sum() / 50000


def btc_daily(path, deposit):
    d = book_entry_costs_at_exit(report_deals(path))
    return (d.profit + d.commission + d.swap).groupby(d.day).sum() / deposit


def acc_daily():
    o = pd.read_csv("data/derived/bd1/clusters_strict.csv").sort_values("t0")
    o["day"] = pd.to_datetime(o.t1, unit="s").dt.normalize()
    o["cross"] = (pd.to_datetime(o.t0, unit="s") < SPLIT) & (pd.to_datetime(o.t1, unit="s") >= SPLIT)
    r, tr = {}, {}
    for day, g in o.groupby("day"):
        eq, low = 1.0, 0.0
        for p, m in zip(g.pnl_pct.values / 100, g.mae_pct.values / 100):
            low = min(low, eq * (1 + min(m, 0)) - 1)
            eq *= 1 + p
        r[day], tr[day] = eq - 1, min(low, eq - 1)
    return pd.Series(r), pd.Series(tr), o.groupby("day").cross.any()


if __name__ == "__main__":
    a, atr, cross = acc_daily(); b = bull_daily()
    days = pd.bdate_range(max(a.index.min(), b.index.min()), min(a.index.max(), b.index.max()))
    out = pd.DataFrame({"account1": a.reindex(days).fillna(0), "account1_trough": atr.reindex(days).fillna(0),
                        "account1_crosses_split": cross.reindex(days).fillna(False), "bull": b.reindex(days).fillna(0)})
    if len(sys.argv) > 3:
        out["btc"] = btc_daily(sys.argv[2], float(sys.argv[3])).reindex(days).fillna(0)
    out.to_csv(sys.argv[1])
    print(out.describe().round(4).to_string())
    cols = [c for c in ("account1", "bull", "btc") if c in out]
    print("compounded:", (1 + out[cols]).prod().round(3).to_dict(), "| corr\n", out[cols].corr().round(3).to_string())
