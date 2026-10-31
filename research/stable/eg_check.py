"""Second broker check of C1 (docs/STABLE_SYSTEM_PLAN.md): EGlobal has only BTCUSDc (cent account), H1 from 3/2025, so this is the
BTC-only version of the same rule on 12/2025-today, EGlobal vs RoboForex bars. Costs: each broker's 2026 median bar spread
(EGlobal point 0.01 ASSUMED from the 2 price digits), financing 4.75%/yr on both (EGlobal swap not measured). LAG as in
intraday_trend.py. Usage: python research/stable/eg_check.py"""
import os
os.environ["CRY"] = "BTCUSD"
import sys; sys.argv = ["it", "6"]
exec(open("research/stable/intraday_trend.py", encoding="utf-8").read().split("if __name__")[0])
rf = mix()
d = pd.read_csv("data/derived/intraday/BTCUSDc_H1.csv"); d.index = pd.to_datetime(d.time, unit="s")
C = pd.DataFrame({"BTCUSD": d.close.resample(f"{BAR}h").last()}).ffill(limit=2)
R = C.pct_change(fill_method=None); vol = R.rolling(60, min_periods=40).std() * np.sqrt(PER_YEAR)
TC = {"BTCUSD": float((d.spread[d.time >= 1767225600] * 0.01 / d.close[d.time >= 1767225600]).median())}
eg = mix()
for nm, r in (("RoboForex", rf), ("EGlobal", eg)):
    x = r.loc["2025-12-01":]; eq = (1 + x).cumprod()
    print(f"{nm:10s} {x.index[0].date()}..{x.index[-1].date()} ret {(eq.iloc[-1] - 1) * 100:+.1f}% MDD {(eq / eq.cummax() - 1).min() * 100:.1f}%")
print("EGlobal median spread %", round(TC["BTCUSD"] * 100, 3))
