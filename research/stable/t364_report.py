"""t364 first report (D-T): demo (data/derived/demo_c1i2/deals_<tag>.csv) vs tester real-tick runs over the same window.
Matching per docs/prereg/research_t364.md: intent_id = request time floored to H6 (C1) / H1 (I2); same symbol, side, entry/exit.
Price gap = demo fill vs tester fill of the matched deal, in bp (signed: + = demo worse). Volume ratio vs the expected D-T
factor (AV/TV 0.5 x deposit ratio). Usage: py -3.12 research/stable/t364_report.py 20261125"""
import sys, json
import numpy as np, pandas as pd
sys.path.insert(0, "research/btc"); from guardian_sim import deals

TAG = sys.argv[1] if len(sys.argv) > 1 else "20261125"
D = pd.read_csv(f"data/derived/demo_c1i2/deals_{TAG}.csv"); D["ts"] = pd.to_datetime(D.time, unit="s")
dep_demo = float(D[D.type == 2].profit.sum())
D = D[D.type <= 1].copy(); D["side"] = np.where(D.type == 0, "buy", "sell"); D["dir"] = np.where(D.entry == 0, "in", "out")
START = D.ts.min()
OUT = {}
for eng, rep, mag, freq, syms in (("C1", "t364_DT_c1_202611", 61001, "6h", ["BTCUSD", "ETHUSD"]), ("I2", "t364_DT_i2_202611", 7302, "1h", [".USTECHCash"])):
    T = deals(f"C:/MT5_JEV_TEST/{rep}.htm"); T = T[T.symbol.isin(syms)].copy(); T["ts"] = pd.to_datetime(T.t, unit="s")
    T = T[T.ts >= START.floor(freq)]
    d = D[D.magic == mag].copy()
    for x in (d, T): x["intent"] = x.ts.dt.floor(freq)
    tg = T.groupby(["symbol", "intent", "type", "dir"]).agg(t_price=("price", "mean"), t_vol=("volume", "sum")).reset_index().rename(columns={"type": "side"})
    dg = d.groupby(["symbol", "intent", "side", "dir"]).agg(d_price=("price", "mean"), d_vol=("volume", "sum"), d_ts=("ts", "min")).reset_index()
    m = dg.merge(tg, on=["symbol", "intent", "side", "dir"], how="outer", indicator=True)
    both = m[m._merge == "both"].copy()
    sgn = np.where(both.side == "buy", 1, -1)
    both["gap_bp"] = sgn * (both.d_price / both.t_price - 1) * 1e4
    both["vol_ratio"] = both.d_vol / both.t_vol
    OUT[eng] = dict(demo_intents=int((m._merge != "right_only").sum()), tester_intents=int((m._merge != "left_only").sum()), matched=int(len(both)),
                    demo_only=int((m._merge == "left_only").sum()), tester_only=int((m._merge == "right_only").sum()),
                    gap_bp_median=round(float(both.gap_bp.median()), 2) if len(both) else None, gap_bp_mean=round(float(both.gap_bp.mean()), 2) if len(both) else None,
                    vol_ratio_median=round(float(both.vol_ratio.median()), 3) if len(both) else None,
                    status="INSUFFICIENT (<10 matched)" if len(both) < 10 else "measured")
    both.to_csv(f"data/derived/demo_c1i2/t364_matched_{eng}_{TAG}.csv", index=False)
OUT["window"] = dict(demo_start=str(START), demo_deposit=dep_demo, tester_deposit=120000, expected_vol_factor_C1=round(0.5 * dep_demo / 120000, 3))
print(json.dumps(OUT, indent=1))
