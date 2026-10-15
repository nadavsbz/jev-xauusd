"""Run one MT5 Strategy Tester pass in a dedicated tester terminal.

The terminal logs in with the account's investor password (the tester only
needs history from the server; it never trades). The config file holding the
login is written to a private temp folder and deleted when the run ends.
Never point this at a live trading terminal.
"""
import argparse, os, subprocess, sys, tempfile, time

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
Optimization=0
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
    a = p.parse_args()

    root = os.path.dirname(os.path.abspath(a.terminal))
    if "TEST" not in root.upper():
        sys.exit("refusing: the tester terminal folder must be a dedicated *TEST* copy")
    acc = load_account(a.accounts, a.name)
    tmp = tempfile.mkdtemp(prefix="jev_tester_")
    ini = os.path.join(tmp, "tester.ini")
    try:
        with open(ini, "w", encoding="utf-16") as f:
            f.write(INI.format(login=int(acc["login"]), password=acc["password"], server=acc["server"],
                               expert=a.expert, set_line=f"ExpertParameters={a.set}\n" if a.set else "", symbol=a.symbol, period=a.period, model=a.model,
                               from_=a.from_, to=a.to, deposit=a.deposit, leverage=a.leverage, report=a.report))
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
    finally:
        os.remove(ini); os.rmdir(tmp)
    if a.detach:
        return
    found = [f for f in os.listdir(root) if f.startswith(os.path.basename(a.report))]
    print("report files:", found or "none - see the tester log under Tester/logs")


if __name__ == "__main__":
    main()
