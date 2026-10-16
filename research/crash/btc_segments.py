"""BTC Bot over 2023-2026 in the tester, restarted after every wipe: each segment starts with
$2,000 the day after the previous one ended in a wipe (balance at or below 5% of the deposit).
Lists each segment's start, end, peak and the wipe day. Read-only investor login (run_tester.py).
Usage: python research/crash/btc_segments.py OUT_JSON [START YYYY-MM-DD] [PREFIX]
RoboForex-Pro has real gold ticks from April 2024 only; earlier segments run on generated ticks."""
import glob, json, os, re, subprocess, sys, time
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
    start0 = sys.argv[2] if len(sys.argv) > 2 else "2023-01-01"
    prefix = sys.argv[3] if len(sys.argv) > 3 else "btc_seg"
    out, start, k = [], pd.Timestamp(start0), 0
    while start < END - pd.Timedelta(days=7):
        name = f"{prefix}_{k:02d}"
        rep = os.path.join(TERM, name + ".htm")
        for attempt in range(3):                       # the login preflight can fail transiently (IPC)
            if os.path.exists(rep):
                break
            # a failed login preflight leaves the tester terminal open, and the next run refuses
            # to start: close that copy (exact path) before each attempt; no test is running then
            subprocess.run(["powershell", "-NoProfile", "-Command",
                            "Get-Process terminal64 -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq '"
                            + os.path.join(TERM, "terminal64.exe") + "' } | Stop-Process -Force"], capture_output=True)
            time.sleep(5)
            subprocess.run([PY, "run_tester.py", "--accounts", "../accounts.json", "--name", "Black Dragon 3",
                            "--terminal", os.path.join(TERM, "terminal64.exe"), "--expert", r"Jev\BTC Bot mt5.ex5",
                            "--set", "btc_bot_2dig.set", "--symbol", "XAUUSD", "--period", "M15",
                            "--from", start.strftime("%Y.%m.%d"), "--to", END.strftime("%Y.%m.%d"),
                            "--deposit", str(DEPOSIT), "--leverage", "1000", "--report", name],
                           cwd=os.path.join(ROOT, "tools"), timeout=6 * 3600)
            time.sleep(30)
            log_dirs = [os.path.join(TERM, "Tester", "logs")] + glob.glob(os.path.join(TERM, "Tester", "Agent-*", "logs"))
            for f in log_dirs:
                for x in os.listdir(f) if os.path.isdir(f) else []:
                    try:
                        os.remove(os.path.join(f, x))      # tester logs grow to tens of GB
                    except OSError:
                        pass
        if not os.path.exists(rep):
            sys.exit(f"no report for segment {k} after 3 attempts")
        d = deals(rep)
        tr = d[d.type != "balance"]
        if tr.empty:
            break
        low = tr[tr.balance <= DEPOSIT * 0.05]
        # a run that stops trading long before the end (balance too small to open the grid,
        # e.g. $131 after a $9,662 peak) is a wipe too, even above 5% of the deposit
        # stopped trading long before the end AND left with too little to open a grid (below 20% of
        # the deposit): a wipe; a pause with a healthy balance is not
        early = tr.t.iloc[-1] < END - pd.Timedelta(days=7) and tr.balance.iloc[-1] < DEPOSIT * 0.2
        wiped = (not low.empty) or early
        stop = low.t.iloc[0] if not low.empty else tr.t.iloc[-1]
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
