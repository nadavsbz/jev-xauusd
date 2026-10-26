"""Adds the v7 inputs that came after the base sets were made (RandDayPct, RandSeed; Codex PR 41 round 2, P1) to the UTF-16 set files,
right after NewsAfterMin, with their default values; tools/run_queue.py needs every override to exist exactly once.
Usage: python research/bd1/v7_sets.py SET [SET ...]"""
import re, sys

ADD = ["RandDayPct=0", "RandSeed=1"]
for p in sys.argv[1:]:
    t = open(p, "rb").read().decode("utf-16")
    nl = "\r\n" if "\r\n" in t else "\n"
    for line in reversed(ADD):
        k = line.split("=")[0]
        if re.search(rf"(?m)^{k}=", t): continue
        t, n = re.subn(r"(?m)^(NewsAfterMin=[^\r\n]*)", lambda m: m.group(1) + nl + line, t)
        assert n == 1, f"{p}: NewsAfterMin found {n} times"
    open(p, "wb").write(b"\xff\xfe" + t.encode("utf-16-le")); print(p, "ok")
