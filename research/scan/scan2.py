"""Scan round 2 of docs/SCAN_PLAN.md (pre-registered 10.11.2026 night): P0 = I2 as now (fixed server bars 16..22),
P1 = I2 + DST fix (bars 15..21 in the US/EU DST-mismatch weeks), P2 = paper base exit (hold until the opposite band),
P3 = P1 + VWAP trailing stop (paper), P4 = P1 rule on BTCUSD. dev = 12/2017..2022, test = 2023..now (run once).
Usage: python research/scan/scan2.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"

def sunday(y, m, d0, last=False):
    """first Sunday on/after (y,m,d0), or the last Sunday of the month when last=True"""
    if last:
        t = pd.Timestamp(y, m, 1) + pd.offsets.MonthEnd(0); return t - pd.Timedelta(days=(t.dayofweek + 1) % 7)
    t = pd.Timestamp(y, m, d0); return t + pd.Timedelta(days=(6 - t.dayofweek) % 7)

def mismatch(d):
    y = d.year
    return (sunday(y, 3, 8) <= d < sunday(y, 3, 0, True)) or (sunday(y, 10, 0, True) <= d < sunday(y, 11, 1))

def run(h, tc, mode, dst, lb=14, n_chk=6):
    day = h.index.normalize()
    P = {f: h[f].to_frame("v").assign(d=day, k=h.index.hour).pivot_table(index="d", columns="k", values="v")
         for f in ("open", "high", "low", "close", "tick_volume")}
    D = P["close"].index
    sh = np.array([-1 if (dst and mismatch(d)) else 0 for d in D])
    o_hr = 16 + sh
    ok, C, O, V, TP = [], [], [], [], []
    for i, d in enumerate(D):
        hrs = list(range(o_hr[i], o_hr[i] + n_chk + 1))
        if not all(k in P["close"].columns for k in hrs): ok.append(False); C.append(None); O.append(np.nan); V.append(None); TP.append(None); continue
        c = P["close"].loc[d, hrs].values; o = P["open"].loc[d, o_hr[i]]
        tp = (P["high"].loc[d, hrs].values + P["low"].loc[d, hrs].values + c) / 3; v = P["tick_volume"].loc[d, hrs].values
        good = np.isfinite(c).all() and np.isfinite(o)
        ok.append(good); C.append(c); O.append(o); V.append(v); TP.append(tp)
    idx = [i for i in range(len(D)) if ok[i]]
    Cm = np.array([C[i] for i in idx]); Om = np.array([O[i] for i in idx]); Dd = D[idx]
    Vm = np.array([V[i] for i in idx]); TPm = np.array([TP[i] for i in idx])
    M = np.abs(Cm[:, :n_chk] / Om[:, None] - 1)
    S = pd.DataFrame(M).rolling(lb).mean().shift(1).values
    out = np.zeros(len(Dd))
    for i in range(lb + 2, len(Dd)):
        prev = Cm[i - 1, -1]
        if np.isnan(S[i]).any(): continue
        up, lo = max(Om[i], prev), min(Om[i], prev)
        cv = np.cumsum(np.nan_to_num(TPm[i] * Vm[i])); vv = np.cumsum(np.nan_to_num(Vm[i])); vw = np.where(vv > 0, cv / np.maximum(vv, 1e-12), Cm[i])
        q = 0; r = 0.0; last = None
        for j in range(n_chk + 1):
            c = Cm[i, j]
            if last is not None and q: r += q * (c / last - 1)
            last = c
            if j == n_chk: nq = 0
            else:
                U, L = up * (1 + S[i, j]), lo * (1 - S[i, j]); sig = 1 if c > U else (-1 if c < L else 0)
                if mode == "i2": nq = sig
                elif mode == "paper": nq = sig if (q == 0 or sig == -q) else q
                else:   # vwap trailing stop
                    if q == 1: nq = -1 if sig == -1 else (1 if c >= max(U, vw[j]) else 0)
                    elif q == -1: nq = 1 if sig == 1 else (-1 if c <= min(L, vw[j]) else 0)
                    else: nq = sig
            r -= abs(nq - q) * tc; q = nq
        out[i] = r
    return pd.Series(out, index=Dd)

if __name__ == "__main__":
    span = ("2017-12-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    print(f"===== round 2 {PER} {span}")
    u = load("USTECHCash"); tu = tcost("USTECHCash", u)
    b = load("BTCUSD"); tb = tcost("BTCUSD", b)
    print(f"cost per side: USTECH {tu*100:.4f}%  BTC {tb*100:.4f}%")
    for nm, h, tc, mode, dst in (("P0 I2 now", u, tu, "i2", False), ("P1 I2+DST", u, tu, "i2", True),
                                 ("P2 paper", u, tu, "paper", True), ("P3 vwap", u, tu, "vwap", True), ("P4 BTC", b, tb, "i2", True)):
        x = scale(run(h, tc, mode, dst)); x.to_csv(f"data/derived/scan/R2_{nm.split()[0]}_daily.csv", header=["ret"])
        rep(x.loc[span[0]:span[1]], nm)
