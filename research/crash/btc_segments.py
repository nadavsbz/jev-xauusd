"""BTC Bot over 2023-2026 in the tester, restarted after every wipe: each segment starts with
$2,000 the day after the previous one ended in a wipe (balance at or below 5% of the deposit).
Lists each segment's start, end, peak and the wipe day. Read-only investor login (run_tester.py).
Usage: python research/crash/btc_segments.py OUT_JSON"""
import glob, json, os, re, subprocess, sys
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
PY = r"C:\Users\Benza\AppData\Local\Programs\Python\Python312\python.exe"
TERM = r"C:\MT5_JEV_TEST"
END = pd.Timestamp("2026-10-14")
DEPOSIT = 2000


def deals(report):
    text = open(report, "rb").read().decode("utf-16")
    cells = [[re.sub("<.*?>", "", x).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
             for r in re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S)]
    d = pd.DataFrame([c for c in cells if len(c) == 13 and re.match(r"\d{4}\.\d\d\.\d\d", c[0])],
                     columns=["time", "deal", "symbol", "type", "dir", "volume", "price", "order",
                              "commission", "swap", "profit", "balance", "comment"])
    d["balance"] = pd.to_numeric(d.balance.str.replace(" ", "").str.replace(",", ""), errors="coerce")
    d["t"] = pd.to_datetime(d.time, format="%Y.%m.%d %H:%M:%S")
    return d


def main():
    out, start, k = [], pd.Timestamp("2023-01-01"), 0
    while start < END - pd.Timedelta(days=7):
        name = f"btc_seg_{k:02d}"
        rep = os.path.join(TERM, name + ".htm")
        if not os.path.exists(rep):
            subprocess.run([PY, "run_tester.py", "--accounts", "../accounts.json", "--name", "Black Dragon 3",
                            "--terminal", os.path.join(TERM, "terminal64.exe"), "--expert", r"Jev\BTC Bot mt5.ex5",
                            "--set", "btc_bot_2dig.set", "--symbol", "XAUUSD", "--period", "M15",
                            "--from", start.strftime("%Y.%m.%d"), "--to", END.strftime("%Y.%m.%d"),
                            "--deposit", str(DEPOSIT), "--leverage", "1000", "--report", name],
                           cwd=os.path.join(ROOT, "tools"), timeout=6 * 3600)
            log_dirs = [os.path.join(TERM, "Tester", "logs")] + glob.glob(os.path.join(TERM, "Tester", "Agent-*", "logs"))
            for f in log_dirs:
                for x in os.listdir(f) if os.path.isdir(f) else []:
                    try:
                        os.remove(os.path.join(f, x))      # tester logs grow to tens of GB
                    except OSError:
                        pass
        d = deals(rep)
        tr = d[d.type != "balance"]
        if tr.empty:
            break
        low = tr[tr.balance <= DEPOSIT * 0.05]
        wiped = not low.empty
        stop = low.t.iloc[0] if wiped else tr.t.iloc[-1]
        seg = tr[tr.t <= stop]
        out.append({"start": str(start.date()), "end": str(stop), "wiped": wiped,
                    "peak": float(seg.balance.max()), "peak_day": str(seg.t[seg.balance.idxmax()].date()),
                    "days": int((stop - start).days), "final": float(seg.balance.iloc[-1])})
        print(out[-1], flush=True)
        json.dump(out, open(sys.argv[1], "w"), indent=1)
        if not wiped:
            break
        start, k = stop.normalize() + pd.Timedelta(days=1), k + 1


if __name__ == "__main__":
    main()
