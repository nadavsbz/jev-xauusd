"""Round 90 (prereg docs/prereg/r90_spread_regime_bd_crash.md): gold spread regime R24 as a BD crash predictor.
Usage: py -3.12 research/bd1/r90_spread_regime.py dev|hold"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, 'research/btc'); sys.path.insert(0, 'research/stable'); sys.path.insert(0, 'research/scan')
from r64_mass import loadh
PART = sys.argv[1]; THR = 1.3
sp = loadh("XAUUSD").spread.astype(float)
r24 = sp.rolling(24).median() / sp.rolling(1440).median()      # value at bar t uses bars up to t
r24 = r24.shift(1)                                              # known before bar t opens
def at(ts):
    i = r24.index.searchsorted(ts, side="right") - 1
    return r24.iloc[i] if i >= 0 else np.nan
if PART == "dev":
    from guardian_sim import deals
    cut, alld = [], []
    for y in range(2016, 2026):
        x = deals(f"C:/MT5_JEV_TEST/{'ev18' if y <= 2018 else 'ev12'}_rf{y}_ms20_h1119.htm")
        x["day"] = pd.to_datetime(x.t, unit="s").dt.normalize(); x["net"] = x.profit + x.swap + x.commission
        d = x.groupby("day").net.sum(); r = d / (120000 + d.cumsum()).shift(1).fillna(120000)
        cut += [at(k) for k in r[r < -0.02].index]
    days = pd.Series(sp["2016":"2025"].index.normalize().unique())
    alld = [at(k) for k in days]
    cut, alld = np.array(cut), np.array(alld)
    fc, fa = np.nanmean(cut >= THR), np.nanmean(alld >= THR)
    print(f"dev: cut days {len(cut)}, flagged {np.sum(cut >= THR)} ({fc:.0%}); all days {len(alld)}, flagged {fa:.0%}; lift {fc / fa:.2f}")
    print("   R24 on cut days:", np.round(np.sort(cut), 2))
    print("->", "PASS" if fc >= 2 * fa and fc >= 0.40 else "FAIL")
else:
    b = pd.read_csv("docs/agents/grok_data/r88_cutbaskets/baskets.csv")
    t = pd.to_datetime(b.t0_utc, utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None) + pd.Timedelta("7h")
    b["R"] = [at(k) for k in t]
    b = b[t <= pd.Timestamp("2026-10-30")].dropna(subset=["R"])
    f = b.R >= THR
    rc_f, rc_n = b[f].cut.mean(), b[~f].cut.mean(); share = f[b.cut].mean()
    print(f"hold: baskets {len(b)}, flagged {f.mean():.0%}; cut rate flagged {rc_f:.3%} vs other {rc_n:.3%} (x{rc_f / rc_n:.2f}); cut baskets flagged {share:.0%} of {int(b.cut.sum())}")
    print("->", "PASS" if rc_f >= 2 * rc_n and share >= 0.30 else "FAIL")
