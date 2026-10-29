"""Where do the frozen d24ntop losses come from? (user 29.10.2026: something profitable EVERY year)
Per RoboForex year 2019-2025: monthly realised return (balance column), the worst days, and the exits by comment
(floor guard closes vs normal basket closes). Reads the tester reports v7_rf<YEAR>_d24ntop.htm.
Usage: python research/bd1/oos_diag.py"""
import sys, os
import pandas as pd
sys.path.insert(0, "research/btc"); from guardian_sim import deals

T = "C:/MT5_JEV_TEST/"
for y in range(2019, 2026):
    f = T + f"v7_rf{y}_d24ntop.htm"
    if not os.path.exists(f): print(y, "no report"); continue
    d = deals(f); d["ts"] = pd.to_datetime(d.t, unit="s")
    out = d[d.dir == "out"].copy(); out["net"] = out.profit + out.commission + out.swap
    bal = d.balance.dropna(); start = 120000
    m = out.groupby(out.ts.dt.to_period("M")).net.sum()
    eq = start + m.cumsum(); prev = eq.shift(1).fillna(start)
    mret = (m / prev * 100).round(1)
    day = out.groupby(out.ts.dt.date).net.sum()
    dprev = (start + day.cumsum()).shift(1).fillna(start); dret = (day / dprev * 100)
    com = out.groupby(out.comment.str.extract(r"^([A-Za-z_ ]+)", expand=False).fillna("?")).net.agg(["count", "sum"]).round(0)
    print(f"== {y}: total {out.net.sum() / start * 100:+.1f}% of deposit, final balance {bal.iloc[-1]:.0f}")
    print("  months %:", " ".join(f"{p.month:02d}:{v:+.0f}" for p, v in mret.items()))
    w = dret.nsmallest(5)
    print("  worst days %:", " ".join(f"{k}:{v:+.0f}" for k, v in w.items()))
    print("  share of loss from worst 5 days:", f"{day.loc[w.index].sum() / start * 100:+.1f}% of deposit; rest of year {(out.net.sum() - day.loc[w.index].sum()) / start * 100:+.1f}%")
    print("  exits by comment:", com.to_dict("index"))
