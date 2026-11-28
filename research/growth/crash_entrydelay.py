"""Crash days: wait N minutes after a basket's first level and keep it only if gold moved its way (the user's idea, pre-registered
7.11.2026 in docs/CRASH_LINK_PLAN.md). Baskets: rf2022_live from data/derived/crash_signs/baskets.csv (server time = Athens).
Prices: Dukascopy XAUUSD ticks 2022 (data/raw/dukascopy, git-ignored), mid price, last tick of each UTC minute.
For N = 1/5/15: move from t0 to t0+N toward the basket, AUC cut vs not, and the baskets kept when the move was not against
them vs a placebo that keeps the same number at random (200 draws). An approximation: a real delayed entry fills at another price.
Usage: python research/growth/crash_entrydelay.py"""
import glob, lzma, os, struct, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd

ROOT = os.path.join("data", "raw", "dukascopy", "XAUUSD", "2022")
T, P = [], []
for f in sorted(glob.glob(os.path.join(ROOT, "*", "*", "*h_ticks.bi5"))):
    raw = open(f, "rb").read()
    if not raw: continue
    b = lzma.decompress(raw)
    mo, d, h = f.split(os.sep)[-3], f.split(os.sep)[-2], os.path.basename(f)[:2]
    base = dt.datetime(2022, int(mo), int(d), int(h), tzinfo=dt.timezone.utc).timestamp()     # folders are 1-based (dk_download.py)
    for ms, ask, bid, _, _ in struct.iter_unpack(">3I2f", b):
        T.append(base + ms / 1000); P.append((ask + bid) / 2000)
m = pd.Series(P, index=pd.to_datetime(T, unit="s", utc=True)).resample("1min").last().ffill()
print("M1 bars:", len(m), m.index[0], "->", m.index[-1])

B = pd.read_csv("data/derived/crash_signs/baskets.csv")
B = B[B.report == "rf2022_live"].copy()
ath = ZoneInfo("Europe/Athens")
B["u"] = [dt.datetime.utcfromtimestamp(x).replace(tzinfo=ath).astimezone(dt.timezone.utc) for x in B.t0]
B["cut"] = B.kind == "cut"
sgn = np.where(B.side == "buy", 1, -1)
def px(ts):
    i = m.index.searchsorted(ts, side="right") - 1                                  # last minute close at or before ts
    return m.values[np.clip(i, 0, len(m) - 1)]
p0 = px(pd.DatetimeIndex(B.u))
rng = np.random.default_rng(1)
def auc(x, y): return (x[:, None] > y[None, :]).mean() + 0.5 * (x[:, None] == y[None, :]).mean()
print(f"baskets {len(B)} cuts {B.cut.sum()} net {B.net.sum():+,.0f}")
for N in (1, 5, 15):
    mv = sgn * (px(pd.DatetimeIndex(B.u) + pd.Timedelta(minutes=N)) - p0)
    k = mv >= 0
    G = B.net.values
    pl = np.array([G[rng.permutation(len(G))[:k.sum()]].sum() for _ in range(200)])
    ck, cd = B.cut.values[k].mean() * 1000, B.cut.values[~k].mean() * 1000
    print(f"N={N:>2}: AUC(cut, move toward basket) {auc(mv[B.cut.values], mv[~B.cut.values]):.2f} | kept {k.mean():.0%}"
          f" cuts/1000 kept {ck:.1f} dropped {cd:.1f} | net kept {G[k].sum():+,.0f} dropped {G[~k].sum():+,.0f}"
          f" | placebo median {np.median(pl):+,.0f}, kept beats {np.mean(G[k].sum() > pl):.0%}")

# Fresh-entry check: a delayed entry starts a NEW basket at t0+N. If the first N minutes carry information, the adverse run over
# the next 24h measured from the price at t0+N differs between kept and dropped baskets. If not, the effect above is mechanical
# (dropped baskets were already partly underwater) and a real delayed entry would not cut fewer baskets.
mv_ = m.values; ix = m.index
for N in (1, 5, 15):
    s = pd.DatetimeIndex(B.u) + pd.Timedelta(minutes=N)
    i0 = np.clip(ix.searchsorted(s, side="right") - 1, 0, len(m) - 1)
    pN = mv_[i0]
    adv = np.array([(pN[j] - mv_[i0[j]:i0[j] + 1440].min()) if sgn[j] == 1 else (mv_[i0[j]:i0[j] + 1440].max() - pN[j]) for j in range(len(B))])
    k = sgn * (pN - p0) >= 0
    print(f"N={N:>2} fresh entry at t0+N: adverse 24h run median kept {np.median(adv[k]):.2f}$ dropped {np.median(adv[~k]):.2f}$ |"
          f" share >= 20$: kept {(adv[k] >= 20).mean():.1%} dropped {(adv[~k] >= 20).mean():.1%}")

# Variant that can be traded as is: open level 1 at t0 as now, and CLOSE it at t0+N if gold went against it (a time stop on the
# first level). Kept baskets keep their real net; dropped ones book the first level's loss at t0+N instead of their real net.
# First-level lot = basket lots / sum(1.5^k, k < levels) (the account set's Martin 1.5), 100 oz per lot. Approximation: ignores
# levels added inside the N minutes.
lot1 = B.lots.values / np.array([sum(1.5 ** k for k in range(int(n))) for n in B.levels.values])
for N in (1, 5, 15):
    pN = px(pd.DatetimeIndex(B.u) + pd.Timedelta(minutes=N)); mv = sgn * (pN - p0); k = mv >= 0
    early = (mv[~k] * lot1[~k] * 100).sum()
    print(f"N={N:>2} time stop: net {B.net.values[k].sum() + early:+,.0f} (now {B.net.sum():+,.0f}; kept {B.net.values[k].sum():+,.0f},"
          f" stopped {(~k).sum()} baskets {early:+,.0f}; cuts avoided {B.cut.values[~k].sum()} of {B.cut.sum()})")
# Spread cost of the stopped first levels (an extra close at the bid/ask), at 0.20$ and 0.40$, and a random-stop placebo
# (stop the same number of baskets at random, at their own t0+N move): does the CONDITION matter, or only stopping?
for N in (1, 5):
    pN = px(pd.DatetimeIndex(B.u) + pd.Timedelta(minutes=N)); mv = sgn * (pN - p0); k = mv >= 0
    L = lot1[~k].sum() * 100
    pl = []
    for _ in range(200):
        r = np.zeros(len(B), bool); r[rng.permutation(len(B))[:(~k).sum()]] = True
        pl.append(B.net.values[~r].sum() + (mv[r] * lot1[r] * 100).sum())
    base = B.net.values[k].sum() + (mv[~k] * lot1[~k] * 100).sum()
    print(f"N={N}: spread cost {-0.2 * L:+,.0f} / {-0.4 * L:+,.0f} -> net {base - 0.2 * L:+,.0f} / {base - 0.4 * L:+,.0f};"
          f" random-stop placebo median {np.median(pl):+,.0f}, conditional beats {np.mean(base - 0.4 * L > np.array(pl)):.0%}")
