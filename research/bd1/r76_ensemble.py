"""Round 76 (prereg docs/prereg/r76_bd_balancer_ensemble.md, commit 03ea667): ChatGPT t271 ensemble (London ORB + pre-NY straddle +
trend-day chandelier) on XAUUSD M5, as a balancer for BD ms20_h1119. Usage: py -3.12 research/bd1/r76_ensemble.py dev|val|test"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/btc"); sys.path.insert(0, "research/scan")
from guardian_sim import deals
from scan import tcost
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
SPAN = {"dev": ("2016-01-01", "2021-12-31"), "val": ("2022-01-01", "2024-12-31"), "test": ("2025-01-01", "2025-12-31")}[PER]
RISK = {"orb": 0.00117, "str": 0.00083, "chn": 0.00100}

m = pd.read_csv("data/derived/scan/m5/XAUUSD.csv"); t = pd.to_datetime(m.time, unit="s")
utc = t.dt.tz_localize("Europe/Athens", ambiguous="NaT", nonexistent="NaT").dt.tz_convert("UTC")
m = m[utc.notna().values].copy(); m.index = pd.DatetimeIndex(utc[utc.notna()]).tz_localize(None); m = m[~m.index.duplicated()].sort_index()
lon = m.index.tz_localize("UTC").tz_convert("Europe/London").tz_localize(None)
m["lon"] = lon; m["sp"] = m.spread * 0.01
tc = tcost("XAUUSD", m.resample("1h").last().dropna())
H = m.resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
trh = pd.concat([H.high - H.low, (H.high - H.close.shift()).abs(), (H.low - H.close.shift()).abs()], axis=1).max(1)
atr_h1 = trh.rolling(20).mean().shift(1)                          # known at the start of each hour
D = m.resample("1D").agg({"high": "max", "low": "min", "close": "last"}).dropna()
trd = pd.concat([D.high - D.low, (D.high - D.close.shift()).abs(), (D.low - D.close.shift()).abs()], axis=1).max(1)
atr_d = trd.rolling(20).mean().shift(1)
Q = m.resample("15min").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
trq = pd.concat([Q.high - Q.low, (Q.high - Q.close.shift()).abs(), (Q.low - Q.close.shift()).abs()], axis=1).max(1)
atr_q = trq.rolling(14).mean()
ah = lambda ts: atr_h1.asof(ts.floor("h"))
cost = lambda row: max(tc * row.close, row.sp)

def manage(bars, d, entry, stop, R, end, risk, trail_atr=None, be_at=None, partial_at=None, chand=None):
    """walk bars after entry; returns pnl in equity fraction. stop checked first in each bar (conservative)."""
    best = entry; s = stop; half_done = False; pnl_r = 0.0; w = 1.0
    for ts, b in bars.iterrows():
        if ts >= end:
            pnl_r += w * d * (b.open - entry) / R; return risk * (pnl_r - cost(b) / R)
        if (d > 0 and b.low <= s) or (d < 0 and b.high >= s):
            px = min(s, b.open) if d > 0 else max(s, b.open)
            pnl_r += w * d * (px - entry) / R; return risk * (pnl_r - cost(b) / R)
        if partial_at and not half_done and d * (b.high if d > 0 else b.low) >= d * partial_at:
            pnl_r += 0.5 * d * (partial_at - entry) / R; w = 0.5; half_done = True
        best = max(best, b.close) if d > 0 else min(best, b.close)
        if be_at is not None and d * (b.close - entry) >= be_at: s = max(s, entry) if d > 0 else min(s, entry)
        if trail_atr is not None:
            a = ah(ts) * trail_atr
            if np.isfinite(a): s = max(s, best - a) if d > 0 else min(s, best + a)
        if chand is not None:
            a = 2 * atr_q.asof(ts)
            ext = bars.loc[:ts].high.max() if d > 0 else bars.loc[:ts].low.min()
            if np.isfinite(a): s = max(s, ext - a) if d > 0 else min(s, ext + a)
    return 0.0

def oco(win, hi_lvl, lo_lvl):
    for ts, b in win.iterrows():
        up, dn = b.high >= hi_lvl, b.low <= lo_lvl
        if up and dn: return ts, 0, None
        if up: return ts, 1, max(hi_lvl, b.open)
        if dn: return ts, -1, min(lo_lvl, b.open)
    return None, None, None

res = {}
days = pd.date_range(SPAN[0], SPAN[1], freq="D")
for day in days:
    g = m[(m.index >= day) & (m.index < day + pd.Timedelta(days=1))]
    if len(g) < 100: continue
    out = {"orb": 0.0, "str": 0.0, "chn": 0.0}
    ad = atr_d.get(day, np.nan)
    # leg 1: London ORB
    orw = g[(g.lon.dt.hour == 7)] if hasattr(g.lon, "dt") else g[(pd.DatetimeIndex(g.lon).hour == 7)]
    L = pd.DatetimeIndex(g.lon)
    orw = g[L.hour == 7]; after = g[(L.hour >= 8) & ((L.hour < 19) | ((L.hour == 19) & (L.minute < 30)))]
    if len(orw) >= 10 and len(after) and np.isfinite(ad):
        hi, lo = orw.high.max(), orw.low.min(); wdt = hi - lo; a = ah(after.index[0])
        if 0.35 * ad <= wdt <= 1.25 * ad and np.isfinite(a):
            ts, d, px = oco(after, hi + 0.10 * a, lo - 0.10 * a)
            end = after.index[-1] + pd.Timedelta(minutes=5)
            if d == 0: out["orb"] = -RISK["orb"]
            elif d:
                stop = lo - 0.10 * a if False else (lo if d > 0 else hi); R = abs(px - stop)
                if R > 0: out["orb"] = manage(after[after.index > ts], d, px, stop, R, end, RISK["orb"], trail_atr=1.0, be_at=wdt) - RISK["orb"] * cost(g.loc[ts]) / R
    # leg 2: straddle at 12:20 UTC
    rng = g[(g.index >= day + pd.Timedelta(hours=10, minutes=50)) & (g.index < day + pd.Timedelta(hours=12, minutes=20))]
    win = g[(g.index >= day + pd.Timedelta(hours=12, minutes=20)) & (g.index < day + pd.Timedelta(hours=20))]
    if len(rng) >= 12 and len(win) and np.isfinite(ad):
        hi, lo = rng.high.max(), rng.low.min(); a = ah(win.index[0])
        if hi - lo <= 1.2 * ad and np.isfinite(a):
            ts, d, px = oco(win, hi + 0.15 * a, lo - 0.15 * a)
            if d == 0: out["str"] = -RISK["str"]
            elif d:
                stop = lo if d > 0 else hi; R = abs(px - stop)
                if R > 0: out["str"] = manage(win[win.index > ts], d, px, stop, R, day + pd.Timedelta(hours=20), RISK["str"], trail_atr=1.0,
                                              partial_at=px + d * 1.5 * R) - RISK["str"] * cost(g.loc[ts]) / R
    # leg 3: trend-day chandelier
    t07, t1430 = day + pd.Timedelta(hours=7), day + pd.Timedelta(hours=14, minutes=30)
    qd = Q[(Q.index >= t07) & (Q.index < t1430)]
    if len(qd) >= 25 and t07 in g.index:
        p07 = g.open[t07]; pc = qd.close.iloc[-1]; a = ah(t1430); d = int(np.sign(pc - p07))
        day_rng = g[g.index < t1430]; dh, dl = day_rng.high.max(), day_rng.low.min()
        frac = ((np.sign(qd.close - qd.open) == d).mean()) if d else 0
        pos = (pc - dl) / (dh - dl) if dh > dl else 0.5
        if d and np.isfinite(a) and abs(pc - p07) > 1.25 * a and frac >= 0.70 and ((d > 0 and pos >= 0.75) or (d < 0 and pos <= 0.25)):
            eq_ = Q.index[Q.index >= t1430]
            if len(eq_):
                ets = eq_[0] + pd.Timedelta(minutes=15); px = Q.close.get(eq_[0], np.nan); aq = atr_q.asof(eq_[0])
                if np.isfinite(px) and np.isfinite(aq) and aq > 0:
                    stop = px - d * 2 * aq; R = 2 * aq
                    rest = g[(g.index >= ets) & (g.index < day + pd.Timedelta(hours=21))]
                    out["chn"] = manage(rest, d, px, stop, R, day + pd.Timedelta(hours=21), RISK["chn"], chand=True) - RISK["chn"] * cost(g.loc[g.index[g.index <= eq_[0]][-1]]) / R
    res[day] = out
Hd = pd.DataFrame(res).T; Hd["ens"] = Hd.sum(1); Hd.to_csv(f"data/derived/bd/r76_hedge_{PER}.csv")
# BD daily
out = []
for y in range(int(SPAN[0][:4]), int(SPAN[1][:4]) + 1):
    tag = "ev18" if y <= 2018 else "ev12"
    x = deals(f"C:/MT5_JEV_TEST/{tag}_rf{y}_ms20_h1119.htm"); x["day"] = pd.to_datetime(x.t, unit="s").dt.normalize()
    p = (x.profit + x.swap + x.commission).groupby(x.day).sum().reindex(pd.bdate_range(f"{y}-01-01", f"{y}-12-31")).fillna(0)
    eq = 120000 + p.cumsum(); out.append(p / eq.shift(1).fillna(120000))
bd = pd.concat(out); h = Hd.ens.reindex(bd.index).fillna(0)
print(f"===== {PER} {SPAN}  hedge legs total %:", (Hd[["orb", "str", "chn"]].sum() * 100).round(2).to_dict(), " trades:", (Hd[["orb", "str", "chn"]] != 0).sum().to_dict())
stops = bd[bd < -0.05]; inwin = pd.Series(False, index=bd.index); ev = []
for s in stops.index:
    k = bd.index.get_loc(s); idx = bd.index[max(0, k - 10):k + 1]; inwin[idx] = True; ev.append((h[idx].sum(), bd[s]))
ev = np.array(ev) if ev else np.zeros((0, 2))
catch = -ev[:, 0].sum() / ev[:, 1].sum() if len(ev) else np.nan
corr = np.corrcoef(ev[:, 0], ev[:, 1])[0, 1] if len(ev) >= 5 else np.nan
normal_cost = -h[~inwin].sum(); bd_normal = bd[~inwin].sum()
print(f"stop days {len(stops)}  catch {catch*100:.1f}%  corr(window hedge, stop loss) {corr:.2f}  hedge in windows {ev[:,0].sum()*100:.2f}%  BD stop losses {ev[:,1].sum()*100:.1f}%")
print(f"normal-day hedge P&L {-normal_cost*100:+.2f}%  BD normal-day {bd_normal*100:+.1f}%  cost share {normal_cost/bd_normal*100 if bd_normal>0 else np.nan:.1f}%")
for k in (0.5, 1.0, 1.5):
    cb = bd + k * h; rows = []
    for y, s in cb.groupby(cb.index.year):
        e = (1 + s).cumprod(); rows.append(f"{y%100:02d}:{(e.iloc[-1]-1)*100:+.0f}/{(e/e.cummax()-1).min()*100:.0f}")
    print(f"BD+{k}xH ret/MDD per year: " + "  ".join(rows))
e = (1 + bd).cumprod(); print("BD alone: " + "  ".join(f"{y%100:02d}:{((1+s).prod()-1)*100:+.0f}/{(((1+s).cumprod())/((1+s).cumprod()).cummax()-1).min()*100:.0f}" for y, s in bd.groupby(bd.index.year)))
