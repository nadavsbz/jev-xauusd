"""Sequential tester queue: one MT5 tester run at a time, each from a base .set with overrides.
For every job: write the .set (UTF-16 LE with BOM, the encoding the tester reads), run run_tester.py,
summarise the report into docs/evidence/<report>.json, CHECK that the report's inputs carry every
override (a run with ignored inputs is marked invalid), append one line to the results file.
Jobs whose evidence file already exists are skipped, so the queue can be restarted; an invalid run
(non-zero exit or ignored inputs) writes <report>.json.invalid only, so it is run again.
Usage: python tools/run_queue.py QUEUE_JSON RESULTS_JSONL
QUEUE_JSON: [{"report": "...", "base_set": "...", "overrides": {"MaxLot_": "0.5"}, "name": "Black Dragon 3",
              "expert": "BD\\EA Black Dragon.ex5", "symbol": "XAUUSD", "period": "M15",
              "from": "2024.04.01", "to": "2025.10.31", "deposit": 24895, "leverage": 1000}]"""
import json, os, re, subprocess, sys

TERM = r"C:\MT5_JEV_TEST\terminal64.exe"
SETS = r"C:\MT5_JEV_TEST\MQL5\Profiles\Tester"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable


def file_spec(j):
    """EA and base .set hashes (review PR #26): a cached result is reused only for the same binaries/settings."""
    import hashlib
    h = lambda f: hashlib.sha256(open(f, "rb").read()).hexdigest() if os.path.exists(f) else None
    root = r"C:\MT5_JEV_TEST\MQL5"
    return {"ea_sha256": h(os.path.join(root, "Experts", j["expert"])),
            "set_sha256": h(os.path.join(root, "Profiles", "Tester", j["base_set"]))}


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
    failed = []                                   # jobs that did not produce valid evidence (review PR #27)
    for j in jobs:
        ev = os.path.join(ROOT, "docs", "evidence", j["report"] + ".json")
        if os.path.exists(ev):
            # reuse only evidence of exactly this job (review PR #22/#23); otherwise move it aside and rerun
            old = json.load(open(ev, encoding="utf-8"))
            if old.get("job") == j and old.get("files") == file_spec(j):
                continue
            os.replace(ev, ev + ".stale")
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
            tmp = ev + ".tmp"          # promoted to the evidence file only after the checks pass
            if os.path.exists(tmp):
                os.remove(tmp)         # never read a summary left by an interrupted attempt (review)
            s = subprocess.run([PY, os.path.join(ROOT, "tools", "tester_summary.py"), htm, tmp],
                               capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"})
            if s.returncode != 0 or not os.path.exists(tmp):
                row["error"] = "tester_summary failed: " + (s.stdout + s.stderr)[-300:]; failed.append(j["report"])
                with open(res_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                continue
            d = json.load(open(tmp, encoding="utf-8"))
            ins = set(d.get("inputs", []))
            row["inputs_ok"] = all(f"{k}={v}" in ins for k, v in j.get("overrides", {}).items())
            if r.returncode == 0 and row["inputs_ok"]:
                d["job"] = j                                    # the full job spec, compared before any reuse
                d["files"] = file_spec(j)
                json.dump(d, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                os.replace(tmp, ev)
            else:                      # invalid run: no evidence file, so a restart runs it again
                os.replace(tmp, ev + ".invalid"); failed.append(j["report"])
            row["summary"] = d.get("summary_from_report")
            try:
                row.update({k: json.loads(s.stdout)[k] for k in ("entries", "net", "active_days")})
            except Exception:
                pass
        else:
            row["error"] = (r.stdout + r.stderr)[-500:]; failed.append(j["report"])
        with open(res_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(json.dumps(row, ensure_ascii=False), flush=True)
    if failed:
        sys.exit("no valid evidence for: " + ", ".join(failed))


if __name__ == "__main__":
    main()
