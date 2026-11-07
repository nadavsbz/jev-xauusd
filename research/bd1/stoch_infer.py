"""Which Stochastic rule did the original EA use? (docs/CRASH_LINK_PLAN.md, v13 validation failed: same_bar <= 0.45.)
Original EA baskets from the tester report lars_stoh_2022 (Lars set, Use_Stoh true, 80/20, K7 D1 slowing 2, M15).
M15 bars from Dukascopy XAUUSD 2022 ticks (data/raw/dukascopy, git-ignored), mid price, shifted to server time (Europe/Athens).
For every basket's first entry: the stochastic %K (and its EMA99 side) on the bar that opened it (0) and the last closed bar (1).
Usage: python research/bd1/stoch_infer.py"""
import glob, lzma, os, struct, sys, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd
sys.path[:0] = [os.path.join(os.path.dirname(__file__), "..", "btc"), os.path.dirname(__file__)]
import guardian_sim as g
from clone_vs_live import table

T, P = [], []
for f in sorted(glob.glob(os.path.join("data", "raw", "dukascopy", "XAUUSD", "2022", "*", "*", "*h_ticks.bi5"))):
    raw = open(f, "rb").read()
    if not raw: continue
    mo, d, h = f.split(os.sep)[-3], f.split(os.sep)[-2], os.path.basename(f)[:2]
    base = dt.datetime(2022, int(mo), int(d), int(h), tzinfo=dt.timezone.utc).timestamp()
    for ms, ask, bid, _, _ in struct.iter_unpack(">3I2f", lzma.decompress(raw)):
        T.append(base + ms / 1000); P.append((ask + bid) / 2000)
s = pd.Series(P, index=pd.to_datetime(T, unit="s", utc=True).tz_convert(ZoneInfo("Europe/Athens")).tz_localize(None))
m = s.resample("15min").ohlc().dropna()
def sto(k, d, sl):
    lo, hi = m.low.rolling(k).min(), m.high.rolling(k).max()
    return (100 * (m.close - lo).rolling(sl).sum() / (hi - lo).rolling(sl).sum()).rolling(d).mean()
K = sto(7, 1, 2); E = m.close.ewm(span=99, adjust=False).mean()
b = table(g.pair(g.deals("C:/MT5_JEV_TEST/lars_stoh_2022.htm"))[0])
b["bar"] = pd.to_datetime(b.t0, unit="s").dt.floor("15min")
i = m.index.get_indexer(b.bar)
ok = i > 1; b = b[ok]; i = i[ok]
b["k0"] = K.values[i]; b["k1"] = K.values[i - 1]; b["ema_side"] = np.where(m.close.values[i - 1] > E.values[i - 1], "buy", "sell")
print("baskets", len(b))
for sd, G in b.groupby("side"):
    print(f"\n{sd}: n={len(G)} | EMA side agrees {np.mean(G.ema_side == sd):.0%}")
    for c in ("k1", "k0"):
        q = G[c].quantile([.05, .25, .5, .75, .95]).round(1).tolist()
        edge = (G[c] < 20).mean() if sd == "buy" else (G[c] > 80).mean()
        print(f"  {c}: quantiles {q} | at its edge {edge:.0%}")

# Search: which stochastic definition puts (nearly) every basket at its edge? Close/close variant = Low/High from closes.
print("\nsearch: share of baskets at the edge (buy %K < 20, sell %K > 80)")
R = []
for k in range(4, 22):
    for sl in (1, 2, 3):
        for d in (1, 2, 3):
            for src in ("lh", "cc"):
                lo = (m.low if src == "lh" else m.close).rolling(k).min(); hi = (m.high if src == "lh" else m.close).rolling(k).max()
                v = ((100 * (m.close - lo).rolling(sl).sum() / (hi - lo).rolling(sl).sum()).rolling(d).mean()).values
                for bar in (0, 1):
                    x = v[i - bar]
                    e = np.where(b.side == "buy", x < 20, x > 80).mean()
                    R.append((round(e, 3), k, sl, d, src, bar))
for r in sorted(R, reverse=True)[:12]: print(r)
