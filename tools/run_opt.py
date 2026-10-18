"""One MT5 optimization run (slow complete: every combination) from a base .set with ranges, results
parsed from the XML report into docs/evidence/<report>.json. The local tester agents run the
passes in parallel, so it is still ONE tester run at a time.
The evidence is written only when every expected combination is present in the report with the
expected input values (otherwise <report>.json.invalid), so ignored ranges never count.
Usage: python tools/run_opt.py JOB_JSON
JOB_JSON: {"report": "...", "base_set": "...", "fixed": {"MaxLot_": "0.2"},
           "ranges": {"Martin_": [1.3, 0.2, 1.5]},   # start, step, stop
           "name": "Black Dragon 3", "expert": "BD\\EA Black Dragon.ex5", "symbol": "XAUUSD", "period": "M15",
           "from": "2024.04.01", "to": "2025.10.31", "deposit": 24895, "leverage": 1000}"""
import itertools, json, os, re, subprocess, sys
import xml.etree.ElementTree as ET

TERM = r"C:\MT5_JEV_TEST\terminal64.exe"
SETS = r"C:\MT5_JEV_TEST\MQL5\Profiles\Tester"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NS = {"ss": "urn:schemas-microsoft-com:office:spreadsheet"}


def values(start, step, stop):
    n = int(round((stop - start) / step)) + 1
    return [round(start + i * step, 6) for i in range(n)]


def write_set(base, fixed, ranges, out):
    b = open(os.path.join(SETS, base), "rb").read(); t = b.decode("utf-16")
    for k, v in fixed.items():
        t, n = re.subn(rf"(?m)^{re.escape(k)}=[^\r\n]*", f"{k}={v}", t)
        if n != 1:
            sys.exit(f"{base}: input {k} found {n} times")
    for k, (a, s, z) in ranges.items():
        t, n = re.subn(rf"(?m)^{re.escape(k)}=[^\r\n]*", f"{k}={a}||{a}||{s}||{z}||Y", t)
        if n != 1:
            sys.exit(f"{base}: input {k} found {n} times")
    open(os.path.join(SETS, out), "wb").write(b"\xff\xfe" + t.encode("utf-16-le"))


def parse_xml(path):
    root = ET.parse(path).getroot()
    rows = [[(c.find("ss:Data", NS).text if c.find("ss:Data", NS) is not None else "") for c in r.findall("ss:Cell", NS)]
            for r in root.iter("{urn:schemas-microsoft-com:office:spreadsheet}Row")]
    head, body = rows[0], rows[1:]
    return [dict(zip(head, r)) for r in body]


def main():
    j = json.load(open(sys.argv[1], encoding="utf-8"))
    if "--revalidate" in sys.argv:          # check an existing XML report again with the current rule
        ev = os.path.join(ROOT, "docs", "evidence", j["report"] + ".json")
        validate_and_write(j, dict(j["ranges"]), os.path.join(os.path.dirname(TERM), j["report"] + ".xml"), ev)
        return
    ev = os.path.join(ROOT, "docs", "evidence", j["report"] + ".json")
    if os.path.exists(ev):
        print("exists:", ev); return
    set_name = j["report"] + ".set"
    # fixed inputs are written as single-value ranges, so the report carries them as columns and
    # every pass can be checked against them (review: a ignored fixed value must not pass)
    # a single-value range makes the tester refuse to start (OBSERVED 17.10.2026): fixed inputs are written
    # as plain values; inputs that must be verified per pass belong in "ranges"
    ranges = dict(j["ranges"])
    write_set(j["base_set"], j.get("fixed", {}), ranges, set_name)
    cmd = [sys.executable, "run_tester.py", "--accounts", "../accounts.json", "--name", j["name"], "--terminal", TERM,
           "--expert", j["expert"], "--set", set_name, "--symbol", j["symbol"], "--period", j["period"],
           "--from", j["from"], "--to", j["to"], "--deposit", str(j["deposit"]), "--leverage", str(j["leverage"]),
           "--report", j["report"], "--optimization", "1", "--timeout", str(12 * 3600)]
    r = subprocess.run(cmd, cwd=os.path.join(ROOT, "tools"), capture_output=True, text=True)
    print(r.stdout[-800:], r.stderr[-800:])
    xml = os.path.join(os.path.dirname(TERM), j["report"] + ".xml")
    if r.returncode != 0 or not os.path.exists(xml):
        sys.exit(f"optimization failed (rc {r.returncode})")
    validate_and_write(j, ranges, xml, ev)


def validate_and_write(j, ranges, xml, ev):
    """Evidence only when every expected combination of the RANGES is in the report. Fixed inputs are
    plain values in the .set (a single-value range is refused by the tester), so they are not report
    columns: a pass that DOES carry a fixed input with another value invalidates the report; otherwise
    the fixed values are recorded as written in the .set (verified by a separate single-pass spot check
    where a result depends on them; review PR #22)."""
    passes = parse_xml(xml)
    want = set(itertools.product(*[values(*v) for v in ranges.values()]))
    got = set()
    for p in passes:
        try:
            got.add(tuple(round(float(p[k]), 6) for k in ranges))
        except (KeyError, ValueError):
            pass
    bad = [p for p in passes if any(k in p and round(float(p[k]), 6) != round(float(v), 6) for k, v in j.get("fixed", {}).items())]
    if bad:
        got = set()
    out = {"job": j, "report_file": os.path.basename(xml), "passes": passes,
           "fixed_as_columns": [k for k in j.get("fixed", {}) if passes and k in passes[0]],
           "combinations_expected": len(want), "combinations_found": len(got & want)}
    ok = want <= got
    json.dump(out, open(ev if ok else ev + ".invalid", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if ok and os.path.exists(ev + ".invalid"):
        os.remove(ev + ".invalid")
    print("ok" if ok else "INVALID: missing combinations", len(got & want), "/", len(want))
    return ok


if __name__ == "__main__":
    main()
