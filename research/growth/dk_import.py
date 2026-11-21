"""Load Dukascopy XAUUSD ticks (data/raw/dukascopy, from dk_download.py) into the tester terminal as custom symbol XAUUSD_DK, one month
per terminal start (docs/CRASH_LINK_PLAN.md). UTC -> RoboForex server time (GMT+3 during US daylight time, else GMT+2); prices
rounded to 2 digits as XAUUSD on RoboForex. Writes MQL5\\Files\\dk_chunk.bin + dk_job.txt (overwritten each month), starts
C:\\MT5_JEV_TEST with [StartUp] Script=Jev\\ImportTicks (mql5/ImportTicks.mq5) and reads dk_done.txt. Never touches another terminal.
Usage: python research/growth/dk_import.py 2016-01 2022-12"""
import glob, lzma, os, struct, subprocess, sys, tempfile, time
import numpy as np, pandas as pd

TERM = r"C:\MT5_JEV_TEST\terminal64.exe"; FILES = r"C:\MT5_JEV_TEST\MQL5\Files"
SRC = os.path.join("data", "raw", "dukascopy", "XAUUSD"); SYM = "XAUUSD_DK"

def us_dst(ts):
    """True when New York is on daylight time (2nd Sunday of March 2:00 .. 1st Sunday of November 2:00), ts in UTC"""
    y = ts.year
    mar = pd.Timestamp(y, 3, 1); start = mar + pd.Timedelta(days=(6 - mar.weekday()) % 7 + 7, hours=7)
    nov = pd.Timestamp(y, 11, 1); end = nov + pd.Timedelta(days=(6 - nov.weekday()) % 7, hours=6)
    return start <= ts < end

def month_ticks(y, m):
    out = []
    for f in sorted(glob.glob(os.path.join(SRC, f"{y}", f"{m:02d}", "*", "*.bi5"))):
        raw = open(f, "rb").read()
        if not raw: continue
        b = lzma.decompress(raw); a = np.frombuffer(b, dtype=">u4").reshape(-1, 5)
        d, hh = int(f.split(os.sep)[-2]), int(os.path.basename(f)[:2])
        t0 = pd.Timestamp(y, m, d, hh)
        off = 3 if us_dst(t0) else 2
        base = int((t0 + pd.Timedelta(hours=off)).value // 1_000_000)
        out.append(np.column_stack([base + a[:, 0].astype(np.int64), a[:, 2] / 1000.0, a[:, 1] / 1000.0]))   # bid, ask
    if not out: return None
    x = np.vstack(out); x[:, 1:] = np.round(x[:, 1:], 2)
    keep = np.r_[True, (np.diff(x[:, 1]) != 0) | (np.diff(x[:, 2]) != 0)]                           # drop repeated quotes
    return x[keep]

def run(y, m):
    x = month_ticks(y, m)
    if x is None: print(y, m, "no data"); return True
    rec = np.zeros(len(x), dtype=[("t", "<i8"), ("b", "<f8"), ("a", "<f8")]); rec["t"] = x[:, 0].astype(np.int64); rec["b"] = x[:, 1]; rec["a"] = x[:, 2]
    rec.tofile(os.path.join(FILES, "dk_chunk.bin"))
    open(os.path.join(FILES, "dk_job.txt"), "w").write(f"{SYM};XAUUSD;dk_chunk.bin")
    open(os.path.join(FILES, "dk_done.txt"), "w").write("PENDING")
    ini = os.path.join(tempfile.gettempdir(), "dk_import.ini")
    open(ini, "w").write("[StartUp]\nScript=Jev\\ImportTicks\nSymbol=XAUUSD\nPeriod=M1\n")
    p = subprocess.Popen([TERM, "/portable", f"/config:{ini}"])
    try: p.wait(timeout=1800)
    except subprocess.TimeoutExpired: p.kill(); print(y, m, "TIMEOUT"); return False
    r = open(os.path.join(FILES, "dk_done.txt")).read().strip()
    print(f"{y}-{m:02d} ticks {len(x):,} -> {r}", flush=True); return r.startswith("OK")

if __name__ == "__main__":
    a, b = pd.Period(sys.argv[1], "M"), pd.Period(sys.argv[2], "M")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Process terminal64,metatester64 -ErrorAction SilentlyContinue | "
                          "ForEach-Object { $_.Path }"], capture_output=True, text=True).stdout
    if "mt5_jev_test" in out.lower(): sys.exit("the tester terminal is running - aborting")
    p = a
    while p <= b:
        if not run(p.year, p.month): sys.exit(f"stopped at {p}")
        p += 1
