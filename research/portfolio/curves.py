"""Daily return curves of the tools on their common calendar (portfolio plan, step 2).
- account1: real baskets (clusters_strict.csv), per day of basket start: realised return
  compounded, and the worst floating trough of the day's baskets, as % of the balance.
- bull: Bull Scalper EGlobal M5 tester run (100% real ticks), realised per day as % of the
  $50,000 deposit, with commission and swap rescaled per lot to the RoboForex ECN run
  (ASSUMED: the same trades at a low-commission broker; floating not included).
Usage: python research/portfolio/curves.py OUT_CSV"""
import re, sys
import numpy as np, pandas as pd

EG = r"C:\MT5_JEV_TEST\bull_ftmo_full_m5.htm"
COMM_PER_LOT_ROBO, SWAP_PER_LOT_ROBO = -538.07 / 2199.2, -4475.43 / 2199.2      # bull_robo_ecn_m5 evidence
COMM_PER_LOT_EG, SWAP_PER_LOT_EG = -12031.49 / 2390.8, -3383.34 / 2390.8        # bull_ftmo_full_m5 evidence (USD)


def bull_daily():
    text = open(EG, "rb").read().decode("utf-16")
    cells = [[re.sub("<.*?>", "", x).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
             for r in re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S)]
    d = pd.DataFrame([c for c in cells if len(c) == 13 and re.match(r"\d{4}\.\d\d\.\d\d", c[0])],
                     columns=["time", "deal", "symbol", "type", "dir", "volume", "price", "order",
                              "commission", "swap", "profit", "balance", "comment"])
    for c in ["commission", "swap", "profit"]:
        d[c] = pd.to_numeric(d[c].str.replace(" ", "").str.replace(",", ""), errors="coerce") / 100   # cents -> USD
    d = d[d.type != "balance"]
    net = d.profit + d.commission * (COMM_PER_LOT_ROBO / COMM_PER_LOT_EG) + d.swap * (SWAP_PER_LOT_ROBO / SWAP_PER_LOT_EG)
    t = pd.to_datetime(d.time, format="%Y.%m.%d %H:%M:%S").dt.normalize()
    return net.groupby(t).sum() / 50000


def acc_daily():
    o = pd.read_csv("data/derived/bd1/clusters_strict.csv")
    o["day"] = pd.to_datetime(o.t0, unit="s").dt.normalize()
    r = o.groupby("day").pnl_pct.apply(lambda s: np.prod(1 + s / 100) - 1)
    tr = o.groupby("day").mae_pct.min() / 100
    return r, tr


if __name__ == "__main__":
    a, atr = acc_daily(); b = bull_daily()
    days = pd.bdate_range(max(a.index.min(), b.index.min()), min(a.index.max(), b.index.max()))
    out = pd.DataFrame({"account1": a.reindex(days).fillna(0), "account1_trough": atr.reindex(days).fillna(0),
                        "bull": b.reindex(days).fillna(0)})
    out.to_csv(sys.argv[1])
    print(out.describe().round(4).to_string())
    print("compounded:", (1 + out[["account1", "bull"]]).prod().round(3).to_dict(), "| corr", round(out.account1.corr(out.bull), 3))
