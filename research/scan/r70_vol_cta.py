"""Round 70 (prereg docs/prereg/r70_vol_cta_flow.md, commit 7922a3f): short US500 (SPX proxy) when vol20 > p80(250) and close < MA100,
exit after 2 days or when vol20 <= p80. Usage: py -3.12 research/scan/r70_vol_cta.py dev|test"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan"); sys.path.insert(0, "research/stable")
import r66_structural as R
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
R.PER = PER; R.SPAN = ("2001-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2026-12-31")
TC = 2.56e-5 + 0.00005; SWS = -0.018
c = pd.read_csv("data/raw/yahoo/SPX.csv", parse_dates=["date"]).set_index("date").close
c = c[~c.index.duplicated()].dropna()
r = c.pct_change(); v = r.rolling(20).std(); p80 = v.rolling(250, min_periods=200).quantile(0.8).shift(1); ma = c.rolling(100).mean()
cond = (v > p80) & (c < ma)
rows = []; i = 0; ix = c.index
while i < len(c) - 1:
    if cond.iloc[i]:
        j = i + 1
        while j < len(c) - 1 and j < i + 2 and v.iloc[j] > p80.iloc[j]: j += 1
        g = -(c.iloc[j] / c.iloc[i] - 1); sw = SWS * (ix[j] - ix[i]).days / 365
        rows.append((ix[j], g - 2 * TC + sw, 2 * TC - min(sw, 0))); i = j
    i += 1
print(f"===== {PER} {R.SPAN}")
R.report(pd.DataFrame(rows, columns=["d", "net", "cost"]).set_index("d"), "r70 vol/CTA short US500")
