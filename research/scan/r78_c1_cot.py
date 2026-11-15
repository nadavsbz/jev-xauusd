"""Round 78 (prereg docs/prereg/r78_c1_cot_filter.md): C1 python rule on BTC+ETH with CME Bitcoin TFF COT crowding filter.
Usage: py -3.12 research/scan/r78_c1_cot.py"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
import r77_c1_breadth as B
c = pd.read_csv("data/derived/crypto/btc_cot_tff.csv", parse_dates=["report_date_as_yyyy_mm_dd"]).set_index("report_date_as_yyyy_mm_dd").sort_index()
oi = c.open_interest_all
lf = (c.lev_money_positions_long - c.lev_money_positions_short) / oi; am = (c.asset_mgr_positions_long - c.asset_mgr_positions_short) / oi
z = lambda s: (s - s.rolling(156, min_periods=52).mean().shift(1)) / s.rolling(156, min_periods=52).std().shift(1)
lfz, amz = z(lf), z(am); lfz.index = lfz.index + pd.Timedelta(days=4); amz.index = amz.index + pd.Timedelta(days=4)
idx = B.idx; LZ = lfz.reindex(idx, method="ffill"); AZ = amz.reindex(idx, method="ffill")
okL = (AZ > -0.5) & (LZ < 1.5); okS = (AZ < 0.5) & (LZ > -1.5)
def run(filt, assets=("BTCUSD", "ETHUSD")):
    out = []
    for s in assets:
        w = B.W[s].reindex(idx).fillna(0)
        if filt: w = w.where(((w > 0) & okL) | ((w < 0) & okS) | (w == 0), 0.5 * w)
        tc, sl, ss, dt = B.NET[s]; r = B.R[s].reindex(idx).fillna(0); dt = dt.reindex(idx).fillna(0)
        net = w * r - w.diff().abs().fillna(0) * tc + np.where(w > 0, w * sl, -w * ss) * dt
        out.append(B.scale((1 + net).groupby(net.index.normalize()).prod() - 1))
    return B.scale(pd.concat(out, axis=1).fillna(0).mean(1))
print("share of C1 bars filtered (2019+):", round(1 - (okL | okS)["2019":].mean(), 3), " long-ok", round(okL["2019":].mean(), 2), " short-ok", round(okS["2019":].mean(), 2))
for lab, assets in [("BASKET", ("BTCUSD", "ETHUSD")), ("BTC (desc)", ("BTCUSD",)), ("ETH (desc)", ("ETHUSD",))]:
    b, f = run(False, assets), run(True, assets)
    for nm, a, zz in [("dev 2019-2022", "2019", "2022"), ("holdout 2023-2026", "2023", "2026")]:
        sb, mb, yb = B.st(b[a:zz]); sf, mf, yf = B.st(f[a:zz])
        print(f"{lab:10s} {nm}: base Sh {sb:.2f} MDD {mb:.1f} | COT Sh {sf:.2f} MDD {mf:.1f}")
