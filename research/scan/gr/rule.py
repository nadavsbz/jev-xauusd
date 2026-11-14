"""Gold Reaper entry family decoded from the entry fingerprint (GR period only): in the trade direction,
24h move >= R bp, price within D bp below the 24h extreme (not beyond), and a fresh 60-min extreme within the last W minutes.
signals(m) returns arrays (i, q) of candidate entry bars (enter at open of bar i)."""
import numpy as np, pandas as pd
def signals(m, R=60, D=7, W=10, hours=None, gap=60, V=None, R5=None):
    O = m.open; H, L, C = m.high, m.low, m.close
    hi24, lo24 = H.rolling(1440).max().shift(1), L.rolling(1440).min().shift(1)
    r24 = O / C.shift(1440) - 1
    h60, l60 = H.rolling(60).max().shift(1), L.rolling(60).min().shift(1)
    hw, lw = H.rolling(W).max().shift(1), L.rolling(W).min().shift(1)
    span = (m.index.to_series().diff(1440).dt.total_seconds() / 60).values   # skip if the 1440 bars span > 3 days
    ok = span < 3 * 1440
    L_ = (r24 >= R / 1e4) & (O <= hi24) & (O >= hi24 * (1 - D / 1e4)) & (hw >= h60) & ok
    S_ = (r24 <= -R / 1e4) & (O >= lo24) & (O <= lo24 * (1 + D / 1e4)) & (lw <= l60) & ok
    if V is not None:                                   # short-term vol expansion: std(15 x 1m) / std(1440 x 1m)
        lr = np.log(C).diff(); v = (lr.rolling(15).std() / lr.rolling(1440).std()).shift(1); L_ &= v >= V; S_ &= v >= V
    if R5 is not None:                                  # 5-minute push in the trade direction
        r5 = O / C.shift(5) - 1; L_ &= r5 >= R5 / 1e4; S_ &= r5 <= -R5 / 1e4
    if hours is not None:
        hh = m.index.hour.isin(hours); L_ &= hh; S_ &= hh
    out = []
    t = m.index.values
    for q, s in ((1, L_.values), (-1, S_.values)):
        last = None
        for i in np.where(s)[0]:
            if last is None or (t[i] - t[last]) >= np.timedelta64(gap, "m"): out.append((i, q)); last = i
    out.sort()
    return np.array([a for a, _ in out]), np.array([b for _, b in out])
