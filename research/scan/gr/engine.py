"""Decoded Gold Reaper exit engine (from the GR period, descriptive): TP tp% of price, initial SL sl%, once the favourable excursion
reaches trig% the stop moves to entry + lock%; optional time cap. Simulated on M1 OHLC (bid); if a bar touches both, the stop wins."""
import numpy as np
def run(o, h, l, c, i0, q, tp=0.0034, sl=0.0050, trig=0.0020, lock=0.00033, cap=24 * 60):
    """o,h,l,c numpy arrays of M1; entry at open of bar i0; returns (ret, bars held)."""
    e = o[i0]; stop = e * (1 - q * sl); tgt = e * (1 + q * tp); moved = False
    n = len(o); end = min(n - 1, i0 + cap)
    for i in range(i0, end + 1):
        hi, lo = h[i], l[i]
        if q > 0:
            if lo <= stop: return stop / e - 1, i - i0
            if hi >= tgt: return tp, i - i0
            if not moved and hi >= e * (1 + trig): stop = e * (1 + lock); moved = True
        else:
            if hi >= stop: return 1 - stop / e, i - i0
            if lo <= tgt: return tp, i - i0
            if not moved and lo <= e * (1 - trig): stop = e * (1 - lock); moved = True
    return q * (c[end] / e - 1), end - i0
