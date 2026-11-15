"""Round 63 (prereg docs/prereg/r63_inventory_carry_oil.md, commit 7648e56): Grok H1 - long/short WTI+BRENT by crude stocks vs 5y same-week avg.
Usage: py -3.12 research/scan/r63_inventory_oil.py [dev|test]"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan"); sys.path.insert(0, "research/stable")
from scan import scale, load, tcost, trend
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
SPAN = ("2012-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2026-12-31")
TC, SWL, SWS = 0.000376, -0.06, -0.03

st = pd.read_csv("data/derived/oil/wti_stocks.csv", parse_dates=["date"]).set_index("date").v.sort_index()
avg = pd.Series({d: np.mean([st.iloc[st.index.get_indexer([d - pd.Timedelta(weeks=52 * k)], method="nearest")[0]] for k in range(1, 6)])
                 for d in st.index if d >= st.index[0] + pd.Timedelta(weeks=52 * 5 + 2)})
D = (st.reindex(avg.index) - avg) / avg
sig = np.sign(-D); sig.index = sig.index + pd.Timedelta(days=6)        # known at Thursday close

def leg(f):
    p = pd.read_csv(f"data/derived/oil/{f}.csv", parse_dates=["date"]).set_index("date").iloc[:, 0].sort_index()
    r = p.pct_change(); bad = (p <= 0) | (p.shift(1) <= 0); r[bad | bad.shift(1, fill_value=False)] = 0.0; r = r.fillna(0)
    s = sig.reindex(p.index.union(sig.index)).ffill().reindex(p.index).shift(1).fillna(0)   # held from the day after
    raw = s * r
    v = raw.rolling(90, min_periods=60).std().shift(1) * np.sqrt(252); w = s * (0.10 / v).clip(upper=5).fillna(0)
    days = p.index.to_series().diff().dt.days.fillna(1)
    return w * r - w.diff().abs().fillna(0) * TC + np.where(w > 0, w * SWL, -w * SWS) * days / 365
W, B = leg("wti_spot"), leg("brent_spot")
bk = pd.concat([W, B], axis=1).fillna(0).mean(1); bk = scale(bk)[SPAN[0]:SPAN[1]]

def rep(x, nm):
    y = x.groupby(x.index.year).sum() * 100; sh = x.mean() / x.std() * np.sqrt(252); eq = (1 + x).cumprod()
    print(f"{nm:10s} Sh {sh:5.2f} ann {x.mean()*252*100:5.1f}% MDD {(eq/eq.cummax()-1).min()*100:6.1f}% pos {int((y>0).sum())}/{len(y)} |", " ".join(f"{a%100:02d}:{v:+.0f}" for a, v in y.items()))
print(f"== {PER} {SPAN}  long share {(sig[SPAN[0]:SPAN[1]] > 0).mean():.2f}  flips {int((sig[SPAN[0]:SPAN[1]].diff() != 0).sum())}")
rep(W[SPAN[0]:SPAN[1]], "WTI leg"); rep(B[SPAN[0]:SPAN[1]], "BRENT leg"); rep(bk, "BASKET")
C1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.pct_change()
from book_tester import i2_daily
for nm, o in [("C1", C1), ("I2", i2_daily())]:
    j = pd.concat([bk, o], axis=1).dropna(); print(f"corr {nm}: {j.corr().iloc[0,1]:.2f} (n={len(j)})")
h = load("WTI"); co = trend(h, tcost("WTI", h), -6, -3); co.index = co.index.tz_localize(None) if co.index.tz else co.index
j = pd.concat([bk, co], axis=1).dropna(); print(f"corr C1-oil: {j.corr().iloc[0,1]:.2f} (n={len(j)})")
