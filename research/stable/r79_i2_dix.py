"""Round 79 (prereg docs/prereg/r79_i2_dix_veto.md): veto I2 tester trades by yesterday's DIX percentile.
Usage: py -3.12 research/stable/r79_i2_dix.py dev|test"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/btc"); from guardian_sim import deals
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"; YRS = range(2018, 2023) if PER == "dev" else range(2023, 2027)
dx = pd.read_csv("data/derived/macro/dix_gex.csv", parse_dates=["date"]).set_index("date").dix
pct = dx.expanding(min_periods=252).apply(lambda x: (x[:-1] < x[-1]).mean() if len(x) > 1 else np.nan, raw=True)
rows = []
for y in YRS:
    x = deals(f"C:/MT5_JEV_TEST/in2dst_t_{y}.htm"); x = x[x.symbol == ".USTECHCash"].reset_index(drop=True)
    ins = x[x.dir == "in"]; outs = x[x.dir == "out"]
    for (_, a), (_, b) in zip(ins.iterrows(), outs.iterrows()):
        d = pd.to_datetime(a.t, unit="s").normalize(); prev = pct[pct.index < d]
        p = prev.iloc[-1] if len(prev) else np.nan
        side = 1 if a.type == "buy" else -1
        veto = (side < 0 and p > 0.8) or (side > 0 and p < 0.2)
        rows.append(dict(d=pd.to_datetime(b.t, unit="s").normalize(), pnl=b.profit + b.swap + b.commission + a.commission, veto=veto, side=side))
T = pd.DataFrame(rows)
def daily(df):
    p = df.groupby("d").pnl.sum(); idx = pd.bdate_range(T.d.min(), T.d.max()); p = p.reindex(idx).fillna(0)
    eq = 120000 + p.cumsum(); r = p / eq.shift(1).fillna(120000); return r.mean() / r.std() * np.sqrt(252), p.sum()
sb, pb = daily(T); sf, pf = daily(T[~T.veto]); v = T[T.veto]
print(f"{PER}: trades {len(T)}, vetoed {len(v)} (short {int((v.side<0).sum())}, long {int((v.side>0).sum())}); vetoed mean pnl {v.pnl.mean():.1f} (t {v.pnl.mean()/v.pnl.std()*np.sqrt(len(v)):.2f})")
print(f"base Sh {sb:.2f} profit {pb:,.0f} | filtered Sh {sf:.2f} profit {pf:,.0f} ({pf/pb*100:.0f}%)")
ok = sf >= sb + 0.10 and pf >= 0.9 * pb and v.pnl.mean() < 0
print("gate:", "PASS" if ok else "KILL")
