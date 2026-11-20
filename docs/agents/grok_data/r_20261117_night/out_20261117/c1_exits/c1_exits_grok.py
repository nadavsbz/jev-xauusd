"""C1 exit variants (PREREG_c1_exits_grok.md, sha 89acc43e...). Port of research/scan/r82_c1_exit.py BASE + E1/E2/E3.
Usage: python3 c1_exits_grok.py rf|binance dev|hold"""
import sys, json
import numpy as np, pandas as pd
SRC, PART = sys.argv[1], sys.argv[2]
D0 = "/workspace/research_new_component/data"
SWAP = -0.0475

def scale(r, target=0.10):                       # research/scan/scan.py
    v = r.rolling(90, min_periods=60).std().shift(1) * np.sqrt(252)
    return r * (target / v).clip(upper=5).fillna(0)

def st(x):                                       # research/scan/r77_c1_breadth.py
    x = x[x.ne(0).idxmax():]; eq = (1 + x).cumprod()
    return x.mean() / x.std() * np.sqrt(365), (eq / eq.cummax() - 1).min() * 100, x.groupby(x.index.year).sum().mul(100).round(0).to_dict()

def load(s):
    if SRC == "rf":
        h = pd.read_csv(f"{D0}/cfd_h1/{s}.csv"); h.index = pd.to_datetime(h.time, unit="s")
    else:
        h = pd.read_csv(f"{D0}/binance/{s}T_1h.csv"); h.index = pd.to_datetime(h.open_time_ms, unit="ms")
    h = h[~h.index.duplicated()].sort_index(); h = h[(h.close > 0) & (h.open > 0)]
    if SRC == "rf":
        x = h.loc["2026"]; sp = float((x.spread * 0.01 / x.close).median())
        tc = max(sp, 0.0001) + 0.00005
    else:
        tc = 0.0010
    return h, tc

def donch_v(o, long_only, mode):
    c = o.close; cv = c.values; r = c.pct_change().values
    sig = c.pct_change().rolling(60).std().values
    sigl = np.r_[np.nan, sig[:-1]]
    pc = c.shift(1)
    tr_ = pd.concat([o.high - o.low, (o.high - pc).abs(), (o.low - pc).abs()], axis=1).max(axis=1)
    atr = tr_.rolling(22).mean().values
    st_ = []
    for n in (10, 20, 30, 60, 90, 150, 250):
        hv, lv = c.rolling(n).max().values, c.rolling(n).min().values
        k = n // 2
        xl, xh = c.rolling(k).min().values, c.rolling(k).max().values
        p = np.zeros(len(c)); e = 0.0; ext = 0.0; tgt = 0.0; part = False; d = 0
        for i in range(1, len(c)):
            q = p[i - 1]
            if q == 0:
                d = 1 if cv[i] >= hv[i] else (-1 if (not long_only and cv[i] <= lv[i]) else 0)
                q = d
                if d != 0:
                    e, ext, part = cv[i], cv[i], False
                    tgt = (sig[i] if sig[i] == sig[i] else 0.0) * np.sqrt(n) * 2
            else:
                ext = max(ext, cv[i]) if d > 0 else min(ext, cv[i])
                chan = (d > 0 and cv[i] <= xl[i]) or (d < 0 and cv[i] >= xh[i])
                if mode == "BASE":
                    if chan: q = 0
                elif mode == "E1":
                    a = atr[i]
                    if a == a:
                        dist = 3 * a * np.sqrt(n / 22)
                        if (d > 0 and cv[i] <= ext - dist) or (d < 0 and cv[i] >= ext + dist): q = 0
                elif mode == "E2":
                    if chan: q = 0
                    elif not part and tgt > 0 and d * (cv[i] / e - 1) >= tgt: q = 0.5 * d; part = True
                elif mode == "E3":
                    if chan: q = 0
                    elif sigl[i] == sigl[i] and sigl[i] > 0 and d * r[i] <= -3 * sigl[i]: q = 0
            p[i] = q
        st_.append(p)
    return pd.Series(np.mean(st_, axis=0), index=c.index)

SY = ("BTCUSD", "ETHUSD")
D = {}
for s in SY:
    h, tc = load(s)
    o = pd.DataFrame({"open": h.open.resample("6h").first(), "high": h.high.resample("6h").max(),
                      "low": h.low.resample("6h").min(), "close": h.close.resample("6h").last()}).dropna()
    dt = o.index.to_series().diff().dt.total_seconds().fillna(0) / 86400 / 365
    D[s] = (o, tc, dt)

def run(mode):
    out = []; turn = []
    for s, (o, tc, dt) in D.items():
        c = o.close
        w = (0.5 * donch_v(o, True, mode) + 0.5 * donch_v(o, False, mode)).shift(2).fillna(0); r = c.pct_change().fillna(0)
        net = w * r - w.diff().abs().fillna(0) * tc + np.where(w > 0, w * SWAP, -w * SWAP) * dt
        out.append(scale((1 + net).groupby(net.index.normalize()).prod() - 1))
    return scale(pd.concat(out, axis=1, sort=True).fillna(0).mean(1))

a, z = ("2017", "2022") if PART == "dev" else ("2023", "2026")
modes = ("BASE",) if (len(sys.argv) > 3 and sys.argv[3] == "base") else ("BASE", "E1", "E2", "E3")
res = {m: run(m) for m in modes}
sb, mb, yb = st(res["BASE"][a:z])
rep = {"src": SRC, "part": PART, "tc": {s: D[s][1] for s in SY}, "BASE": {"sh": round(sb, 3), "mdd": round(mb, 2), "years": yb}}
print(f"{SRC} {PART} {a}-{z}: tc {rep['tc']} BASE Sh {sb:.2f} MDD {mb:.1f} | {yb}")
for m in modes[1:]:
    s_, m_, y_ = st(res[m][a:z])
    ok = (s_ >= sb + 0.10 and m_ >= mb) if PART == "dev" else (s_ >= sb + 0.05 and m_ >= mb - 1)
    cr = res[m][a:z].corr(res["BASE"][a:z])
    print(f"  {m}: Sh {s_:.2f} ({s_ - sb:+.2f}) MDD {m_:.1f} corr {cr:.2f} -> {'PASS' if ok else 'FAIL'} | {y_}")
    rep[m] = {"sh": round(s_, 3), "dsh": round(s_ - sb, 3), "mdd": round(m_, 2), "corr": round(cr, 3), "pass": bool(ok), "years": y_}
json.dump(rep, open(f"res_{SRC}_{PART}.json", "w"), indent=1, default=str)
