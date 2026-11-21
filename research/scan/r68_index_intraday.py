"""Round 68 (prereg docs/prereg/r68_index_intraday_scan.md, commit e14ec8e): 11 session-based intraday rules x 4 indices + baskets.
Usage: py -3.12 research/scan/r68_index_intraday.py dev|test"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan"); sys.path.insert(0, "research/stable")
from scan import tcost, E, scale
from scan2 import mismatch
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
SPAN = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2026-12-31")
TD = pd.Timedelta; IDX = ["DE40Cash", "US500Cash", "USTECHCash", "US30Cash"]

def session(s, d):
    if s == "DE40Cash": return d + TD(hours=10), d + TD(hours=18, minutes=25)
    k = 6 if mismatch(d) else 7
    return d + TD(hours=9 + k, minutes=30), d + TD(hours=15 + k, minutes=55)

def build(s):
    m = pd.read_csv(f"data/derived/scan/m5/{s}.csv"); m.index = pd.to_datetime(m.time, unit="s"); m = m[~m.index.duplicated()]
    tc = tcost(s, m.resample("1h").last().dropna()); pt = E.loc["." + s, "point"]
    P = m.open; S = m.spread * pt / m.open
    c = lambda t: max(tc, S.get(t, 0))
    D = []
    for d in sorted(set(m.index.normalize())):
        if d.dayofweek > 4: continue
        O, X = session(s, d); H1 = O + TD(hours=1); M = O + ((X - O) / 2).round("5min"); L = X - TD(hours=1)
        blocks = list(pd.date_range(O, X, freq="1h")) + ([X] if (X - O) % TD(hours=1) else [])
        pts = [O, H1, M, L, X] + blocks
        if not all(t in P.index for t in pts): continue
        fh = m.loc[O:H1 - TD(minutes=5)]
        D.append(dict(d=d, O=P[O], H1=P[H1], M=P[M], L=P[L], X=P[X], rng=(fh.high.max() - fh.low.min()) / P[O],
                      cO=c(O), cH1=c(H1), cM=c(M), cL=c(L), cX=c(X),
                      blk=[P[b2] / P[b1] - 1 for b1, b2 in zip(blocks[:-1], blocks[1:])], cblk=[c(b) for b in blocks]))
    D = pd.DataFrame(D).set_index("d")
    r = lambda a, b: D[b] / D[a] - 1
    sess = r("O", "X"); prevX = D.X.shift(1)
    out = {}
    def trade(sig, a, b, ca, cb, name):
        sig = sig.fillna(0); net = sig * r(a, b) - sig.abs() * (D[ca] + D[cb]); out[name] = (net, (sig.abs() * (D[ca] + D[cb])))
    trade(np.sign(r("O", "H1")), "H1", "X", "cH1", "cX", "1_fh_mom")
    trade(-np.sign(r("O", "H1")), "H1", "X", "cH1", "cX", "2_fh_rev")
    trade(np.sign(r("O", "L")), "L", "X", "cL", "cX", "3_lasthour_mom")
    trade(-np.sign(r("O", "M")), "M", "X", "cM", "cX", "4_pm_rev")
    trade(np.sign(sess.shift(1)), "O", "X", "cO", "cX", "5_day_cont")
    trade(-np.sign(sess.shift(1)), "O", "X", "cO", "cX", "6_day_rev")
    gap = np.sign(D.O / prevX - 1)
    trade(gap, "O", "X", "cO", "cX", "7_gap_cont")
    trade(-gap, "O", "H1", "cO", "cH1", "8_gap_fade_1h")
    big = D.rng > 1.5 * D.rng.rolling(20).mean().shift(1)
    trade(np.sign(r("O", "H1")).where(big, 0), "H1", "X", "cH1", "cX", "9_range_exp")
    dow = pd.Series(D.index.dayofweek, D.index)
    trade(np.sign(sess.groupby(dow).transform(lambda x: x.rolling(150, min_periods=100).mean().shift(1))), "O", "X", "cO", "cX", "10_dow")
    B = pd.DataFrame(D.blk.tolist(), index=D.index); CB = pd.DataFrame(D.cblk.tolist(), index=D.index)
    sg = np.sign(B.rolling(60, min_periods=40).mean().shift(1)).fillna(0)
    prev = pd.concat([pd.Series(0, index=D.index, name=-1), sg], axis=1); nxt = pd.concat([sg, pd.Series(0, index=D.index)], axis=1)
    turns = (nxt.values - prev.values)
    cost = (np.abs(turns) * CB.values[:, :turns.shape[1]]).sum(1)
    out["11_hour_wf"] = ((sg * B).sum(1) - cost, pd.Series(cost, index=D.index))
    return out

def stats(net, cost):
    x = net[SPAN[0]:SPAN[1]]; cst = cost[SPAN[0]:SPAN[1]]
    full = x.reindex(pd.bdate_range(x.index[0], x.index[-1])).fillna(0)
    sh = full.mean() / full.std() * np.sqrt(252); yrs = len(full) / 252
    y = x.groupby(x.index.year).sum()
    return dict(sh=sh, t=sh * np.sqrt(yrs), pos=(y > 0).mean(), npos=int((y > 0).sum()), ny=len(y),
                nc=x.sum() / cst.sum() if cst.sum() > 0 else np.nan, n=int((cst > 0).sum()), bp=x[cst > 0].mean() * 1e4), full

if __name__ == "__main__":
    C1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.pct_change()
    from book_tester import i2_daily
    I2 = i2_daily(); res = {s: build(s) for s in IDX}; rows = []
    rules = list(res[IDX[0]])
    for k in rules:
        for s in IDX + ["BASKET"]:
            if s == "BASKET":
                nets = pd.concat([scale(res[i][k][0].reindex(pd.bdate_range("2017-12-01", "2026-12-31")).fillna(0)) for i in IDX], axis=1).mean(1)
                costs = pd.concat([res[i][k][1] for i in IDX], axis=1).fillna(0).mean(1).reindex(nets.index).fillna(0)
                st, full = stats(nets[nets.ne(0).idxmax():], costs)
            else: st, full = stats(*res[s][k])
            cc = max(abs(pd.concat([full, o], axis=1).dropna().corr().iloc[0, 1]) for o in (C1, I2))
            rows.append(dict(rule=k, sym=s, **{a: round(b, 2) for a, b in st.items()}, cc=round(cc, 2)))
    R = pd.DataFrame(rows); pd.set_option("display.width", 200)
    if PER == "dev":
        R["pass"] = (R.t >= 2.5) & (R.pos >= 0.6) & (R.nc >= 3) & (R.cc <= 0.3)
        R.to_csv("data/derived/scan/r68_dev.csv", index=False)
    else:
        dv = pd.read_csv("data/derived/scan/r68_dev.csv"); R = R.merge(dv[["rule", "sym", "pass"]], on=["rule", "sym"])
        R["ho_ok"] = (R.sh >= 0.5) & (R.npos >= 3)
    print(R.to_string(index=False))
