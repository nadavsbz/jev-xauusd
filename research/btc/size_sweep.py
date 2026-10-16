"""BTC Bot capital per starting lot: one continuous tester run (no restarts) over the real-tick
period, April 2024 to October 2026 (RoboForex-Pro XAUUSD, M15), with the user's settings (start lot
0.01) and different deposits. A bigger deposit at a fixed lot is the same as a smaller lot at a
fixed deposit (ASSUMED: the robot sizes by Lot_Init_ only, Autolot_=false), so the result reads
as "dollars of capital per 0.01 lot".
For each deposit: survived or wiped (balance at or below 5% of the deposit), end balance,
max equity drawdown from the report, profit per day, worst day.
Chosen on the same 2.5 years it is measured on, so the "safe" capital is an in-sample figure;
the next crash can be bigger (ASSUMED risk, stated in the report).
Usage: python research/btc/size_sweep.py OUT_JSON [deposit ...]   (env BTC_SET = another set file, e.g. btc_m11.set)"""
import json, os, re, subprocess, sys, time, glob
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
PY = r"C:\Users\Benza\AppData\Local\Programs\Python\Python312\python.exe"
TERM = r"C:\MT5_JEV_TEST"
FROM, TO = "2024.04.01", "2026.10.14"
SET = os.environ.get("BTC_SET", "btc_bot_2dig.set")


def parse(rep):
    text = open(rep, "rb").read().decode("utf-16")
    cells = [[re.sub("<.*?>", "", x).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
             for r in re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S)]
    pairs = {}
    for c in cells:
        for i in range(len(c) - 1):
            if c[i].endswith(":") and c[i + 1]:
                pairs.setdefault(c[i].rstrip(":"), c[i + 1])
    d = pd.DataFrame([c for c in cells if len(c) == 13 and re.match(r"\d{4}\.\d\d\.\d\d", c[0])],
                     columns=["time", "deal", "symbol", "type", "dir", "volume", "price", "order",
                              "commission", "swap", "profit", "balance", "comment"])
    for c in ["commission", "swap", "profit", "balance"]:
        d[c] = pd.to_numeric(d[c].str.replace(" ", "").str.replace(",", ""), errors="coerce")
    d["t"] = pd.to_datetime(d.time, format="%Y.%m.%d %H:%M:%S")
    return d[d.type != "balance"], pairs


def run(dep):
    name = f"btc_size_{dep}" + ("" if SET == "btc_bot_2dig.set" else "_" + SET.replace(".set", ""))
    rep = os.path.join(TERM, name + ".htm")
    for _ in range(3):
        if os.path.exists(rep):
            break
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Get-Process terminal64 -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq '"
                        + os.path.join(TERM, "terminal64.exe") + "' } | Stop-Process -Force"], capture_output=True)
        time.sleep(5)
        subprocess.run([PY, "run_tester.py", "--accounts", "../accounts.json", "--name", "Black Dragon 3",
                        "--terminal", os.path.join(TERM, "terminal64.exe"), "--expert", r"Jev\BTC Bot mt5.ex5",
                        "--set", SET, "--symbol", "XAUUSD", "--period", "M15",
                        "--from", FROM, "--to", TO, "--deposit", str(dep), "--leverage", "1000", "--report", name],
                       cwd=os.path.join(ROOT, "tools"), timeout=8 * 3600)
        time.sleep(30)
        for f in [os.path.join(TERM, "Tester", "logs")] + glob.glob(os.path.join(TERM, "Tester", "Agent-*", "logs")):
            for x in os.listdir(f) if os.path.isdir(f) else []:
                try:
                    os.remove(os.path.join(f, x))
                except OSError:
                    pass
    tr, pairs = parse(rep)
    net = tr.profit + tr.commission + tr.swap
    day = net.groupby(tr.t.dt.normalize()).sum()
    low = tr[tr.balance <= dep * 0.05]
    # a grid left with a balance above 5% but too little to trade (it stops long before the end
    # with less than 20% of the deposit) has not survived either
    stuck = tr.t.iloc[-1] < pd.Timestamp(TO.replace(".", "-")) - pd.Timedelta(days=7) and tr.balance.iloc[-1] < dep * 0.2
    end = low.t.iloc[0] if len(low) else tr.t.iloc[-1]
    dd_abs = float(re.sub(r"[^\d.]", "", (pairs.get("שווי הפסד מקסימלי") or "0").split("(")[0]) or 0)
    quality = next((v for v in pairs.values() if "טיקים" in v or "ticks" in v.lower()), None)
    return {"set": SET, "deposit": dep, "wiped": bool(len(low)) or bool(stuck), "end": str(end.date()), "final": round(float(tr.balance.iloc[-1]), 2),
            "net": round(float(net.sum()), 2), "equity_dd": pairs.get("שווי הפסד מקסימלי") or pairs.get("Equity Drawdown Maximal"),
            "equity_dd_usd": dd_abs,
            # the registered safety margin: the deposit must cover 1.5x the worst equity drawdown, and survive
            "meets_margin_1_5": (not (bool(len(low)) or bool(stuck))) and dep >= 1.5 * dd_abs,
            "trading_days": int((day != 0).sum()), "avg_per_trading_day": round(float(day[day != 0].mean()), 2),
            "worst_day": round(float(day.min()), 2), "worst_day_date": str(day.idxmin().date()), "history_quality": quality}


def main():
    out = sys.argv[1]
    deps = [int(x) for x in sys.argv[2:]] or [5000, 10000, 20000, 40000, 80000]
    res = json.load(open(out)) if os.path.exists(out) else []
    done = {(r.get("set", "btc_bot_2dig.set"), r["deposit"]) for r in res}
    for dep in deps:
        if (SET, dep) in done:
            continue
        res.append(run(dep)); print(res[-1], flush=True)
        json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
