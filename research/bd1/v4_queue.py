"""Queue builder for crash-day variants of the frozen clone (docs/BD_V4_PLAN.md).
Usage: python research/bd1/v4_queue.py OUT.json EA TAG MONTHS KEY=VAL ...
EA = file name under Experts/Jev without .ex5 (DragonClone_v3, DragonClone_v4a ...); MONTHS comma list or 'crash'/'normal'/'all'.
Account 1 balance and opening lot at each month start (deals snapshot 23.10.2026)."""
import json, sys

MONTHS = {  # tag: (from, to, deposit, Lot_Init_)
    "dec25": ("2025.12.01", "2026.01.01", 26699, "0.01"), "mar26": ("2026.03.01", "2026.04.01", 74229, "0.10"),
    "may26": ("2026.05.01", "2026.06.01", 111729, "0.25"), "jun26": ("2026.06.01", "2026.07.01", 154918, "0.23"),
    "jul26": ("2026.07.01", "2026.08.01", 163914, "0.24"), "aug26": ("2026.08.01", "2026.09.01", 144501, "0.17"),
    "sep26": ("2026.09.01", "2026.10.01", 109829, "0.18"), "oct26": ("2026.10.01", "2026.10.24", 150298, "0.22")}
GROUPS = {"crash": ["may26", "jun26", "jul26", "aug26", "oct26"], "normal": ["dec25", "mar26", "sep26"]}
GROUPS["all"] = GROUPS["normal"] + GROUPS["crash"]

def jobs(ea, tag, months, extra):
    out = []
    for m in months:
        f, t, dep, lot = MONTHS[m]
        out.append({"name": "Black Dragon 1", "expert": "Jev\\" + ea + ".ex5", "symbol": "XAUUSDc", "period": "M15", "deposit": dep,
                    "leverage": 1000, "base_set": "dcv4_base.set", "from": f, "to": t, "report": f"{tag}_{m}",
                    "overrides": dict({"Lot_Init_": lot}, **extra)})
    return out

if __name__ == "__main__":
    out, ea, tag, ms = sys.argv[1:5]
    months = GROUPS.get(ms) or ms.split(",")
    extra = dict(a.split("=", 1) for a in sys.argv[5:])
    q = json.load(open(out, encoding="utf-8")) if len(sys.argv) > 0 and __import__("os").path.exists(out) else []
    q += jobs(ea, tag, months, extra)
    json.dump(q, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(q), [j["report"] for j in q][-len(months):])
