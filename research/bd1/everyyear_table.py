"""Table of the 'every year' rounds: % net per RF year (of the 120K deposit) per configuration, years positive, years >= +20%,
worst year, compound multiplier; the frozen base from v7_rf<year>_d24ntop. Usage: python research/bd1/everyyear_table.py [ROUND=1]"""
import json, os, sys, re
R = sys.argv[1] if len(sys.argv) > 1 else "1"
YRS = range(2019, 2026)
def net(rep):
    f = f"docs/evidence/{rep}.json"
    if not os.path.exists(f): return None
    return json.load(open(f, encoding="utf-8"))["recomputed"]["net"] / 1200
tags = sorted({re.match(rf"ev{R}_rf\d{{4}}_(.+)\.json", f).group(1) for f in os.listdir("docs/evidence") if re.match(rf"ev{R}_rf\d{{4}}_", f)})
rows = [("base", [net(f"v7_rf{y}_d24ntop") for y in YRS])] + [(t, [net(f"ev{R}_rf{y}_{t}") for y in YRS]) for t in tags]
print(f"{'config':16}" + "".join(f"{y:>8}" for y in YRS) + "   pos  >=20  worst  xTotal")
for t, v in rows:
    ok = [x for x in v if x is not None]; m = 1
    for x in ok: m *= 1 + x / 100
    print(f"{t:16}" + "".join(f"{x:>+8.0f}" if x is not None else f"{'-':>8}" for x in v)
          + f"   {sum(x > 0 for x in ok)}/{len(ok)}  {sum(x >= 20 for x in ok):>3}  {min(ok):>+5.0f}  x{m:.2f}")
