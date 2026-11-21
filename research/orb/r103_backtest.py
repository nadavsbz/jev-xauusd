"""Round 103 backtest (prereg docs/prereg/r103_orb_stocks_in_play.md): 5-min ORB on the top-20 relative-volume stocks.
Rules as in Zarattini, Barbon & Aziz (pp. 9-10, 15-17); slippage added per the prereg.
Usage: py -3.12 research/orb/r103_backtest.py dev|val|hold [slip=0.02]"""
import sys, os, glob
import numpy as np, pandas as pd
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RAW = "data/raw/alpaca"; PART = sys.argv[1]
SLIP = float(sys.argv[2]) if len(sys.argv) > 2 else 0.02
COMM, RISK, LEV, NPOS, EQ0 = 0.0035, 0.01, 4.0, 20, 25000.0
SPAN = {"dev": ("2016-01-01", "2022-12-31"), "val": ("2023-01-01", "2023-12-31"), "hold": ("2024-01-01", "2026-10-31"), "all": ("2016-01-01", "2026-10-31")}[PART]

S = pd.read_csv(f"{RAW}/selection.csv.gz", parse_dates=["d"]); S = S[(S.d >= SPAN[0]) & (S.d <= SPAN[1])]

def trade(row, m):
    """returns (pnl_per_share, side, entry, n_shares_basis) or None. m: that stock's 1Min bars from 09:35 ET, oldest first."""
    if row.oc == row.oo: return None                                 # doji: no order
    side = 1 if row.oc > row.oo else -1
    lvl = row.oh if side > 0 else row.ol
    stop_d = 0.10 * row.atr
    ent = stop = None
    for k, b in enumerate(m.itertuples()):
        if ent is None:
            hit = b.h >= lvl if side > 0 else b.l <= lvl
            if not hit: continue
            px = max(lvl, b.o) if side > 0 else min(lvl, b.o)       # gap through the level -> fill at the open
            ent = px + side * SLIP; stop = ent - side * stop_d
            if (side > 0 and b.l <= stop) or (side < 0 and b.h >= stop):   # same bar: worst case, stopped out
                ex = stop - side * SLIP; return side * (ex - ent), side, ent
            continue
        if (side > 0 and b.l <= stop) or (side < 0 and b.h >= stop):
            px = min(stop, b.o) if side > 0 else max(stop, b.o)
            ex = px - side * SLIP; return side * (ex - ent), side, ent
    if ent is None: return None
    ex = m.c.iloc[-1] - side * 0.01                                  # 16:00 exit at the last minute close
    return side * (ex - ent), side, ent

eq = EQ0; rows = []; trades = []
for d, g in S.groupby("d"):
    f = f"{RAW}/m1/{d:%Y-%m-%d}.csv.gz"
    if not os.path.exists(f): continue
    M = pd.read_csv(f); M["ts"] = pd.to_datetime(M.t).dt.tz_convert("America/New_York")
    M = M[(M.ts.dt.hour * 60 + M.ts.dt.minute) >= 9 * 60 + 35].sort_values("ts")
    pnl = 0.0
    for r in g.itertuples():
        m = M[M.s == r.s]
        if m.empty: continue
        t = trade(r, m)
        if t is None: continue
        ps, side, ent = t
        sh = min(RISK * eq / (0.10 * r.atr), LEV * eq / NPOS / ent)   # 1% risk at the stop, notional cap 4x/20 per slot
        sh = np.floor(sh)
        if sh < 1: continue
        p = sh * ps - 2 * sh * COMM
        pnl += p; trades.append(dict(d=d, s=r.s, side=side, p=p, r=ps / (0.10 * r.atr)))
    rows.append((d, pnl / eq)); eq += pnl

R = pd.Series(dict(rows)).sort_index(); T = pd.DataFrame(trades)
eqc = (1 + R).cumprod(); sh = R.mean() / R.std() * np.sqrt(252); mdd = (eqc / eqc.cummax() - 1).min() * 100
yrs = R.groupby(R.index.year).apply(lambda x: (1 + x).prod() - 1)
top10 = T.p.nlargest(10).sum(); rest = T.p.sum() - top10
print(f"{PART} {SPAN[0][:4]}-{SPAN[1][:4]} slip ${SLIP}: days {len(R)} trades {len(T)} (long {(T.side > 0).sum()}, short {(T.side < 0).sum()})")
print(f"  Sharpe {sh:.2f}  MDD {mdd:.1f}%  CAGR {(eqc.iloc[-1] ** (252 / len(R)) - 1) * 100:.1f}%  mean R/trade {T.r.mean():.3f}  hit {(T.p > 0).mean():.1%}")
print("  years:", {y: f"{v * 100:+.1f}%" for y, v in yrs.items()})
print(f"  P&L without the 10 best trades: {rest:+,.0f} (total {T.p.sum():+,.0f})")
for sd in (1, -1):
    x = T[T.side == sd]; print(f"  [desc] {'long ' if sd > 0 else 'short'} n {len(x)} mean R {x.r.mean():.3f}")
R.to_csv(f"{RAW}/r103_daily_{PART}_{SLIP}.csv")
