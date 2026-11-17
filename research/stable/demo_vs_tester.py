"""Weekly demo-vs-tester tracker for C1 + I2 (the user's rule: no leverage before 2-3 months of matching demo).
1. Read-only export of the demo deals and open positions (refuses a non-demo account; no orders, no login change).
2. The same period in the tester (real ticks, the demo's .set files) via tools/run_queue.py.
3. Per bot: demo net (closed deals + floating) vs tester net; appends a row to docs/evidence/demo_tracker.md.
Usage: py -3.12 research/stable/demo_vs_tester.py            (period 1.11.2026 -> today)"""
import json, os, subprocess, sys
from datetime import datetime, timedelta
import pandas as pd, MetaTrader5 as mt5

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
START, DEP = datetime(2026, 11, 1), 40000
MAGIC = {"C1": 61001, "I2": 7302}
today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
tag = today.strftime("%Y%m%d")

# 1. demo, read-only
if not mt5.initialize(path=r"C:\MT5_JEV_DEMO\terminal64.exe"):
    sys.exit(f"attach failed: {mt5.last_error()}")
try:
    acc = mt5.account_info()
    if acc is None or acc.trade_mode != 0:
        sys.exit("refusing: the attached account is not a demo account")
    d = mt5.history_deals_get(START, datetime(2030, 1, 1))
    D = pd.DataFrame(list(d), columns=d[0]._asdict().keys())
    D["t"] = pd.to_datetime(D.time, unit="s")
    D = D[D.t < today]                                        # whole days only, same window as the tester
    D.to_csv(f"data/derived/demo_c1i2/deals_{tag}.csv", index=False)
    pos = mt5.positions_get() or ()
    flo = {k: sum(p.profit + p.swap for p in pos if p.magic == m) for k, m in MAGIC.items()}
    bal, eq = acc.balance, acc.equity
finally:
    mt5.shutdown()
D["net"] = D.profit + D.commission + D.swap + D.fee
demo = {k: float(D.loc[D.magic == m, "net"].sum()) + flo[k] for k, m in MAGIC.items()}

# 2. tester, same window
to = today.strftime("%Y.%m.%d")
base = dict(name="Robo ECN demo", period="H1", deposit=DEP, leverage=100, model=4, overrides={}, to=to, **{"from": "2026.11.01"})
q = [dict(base, symbol="BTCUSD", base_set="c1_ecn_x15.set", expert="Jev\\CryptoTrend_C1.ex5", report=f"demo_cmp_c1_{tag}"),
     dict(base, symbol=".USTECHCash", base_set="nasdaq_ecn_x15.set", expert="Jev\\IndexNoise.ex5", report=f"demo_cmp_nq_{tag}")]
qf = f"research/scan/q_demo_cmp_{tag}.json"
json.dump(q, open(qf, "w"), indent=1)
subprocess.run([sys.executable, "tools/run_queue.py", qf, "research/scan/demo_cmp_results.jsonl"], check=True)
res = {}
for l in open("research/scan/demo_cmp_results.jsonl", encoding="utf-8"):
    r = json.loads(l); res[r["report"]] = r
tst = {"C1": res[f"demo_cmp_c1_{tag}"]["net"], "I2": res[f"demo_cmp_nq_{tag}"]["net"]}

# 3. report
row = (f"| {today:%d.%m} | {demo['C1']:+,.0f} | {tst['C1']:+,.0f} | {demo['I2']:+,.0f} | {tst['I2']:+,.0f} | "
       f"{sum(demo.values()):+,.0f} ({sum(demo.values())/DEP:+.1%}) | {sum(tst.values()):+,.0f} ({sum(tst.values())/DEP:+.1%}) |")
md = "docs/evidence/demo_tracker.md"
if not os.path.exists(md):
    open(md, "w", encoding="utf-8").write(
        "# מעקב דמו מול טסטר, C1 + I2 (מ-1.11.2026, הפקדה 40,000)\n"
        "נטו מצטבר מ-1.11 עד תחילת היום שבעמודה הראשונה. בדמו: עסקאות סגורות + צף. בטסטר: טיקים אמיתיים, אותם קבצי set.\n\n"
        "| עד | C1 דמו | C1 טסטר | I2 דמו | I2 טסטר | סה\"כ דמו | סה\"כ טסטר |\n|---|---|---|---|---|---|---|\n")
open(md, "a", encoding="utf-8").write(row + "\n")
print(row)
