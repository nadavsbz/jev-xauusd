"""Round 89 (prereg docs/prereg/r89_btc_weekend_monday.md): BTC weekend move -> US500/USTECH first trading day of the week, intraday.
Usage: py -3.12 research/scan/r89_btc_weekend.py dev|hold"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import tcost
from r64_mass import loadh
PART = sys.argv[1]
a, z = ("2018", "2022") if PART == "dev" else ("2023", "2026")
btc = loadh("BTCUSD").close
rows = {}
for s in (".US500Cash", ".USTECHCash"):
    h = loadh(s); tc = tcost(s.lstrip("."), h)
    day = h.index.normalize(); days = pd.Series(day.unique())
    gap = days.diff().dt.days
    out = []
    for i in range(1, len(days)):
        if gap.iloc[i] < 2: continue                      # first trading day after a weekend (or a holiday gap)
        d0, d1 = days.iloc[i - 1], days.iloc[i]
        prev = h[day == d0]; cur = h[day == d1]
        t_close, t_open = prev.index[-1], cur.index[0]
        b = btc[(btc.index > t_close - pd.Timedelta("1h")) & (btc.index < t_open)]
        if len(b) < 10: continue
        sig = b.iloc[-1] / b.iloc[0] - 1
        ret = cur.close.iloc[-1] / cur.open.iloc[0] - 1
        out.append((d1, sig, ret))
    D = pd.DataFrame(out, columns=["day", "sig", "ret"]).set_index("day")
    D["thr"] = D.sig.abs().rolling(52, min_periods=26).median().shift(1)
    D["net_f"] = np.where(D.sig.abs() >= D.thr, np.sign(D.sig) * D.ret - 2 * tc, np.nan)
    D["net_all"] = np.sign(D.sig) * D.ret - 2 * tc
    rows[s] = D[a:z]
def st(x):
    x = x.dropna(); return len(x), x.mean() * 1e4, x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan
allf = pd.concat([rows[s].net_f for s in rows])
for s, D in rows.items():
    n, m, t = st(D.net_f); n2, m2, t2 = st(D.net_all)
    print(f"{PART} {a}-{z} {s}: filtered n={n} mean {m:+.1f}bp t={t:.2f} | unfiltered n={n2} mean {m2:+.1f}bp t={t2:.2f} | corr(sig,ret)={D.sig.corr(D.ret):+.3f}")
n, m, t = st(allf)
per = [st(rows[s].net_f)[1] > 0 for s in rows]
ok = (m > 0 and t >= 2.0 and all(per)) if PART == "dev" else (m > 0 and t >= 1.5)
print(f"COMBINED n={n} mean {m:+.1f}bp t={t:.2f} -> {'PASS' if ok else 'FAIL'}")
