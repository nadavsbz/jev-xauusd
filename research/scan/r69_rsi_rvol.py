"""Round 69 (prereg docs/prereg/r69_rsi_rvol_reversal.md, commit 96b5c9a): RSI(14) H1 cross-up of 30 + RVOL>=1.5, long, US stocks.
Usage: py -3.12 research/scan/r69_rsi_rvol.py dev|test"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan"); sys.path.insert(0, "research/stable")
from scan import tcost, E, scale
from r64_mass import loadh, cls, swaps
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
SPAN = ("2000-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2026-12-31")

def rsi(c, n=14):
    d = c.diff(); u = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(); v = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + u / v.replace(0, np.nan))

def run(s, sl, use_rvol):
    h = loadh(s); tc = tcost(s, h); swl, _ = swaps(s, float(h.close.iloc[-1]))
    R = rsi(h.close); hr = h.index.hour
    vol = h.tick_volume.astype(float)
    rv = vol / vol.groupby(hr).transform(lambda x: x.rolling(20, min_periods=15).mean().shift(1))
    sig = (R.shift(1) < 30) & (R >= 30) & (hr >= 17) & (hr <= 22)
    if use_rvol: sig &= rv >= 1.5
    O, Hi, Lo, C = h.open.values, h.high.values, h.low.values, h.close.values; T = h.index; days = T.normalize()
    sidx = np.flatnonzero(sig.values); trades = []; busy = -1
    for i in sidx:
        e = i + 1
        if e <= busy or e >= len(h): continue
        px = O[e]; stop = px * (1 - sl); peak = px; trail = False; d0 = days[e]; j = e; exit_px = None
        ndays = 0; lastday = d0
        END = pd.Timestamp(SPAN[1]) + pd.Timedelta(hours=23, minutes=59)   # Codex P1 15.11: no price after the span end
        if T[e] > END: break
        while j < len(h):
            if T[j] > END: j -= 1; exit_px = C[j]; break
            if days[j] != lastday: ndays += 1; lastday = days[j]
            if Lo[j] <= stop: exit_px = min(stop, O[j]) if O[j] < stop else stop; break
            peak = max(peak, C[j])
            if not trail and C[j] >= px * 1.03: trail = True
            if trail and C[j] <= peak * 0.98: exit_px = C[j]; break
            if ndays >= 7 and C[j] < px and T[j].hour >= 22: exit_px = C[j]; break
            if ndays >= 20 and T[j].hour >= 22: exit_px = C[j]; break
            j += 1
        if exit_px is None: break
        nights = (days[j] - d0).days
        g = exit_px / px - 1; cost = 2 * tc; sw = swl * nights / 365
        trades.append((T[e], days[j], g - cost + sw, cost - min(sw, 0)))
        busy = j
    return pd.DataFrame(trades, columns=["t", "x", "net", "cost"])

def evaluate(name, sl, use_rvol, C1, I2):
    stocks = [x for x in E.index if cls(x) == "stock"]; allt = []; book = []
    for s in stocks:
        T = run(s, sl, use_rvol)
        if not len(T): continue
        T["s"] = s; allt.append(T)
    A = pd.concat(allt); A = A[(A.t >= SPAN[0]) & (A.t <= SPAN[1] + " 23:59")]
    # daily book: each trade's return spread evenly over its holding days, averaged over open trades
    rows = []
    for _, r in A.iterrows():
        dd = pd.bdate_range(r.t.normalize(), r.x)
        if len(dd): rows.append(pd.Series((1 + r.net) ** (1 / len(dd)) - 1, index=dd))
    M = pd.concat(rows, axis=1); bk = scale(M.mean(1).fillna(0))
    bk = bk[bk.ne(0).idxmax():]
    sh = bk.mean() / bk.std() * np.sqrt(252); t = A.net.mean() / A.net.std() * np.sqrt(len(A))
    y = A.groupby(A.t.dt.year).net.sum(); nc = A.net.sum() / A.cost.sum()
    cc = max(abs(pd.concat([bk, o], axis=1).dropna().corr().iloc[0, 1]) for o in (C1, I2))
    print(f"[{name}] n {len(A)}  net {A.net.mean()*1e4:.1f} bp  cost {A.cost.mean()*1e4:.1f}  hit {(A.net>0).mean():.2f}  t {t:.2f}  book Sh(UNVERIFIED, smoothed) {sh:.2f}  pos {int((y>0).sum())}/{len(y)}  net/cost {nc:.2f}  corr {cc:.2f}")
    print("      years bp/trade:", " ".join(f"{a%100:02d}:{v*1e4:+.0f}" for a, v in A.groupby(A.t.dt.year).net.mean().items()))
    return dict(t=t, sh=sh, pos=(y > 0).mean(), npos=int((y > 0).sum()), nc=nc, cc=cc)

if __name__ == "__main__":
    C1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.pct_change()
    from book_tester import i2_daily
    I2 = i2_daily(); print(f"===== {PER} {SPAN}")
    for nm, sl, rv in [("V1 SL0.5%", 0.005, True), ("V2 SL5%", 0.05, True), ("V1 no-RVOL (desc)", 0.005, False), ("V2 no-RVOL (desc)", 0.05, False)]:
        st = evaluate(nm, sl, rv, C1, I2)
        if "desc" not in nm:
            ok = (st["t"] >= 2.5 and st["pos"] >= 0.6 and st["nc"] >= 3 and st["cc"] <= 0.3) if PER == "dev" else (st["sh"] >= 0.5 and st["npos"] >= 3)
            print("      gate:", "PASS" if ok else ("KILL" if PER == "dev" else "FAIL"))
