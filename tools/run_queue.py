"""Sequential tester queue: one MT5 tester run at a time, each from a base .set with overrides.
For every job: write the .set (UTF-16 LE with BOM, the encoding the tester reads), run run_tester.py,
summarise the report into docs/evidence/<report>.json, CHECK that the report's inputs carry every
override (a run with ignored inputs is marked invalid), append one line to the results file.
Jobs whose evidence file already exists are skipped, so the queue can be restarted.
Usage: python tools/run_queue.py QUEUE_JSON RESULTS_JSONL
QUEUE_JSON: [{"report": "...", "base_set": "...", "overrides": {"MaxLot_": "0.5"}, "name": "Black Dragon 3",
              "expert": "BD\\EA Black Dragon.ex5", "symbol": "XAUUSD", "period": "M15",
              "from": "2024.04.01", "to": "2025.10.31", "deposit": 24895, "leverage": 1000}]"""
import json, os, re, subprocess, sys

TERM = r"C:\MT5_JEV_TEST\terminal64.exe"
SETS = r"C:\MT5_JEV_TEST\MQL5\Profiles\Tester"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable


def write_set(base, overrides, out):
    b = open(os.path.join(SETS, base), "rb").read()
    t = b.decode("utf-16")
    for k, v in overrides.items():
        t, n = re.subn(rf"(?m)^{re.escape(k)}=[^\r\n]*", f"{k}={v}", t)
        if n != 1:
            sys.exit(f"{base}: input {k} found {n} times")
    open(os.path.join(SETS, out), "wb").write(b"\xff\xfe" + t.encode("utf-16-le"))


def main():
    jobs = json.load(open(sys.argv[1], encoding="utf-8")); res_path = sys.argv[2]
    for j in jobs:
        ev = os.path.join(ROOT, "docs", "evidence", j["report"] + ".json")
        if os.path.exists(ev):
            continue
        set_name = j["report"] + ".set"
        write_set(j["base_set"], j.get("overrides", {}), set_name)
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        f"Get-Process terminal64,metatester64 -ErrorAction SilentlyContinue | "
                        f"Where-Object {{ $_.Path -like 'C:\\MT5_JEV_TEST\\*' }} | Stop-Process -Force"])
        cmd = [PY, "run_tester.py", "--accounts", "../accounts.json", "--name", j["name"], "--terminal", TERM,
               "--expert", j["expert"], "--set", set_name, "--symbol", j["symbol"], "--period", j["period"],
               "--from", j["from"], "--to", j["to"], "--deposit", str(j["deposit"]),
               "--leverage", str(j["leverage"]), "--report", j["report"]]
        r = subprocess.run(cmd, cwd=os.path.join(ROOT, "tools"), capture_output=True, text=True)
        htm = os.path.join(os.path.dirname(TERM), j["report"] + ".htm")
        row = {"report": j["report"], "overrides": j.get("overrides", {}), "from": j["from"], "to": j["to"],
               "deposit": j["deposit"], "rc": r.returncode}
        if os.path.exists(htm):
            s = subprocess.run([PY, os.path.join(ROOT, "tools", "tester_summary.py"), htm, ev],
                               capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"})
            d = json.load(open(ev, encoding="utf-8"))
            ins = set(d.get("inputs", []))
            row["inputs_ok"] = all(f"{k}={v}" in ins for k, v in j.get("overrides", {}).items())
            row["summary"] = d.get("summary_from_report")
            try:
                row.update({k: json.loads(s.stdout)[k] for k in ("entries", "net", "active_days")})
            except Exception:
                pass
        else:
            row["error"] = (r.stdout + r.stderr)[-500:]
        with open(res_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(json.dumps(row, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
