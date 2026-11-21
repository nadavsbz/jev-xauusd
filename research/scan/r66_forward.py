"""Paper-only forward tracking of round 66 idea C (pension rebalance), agreed with Grok 15.11.2026 (grok_inbox 19:35).
Same rule as prereg 6932265: gap = SPY MTD - TLT MTD at the close of the 6th-last trading day; |gap|>2% -> trade against it on SPX
for the last 5 trading days. No account, no orders. Decision after 24 events: Sh>=0.5 and net/cost>=5, else KILL.
Refreshes Yahoo data, writes docs/agents/grok_data/forward_r66.csv (one row per month from 2026-11). Usage: py -3.12 research/scan/r66_forward.py"""
import sys, csv, time, os
import numpy as np, pandas as pd
sys.path.insert(0, "research/third")
from fetch_yahoo import fetch
OUT = "docs/agents/grok_data/forward_r66.csv"; START = "2026-11"
TC, SWL, SWS = 2.56e-5 + 0.00005, -0.086, -0.018

def series(sym, adj):
    r = fetch(sym); q = r["indicators"]; v = q["adjclose"][0]["adjclose"] if adj else q["quote"][0]["close"]
    s = pd.Series(v, index=pd.to_datetime([time.strftime("%Y-%m-%d", time.gmtime(t + r["meta"].get("gmtoffset", 0))) for t in r["timestamp"]]))
    return s.dropna()[~s.dropna().index.duplicated()]

spy, tlt, spx = series("SPY", True), series("TLT", True), series("%5EGSPC", False)
idx = spx.index.intersection(spy.index).intersection(tlt.index)
def nyse_holidays(y):
    """NYSE full-day closures (Codex P1 15.11: the federal calendar is not the exchange calendar)."""
    from dateutil.easter import easter
    def obs(d, newyear=False):
        if d.dayofweek == 5: return None if newyear else d - pd.Timedelta(days=1)
        return d + pd.Timedelta(days=1) if d.dayofweek == 6 else d
    def nth(m, wd, k):
        r = pd.date_range(f"{y}-{m:02d}-01", periods=31, freq="D"); return r[(r.month == m) & (r.dayofweek == wd)][k]
    h = [obs(pd.Timestamp(f"{y}-01-01"), True), nth(1, 0, 2), nth(2, 0, 2), pd.Timestamp(easter(y)) - pd.Timedelta(days=2), nth(5, 0, -1),
         obs(pd.Timestamp(f"{y}-07-04")), nth(9, 0, 0), nth(11, 3, 3), obs(pd.Timestamp(f"{y}-12-25"))]
    if y >= 2022: h.append(obs(pd.Timestamp(f"{y}-06-19")))
    return {d for d in h if d is not None}
rows = []
for mo in pd.period_range(START, pd.Timestamp.today().to_period("M")):
    hol = nyse_holidays(mo.year)
    td = [d for d in pd.bdate_range(mo.start_time, mo.end_time) if d not in hol]
    done = [d for d in idx if mo.start_time <= d <= mo.end_time]
    if done and pd.Timestamp.today().normalize() > mo.end_time: td = done          # completed month: actual trading days
    dec, ex = td[-6], td[-1]
    base = idx[idx < mo.start_time][-1]
    row = dict(month=str(mo), decision_day=dec.date(), exit_day=ex.date(), gap=None, side=None, net_bp=None, status="pending")
    if dec in idx:
        gap = (spy[dec] / spy[base] - 1) - (tlt[dec] / tlt[base] - 1); side = 0 if abs(gap) <= 0.02 else -int(np.sign(gap))
        row.update(gap=round(gap, 4), side=side, status="no trade" if side == 0 else "open")
        if side and ex in idx:
            sw = (SWL if side > 0 else SWS) * (ex - dec).days / 365
            row.update(net_bp=round((side * (spx[ex] / spx[dec] - 1) - 2 * TC + sw) * 1e4, 1), status="closed")
    rows.append(row)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pd.DataFrame(rows).to_csv(OUT, index=False); print(pd.DataFrame(rows).to_string(index=False))
