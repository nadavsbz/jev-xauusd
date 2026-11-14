"""Scan rounds 28-30 of docs/SCAN_PLAN.md (pre-registered together 12.11.2026 night).
Usage: python research/scan/r28_30.py [dev|test] [28 29 30]"""
import glob, os, sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep, trend, E, NONSTOCK, H
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
WHICH = sys.argv[2:] or ["28", "29", "30"]
SPAN = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
SWL, SWS = 0.06, 0.03

def corr_rep(x, tag, name):
    x.to_csv(f"data/derived/scan/{tag}_daily.csv", header=["ret"])
    print(f"===== {name} {PER}"); rep(x.loc[SPAN[0]:SPAN[1]], tag)
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
    j = pd.concat([x, i2, c1], axis=1, keys=["X", "I2", "C1"]).loc[SPAN[0]:SPAN[1]].dropna(subset=["X"]).fillna(0)
    print("    corr:", j.corr().round(2).loc["X"].to_dict())

def daily_closes():
    syms = [os.path.basename(f)[:-4] for f in glob.glob(f"{H}/*.csv")]
    syms = [s for s in syms if s not in NONSTOCK]
    C, TC = {}, {}
    for s in syms:
        h = load(s); C[s] = h.close.groupby(h.index.normalize()).last(); TC[s] = tcost(s, h)
    return pd.DataFrame(C).sort_index(), pd.Series(TC)

def r28():
    C, TC = daily_closes()
    wk = C.groupby(C.index.to_period("W-FRI")).tail(1)              # last trading day of each week
    out = {}
    for a, b, c in zip(wk.index[:-2], wk.index[1:-1], wk.index[2:]):
        past = wk.loc[b] / wk.loc[a] - 1; fwd = wk.loc[c] / wk.loc[b] - 1
        ok = past.notna() & fwd.notna()
        if ok.sum() < 20: continue
        p = past[ok].sort_values(); k = max(1, len(p) // 5)
        lo, hi = p.index[:k], p.index[-k:]
        days = (c - b).days
        r = 0.5 * fwd[lo].mean() - 0.5 * fwd[hi].mean() - 0.5 * 2 * TC[lo].mean() - 0.5 * 2 * TC[hi].mean() \
            - 0.5 * SWL * days / 365 - 0.5 * SWS * days / 365
        out[c] = r
    ev = pd.Series(out); full = pd.Series(0.0, index=pd.bdate_range(ev.index[0], ev.index[-1])); full.loc[ev.index] = ev
    y = ev.loc[SPAN[0]:SPAN[1]]
    print(f"    weeks {len(y)}, mean net {y.mean()*1e4:.1f} bp/week, t {y.mean()/y.std()*np.sqrt(len(y)):.2f}")
    corr_rep(scale(full), "R28_strev", "round 28 weekly cross-sectional reversal (stocks)")

def r29():
    x = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BRENT", "WTI"))
    corr_rep(x, "R29_oiltrend", "round 29 C1 trend rule on BRENT+WTI")

def r30():
    C, TC = daily_closes()
    pairs = [("KO", "PEP"), ("XOM", "CVX"), ("JPM", "BAC"), ("C", "WFC"), ("MCD", "SBUX"), ("PFE", "JNJ")]
    tot = []
    for A, B in pairs:
        d = C[[A, B]].dropna(); la, lb = np.log(d[A]), np.log(d[B])
        pos = 0; age = 0; rets = pd.Series(0.0, index=d.index); idx = d.index
        for i in range(252, len(idx) - 1):
            wa, wb = la.iloc[i - 252:i], lb.iloc[i - 252:i]
            s_hist = (wa - wa.iloc[0]) - (wb - wb.iloc[0]); sd = s_hist.std()
            s_now = (la.iloc[i] - wa.iloc[0]) - (lb.iloc[i] - wb.iloc[0]) - s_hist.mean()
            if pos != 0:
                age += 1
                if np.sign(s_now) != np.sign(pos * -1) or age >= 20:   # crossed zero or timed out
                    rets.iloc[i] -= 2 * (TC[A] + TC[B]) / 2; pos = 0; age = 0
            if pos == 0 and abs(s_now) > 2 * sd:
                pos = -int(np.sign(s_now)); age = 0; rets.iloc[i] -= 2 * (TC[A] + TC[B]) / 2
            if pos != 0:      # hold to next close: pos=+1 means long A short B
                ra = d[A].iloc[i + 1] / d[A].iloc[i] - 1; rb = d[B].iloc[i + 1] / d[B].iloc[i] - 1
                days = (idx[i + 1] - idx[i]).days
                rets.iloc[i + 1] += 0.5 * pos * (ra - rb) - 0.5 * (SWL + SWS) * days / 365
        tot.append(rets.rename(f"{A}/{B}"))
        y = rets.loc[SPAN[0]:SPAN[1]]; print(f"    {A}/{B}: sum {y.sum()*100:6.1f}%  Sh {y.mean()/y.std()*np.sqrt(252) if y.std() else 0:5.2f}")
    P = pd.concat(tot, axis=1).fillna(0).mean(axis=1)
    corr_rep(scale(P), "R30_pairs", "round 30 distance-method pairs (6 fixed pairs)")

if __name__ == "__main__":
    for k in WHICH: globals()[f"r{k}"]()
