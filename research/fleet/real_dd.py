"""MASTER_PLAN 4.3, metric 4 (real side): the maximum drawdown of each live account, rebuilt from its real deals
(read-only export, data/raw/<account>/<snapshot>/deals.csv) and the broker's M1 bars, the same way as the tester
side (research/mgmt/chain.py: the book valued at the bar's low and at its high, sells at the ask; worse total).

Balance operations: a withdrawal is moved to the safe base (the total keeps it, so it is not a drawdown); a deposit
adds capital (the peak rises with it). Positions in other symbols (e.g. silver) are counted when closed only,
their floating is not known (the share is reported). Output: docs/evidence/fleet_real_dd.json, accounts by their
report label (#1..#8), never by number.
Usage: python research/fleet/real_dd.py"""
import glob, json, os, sys
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
K = 100.0
ACC = {"#1": ("black_dragon_1", "eglobal"), "#2": ("black_dragon_2", "robo"), "#3": ("black_dragon_3", "robo"),
       "#4": ("btc_bot_4", "robo"), "#5": ("black_dragon_5", "robo"), "#6": ("black_dragon_6", "robo"),
       "#8": ("black_dragon_8", "eglobal")}
# the window the user's report covers (manual_report.xlsx: first row of the account .. 16.7.2026); A4 compares
# the simulator with the account inside this window only. The full history is reported too.
WINDOW = {"#1": "2025-11-12", "#2": "2026-04-07", "#3": "2026-02-27", "#4": "2026-04-13", "#5": "2026-04-15",
          "#6": "2026-04-15", "#8": "2026-05-29"}
WINDOW_END = "2026-07-16"


def bars(kind):
    pat = {"eglobal": "data/raw/black_dragon_1/rates_XAUUSDc_M1_*/bars.csv",
           "robo": "data/raw/black_dragon_3/rates_XAUUSD_M1_*/bars.csv"}[kind]
    b = pd.read_csv(sorted(glob.glob(os.path.join(ROOT, pat)))[-1])
    point = 0.001 if kind == "eglobal" else 0.01
    return b.time.values.astype(np.int64), b.low.values, b.high.values, b.spread.values * point


def account(folder, kind, start=None):
    snap = sorted(d for d in glob.glob(os.path.join(ROOT, "data", "raw", folder, "2*")) if os.path.isdir(d))[-1]
    d = pd.read_csv(os.path.join(snap, "deals.csv")).sort_values("time_msc")
    bal = d[d.type == 2]; tr = d[d.type.isin([0, 1])].copy()
    tr["net"] = tr.profit + tr.commission + tr.swap + tr.fee
    gold = tr.symbol.astype(str).str.startswith("XAUUSD")
    bt, lo, hi, ask = bars(kind)
    t0 = int(d.time.min()); t1 = int(d.time.max())
    a0 = np.searchsorted(bt, t0, "left"); a1 = np.searchsorted(bt, t1, "right")
    tt = bt[a0:a1]; L, H, A = lo[a0:a1], hi[a0:a1], ask[a0:a1]
    if len(tt) == 0 or bt[0] > t0 + 86400 * 3:
        return {"error": "bars do not cover the account's history", "first_deal": str(pd.to_datetime(t0, unit="s"))}
    cash = np.zeros(len(tt)); safe = np.zeros(len(tt)); fl_lo = np.zeros(len(tt)); fl_hi = np.zeros(len(tt))
    for r in bal.itertuples():                       # deposits raise the cash, withdrawals go to the safe base
        k = np.searchsorted(tt, r.time, "left")
        cash[k:] += r.profit
        if r.profit < 0:
            safe[k:] += -r.profit
    for r in tr.itertuples():                        # every deal's money lands when it happens
        cash[np.searchsorted(tt, r.time, "left"):] += r.net
    n_float = 0
    for pid, g in tr[gold & (tr.position_id > 0)].groupby("position_id"):
        ins = g[g.entry == 0]
        if ins.empty:
            continue
        side = 1 if ins.type.iloc[0] == 0 else -1; vol = ins.volume.sum(); p0 = (ins.price * ins.volume).sum() / vol
        i = max(np.searchsorted(tt, ins.time.min(), "right") - 1, 0)
        outs = g[g.entry == 1]
        j = np.searchsorted(tt, outs.time.max(), "left") if len(outs) else len(tt)
        add = 0.0 if side == 1 else A[i:j]
        fl_lo[i:j] += side * vol * (L[i:j] + add - p0) * K
        fl_hi[i:j] += side * vol * (H[i:j] + add - p0) * K
        n_float += 1
    worst = cash + np.minimum(fl_lo, fl_hi) + safe; best = cash + np.maximum(fl_lo, fl_hi) + safe
    # a deposit is new capital, not a gain: the peak is measured on the total minus the cumulated deposits
    dep = np.zeros(len(tt))
    for r in bal[bal.profit > 0].itertuples():
        dep[np.searchsorted(tt, r.time, "left"):] += r.profit
    with np.errstate(divide="ignore", invalid="ignore"):
        peak = np.maximum.accumulate(best - dep) + dep
        dd = np.where(peak > 0, (worst - peak) / peak, 0.0)
    k = int(np.argmin(dd))
    win = {}
    if start:
        w0 = np.searchsorted(tt, int(pd.Timestamp(start).timestamp()), "left")
        w1 = np.searchsorted(tt, int(pd.Timestamp(WINDOW_END).timestamp()), "right")
        wp = np.maximum.accumulate(best[w0:w1] - dep[w0:w1]) + dep[w0:w1]
        wd = (worst[w0:w1] - wp) / wp; kw = int(np.argmin(wd))
        win = {"window": [start, WINDOW_END], "window_max_dd": round(float(wd[kw]), 4),
               "window_max_dd_at": str(pd.to_datetime(int(tt[w0 + kw]), unit="s"))}
    return {**win,"from": str(pd.to_datetime(t0, unit="s").date()), "to": str(pd.to_datetime(t1, unit="s").date()),
            "max_dd": round(float(dd[k]), 4), "max_dd_at": str(pd.to_datetime(int(tt[k]), unit="s")),
            "gold_positions_floating": n_float, "non_gold_deals": int((~gold).sum()),
            "deposits": round(float(bal[bal.profit > 0].profit.sum()), 2),
            "withdrawals": round(float(-bal[bal.profit < 0].profit.sum()), 2)}


def main():
    out = {}
    for label, (folder, kind) in ACC.items():
        try:
            out[label] = account(folder, kind, WINDOW.get(label))
        except Exception as e:                       # one account's failure must not hide the others
            out[label] = {"error": f"{type(e).__name__}: {e}"}
        print(label, out[label], flush=True)
    json.dump(out, open(os.path.join(ROOT, "docs", "evidence", "fleet_real_dd.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
