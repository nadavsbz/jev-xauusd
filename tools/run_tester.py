"""Run one MT5 Strategy Tester pass in a dedicated tester terminal.

The terminal logs in with the account's investor password (the tester only
needs history from the server; it never trades). The config file holding the
login is written to a private temp folder and deleted when the run ends.
Never point this at a live trading terminal.
"""
import argparse, codecs, glob, os, subprocess, sys, tempfile, time

from collect_history import load_account

INI = """[Common]
Login={login}
Password={password}
Server={server}
[Tester]
Expert={expert}
{set_line}Symbol={symbol}
Period={period}
Model={model}
Optimization={optimization}
OptimizationCriterion=0
FromDate={from_}
ToDate={to}
ForwardMode=0
Deposit={deposit}
Leverage=1:{leverage}
ExecutionMode=0
Report={report}
ReplaceReport=1
ShutdownTerminal=1
UseLocal=1
UseRemote=0
UseCloud=0
Visual=0
"""


# The only terminals this script may start: dedicated copies that run no live EA.
ALLOWED_TERMINALS = {os.path.normcase(os.path.join("C:\\", "MT5_JEV_TEST", "terminal64.exe"))}


def running_from(terminal):
    """PIDs of terminal64.exe processes started from this exact path."""
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-Process terminal64 -ErrorAction SilentlyContinue | "
                          "ForEach-Object { \"$($_.Id)|$($_.Path)\" }"], capture_output=True, text=True).stdout
    want = os.path.normcase(os.path.abspath(terminal))
    return [int(l.split("|")[0]) for l in out.splitlines() if "|" in l and os.path.normcase(l.split("|", 1)[1]) == want]


def preflight(terminal, acc):
    """Fail closed before the terminal is started with a login:
    - it is not already running (a running copy could hold live charts/EAs);
    - its config auto-starts nothing and copies no signal;
    - the login is investor-only: connect read-only through the Python API and
      refuse if the account allows trading, then close that terminal again."""
    root = os.path.dirname(os.path.abspath(terminal))
    if running_from(terminal):
        sys.exit("refusing: the tester terminal is already running")
    for ini in glob.glob(os.path.join(root, "config", "*.ini")):
        raw = open(ini, "rb").read()
        text = raw.decode("utf-16", errors="ignore") if raw.startswith(codecs.BOM_UTF16_LE) else raw.decode("utf-8", errors="ignore")
        section = ""
        for line in text.lower().splitlines():
            if line.strip().startswith("["):
                section = line.strip()
            key, _, val = line.partition("=")
            if section == "[signals]" and val.strip():
                sys.exit(f"refusing: {os.path.basename(ini)} has [Signals] settings (signal copying)")
            # auto-start lives in [StartUp]; [Tester] only remembers the last test
            if section == "[startup]" and key.strip() in ("script", "expert", "service") and val.strip():
                sys.exit(f"refusing: {os.path.basename(ini)} auto-starts a program ({key.strip()}=)")
    import MetaTrader5 as mt5
    login = int(acc["login"])
    if not mt5.initialize(path=terminal, login=login, password=acc["password"], server=acc["server"],
                          portable=True, timeout=240000):
        sys.exit(f"preflight login failed: {mt5.last_error()}")
    try:
        info = None
        for _ in range(12):                      # the login switch can lag behind initialize()
            info = mt5.account_info()
            if info is not None and info.login == login:
                break
            time.sleep(5)
        if info is None or info.login != login:
            sys.exit("preflight: connected to the wrong account")
        if info.trade_allowed:
            sys.exit("preflight: this login allows trading (master password?) - refusing, investor only")
    finally:
        mt5.shutdown()
        for pid in running_from(terminal):       # close the preflight instance (path verified), also on failure
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
        time.sleep(5)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--accounts", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--terminal", required=True, help="tester terminal64.exe (not a live one)")
    p.add_argument("--expert", required=True, help="path under MQL5/Experts")
    p.add_argument("--set", default="", help="file name under MQL5/Profiles/Tester (empty = EA defaults)")
    p.add_argument("--symbol", required=True)
    p.add_argument("--period", default="M1")
    p.add_argument("--model", type=int, default=4, help="0 every tick, 1 M1 OHLC, 4 real ticks")
    p.add_argument("--from", dest="from_", required=True, help="YYYY.MM.DD")
    p.add_argument("--to", required=True, help="YYYY.MM.DD")
    p.add_argument("--deposit", type=int, required=True)
    p.add_argument("--leverage", type=int, default=1000)
    p.add_argument("--report", required=True, help="report name, relative to the terminal folder")
    p.add_argument("--timeout", type=int, default=4 * 3600)
    p.add_argument("--detach", action="store_true", help="start the terminal and return once testing has started")
    p.add_argument("--optimization", type=int, default=0,
                   help="0 single pass, 1 slow complete (every combination of the ranges in the .set; local agents in parallel)")
    a = p.parse_args()

    root = os.path.dirname(os.path.abspath(a.terminal))
    if os.path.normcase(os.path.abspath(a.terminal)) not in ALLOWED_TERMINALS:
        sys.exit(f"refusing: {a.terminal} is not a registered dedicated tester terminal")
    acc = load_account(a.accounts, a.name)
    preflight(a.terminal, acc)
    # an old report with the same name must never pass as this run's result (review)
    for f in os.listdir(root):
        if f.startswith(os.path.basename(a.report) + ".") or f.startswith(os.path.basename(a.report) + "-"):
            os.remove(os.path.join(root, f))
    tmp = tempfile.mkdtemp(prefix="jev_tester_")
    ini = os.path.join(tmp, "tester.ini")
    try:
        with open(ini, "w", encoding="utf-16") as f:
            f.write(INI.format(login=int(acc["login"]), password=acc["password"], server=acc["server"],
                               expert=a.expert, set_line=f"ExpertParameters={a.set}\n" if a.set else "", symbol=a.symbol, period=a.period, model=a.model,
                               from_=a.from_, to=a.to, deposit=a.deposit, leverage=a.leverage, report=a.report,
                               optimization=a.optimization))
        t0 = time.time()
        if a.detach:
            # The terminal runs on its own (survives this script); the config with the
            # login is deleted as soon as the terminal has read it and started testing.
            flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            subprocess.Popen([a.terminal, "/portable", f"/config:{ini}"], creationflags=flags, close_fds=True)
            log = os.path.join(root, "logs", time.strftime("%Y%m%d") + ".log")
            while time.time() - t0 < 600:
                time.sleep(5)
                try:
                    text = open(log, encoding="utf-16", errors="ignore").read()
                except OSError:
                    continue
                if "automatic testing started" in text[text.rfind(ini):] if ini in text else False:
                    print("testing started; the report will appear in", root)
                    break
            else:
                print("terminal did not start testing within 10 minutes")
            return
        proc = subprocess.run([a.terminal, "/portable", f"/config:{ini}"], timeout=a.timeout)
        print(f"terminal exited with {proc.returncode} after {time.time() - t0:.0f}s")
        rc = proc.returncode
    finally:
        os.remove(ini); os.rmdir(tmp)
    if a.detach:
        return
    found = [f for f in os.listdir(root) if f.startswith(os.path.basename(a.report))]
    print("report files:", found or "none - see the tester log under Tester/logs")
    if rc != 0:                         # pass the terminal's failure on (review): the queue must see it
        sys.exit(rc)
    if not any(f == os.path.basename(a.report) + (".xml" if a.optimization else ".htm") for f in found):
        sys.exit("no new report was written")


if __name__ == "__main__":
    main()
