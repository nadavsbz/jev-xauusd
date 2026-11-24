"""BD live record per account (magic 5555): realized monthly P&L and hourly mark-to-market equity drawdown.
Floating P&L is marked at the XAUUSD H1 close of RoboForex data (intra-hour lows are missed, so drawdown is understated somewhat); contract size per account is fitted from closed deals (profit vs price move). Read-only on exported CSVs.
Usage: py -3.12 research/fleet/bd_live_mtm.py ACCT:EXPORTDIR [...]"""
import sys, json
import numpy as np, pandas as pd

PX = pd.read_csv("data/derived/intraday/XAUUSD_H1.csv"); PX["t"] = pd.to_datetime(PX.time, unit="s"); PX = PX.set_index("t")


def run(n, d):
    m = json.load(open(f"data/raw/black_dragon_{n}/{d}/manifest.json")); k = 100   # every fleet account is a cent account (Excel "סנטים"); RoboForex labels them USD
    x = pd.read_csv(f"data/raw/black_dragon_{n}/{d}/deals.csv"); x["t"] = pd.to_datetime(x.time, unit="s"); x = x.sort_values(["time", "ticket"])
    x["cash"] = (x.profit + x.swap + x.commission) / k
    tr = x[(x.type <= 1) & (x.magic == 5555)]
    ins = tr[tr.entry == 0]
    outs = x[(x.type <= 1) & (x.entry != 0) & x.position_id.isin(ins.position_id)]   # exits may carry another magic (manual close)
    pos = ins.groupby("position_id").agg(t0=("t", "first"), p0=("price", "mean"), v=("volume", "sum"), side=("type", "first")).join(
        outs.groupby("position_id").agg(t1=("t", "last"), p1=("price", "mean"), pr=("profit", "sum")))
    c = pos.dropna(); c = c[(c.p1 - c.p0).abs() > 1]
    sgn = np.where(c.side == 0, 1, -1)
    cs = float(np.median(c.pr / k / ((c.p1 - c.p0) * sgn * c.v)))           # fitted USD per lot per $1
    bal = x.cash.cumsum(); bal.index = x.t; bal = bal.groupby(level=0).last()
    hrs = PX.loc[pos.t0.min().floor("h"):].index
    fl = pd.Series(0.0, index=hrs)
    for r in pos.itertuples():
        t1 = r.t1 if pd.notna(r.t1) else hrs[-1]
        w = PX.loc[r.t0.floor("h"):t1.floor("h")]
        if not len(w): continue
        adv = (w.close - r.p0) if r.side == 0 else (r.p0 - w.close)   # H1 close: BD holds both sides, so per-side extremes overstate
        fl.loc[w.index] += adv.values * r.v * cs
    b = bal.reindex(hrs, method="ffill").fillna(0)
    fx = x[x.type == 2].cash; fx.index = x[x.type == 2].t; fx = fx.groupby(level=0).sum().cumsum()
    f = fx.reindex(hrs, method="ffill").fillna(0)
    tp = (b - f) + fl                                                         # trading P&L incl. floating, no deposits/withdrawals
    dd = (tp - tp.cummax()) / b.where(b > 0)                                  # $ drawdown over the balance at that hour
    flows = x[x.type == 2].cash.sum()
    mo = tr.groupby(tr.t.dt.strftime("%Y-%m")).cash.sum()
    worst = dd.groupby(dd.index.strftime("%Y-%m")).min()
    out = dict(acct=n, currency=m["currency"], contract_fit=round(cs, 2), first=str(x.t.min().date()), last_px=str(hrs[-1]),
               deposits_net_usd=round(float(flows)), balance_usd=round(m["balance"] / k), bd_realized_usd=round(float(tr.cash.sum())),
               max_mtm_dd_pct=round(float(dd.min() * 100), 1), max_dd_at=str(dd.idxmin()),
               monthly=pd.DataFrame({"bd_usd": mo.round(0), "worst_mtm_dd_pct": (worst.reindex(mo.index) * 100).round(1)}).T.to_dict())
    print(json.dumps(out, default=str))


if __name__ == "__main__":
    for a in sys.argv[1:]:
        n, d = a.split(":"); run(int(n), d)
