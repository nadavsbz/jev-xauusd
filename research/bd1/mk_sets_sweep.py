"""Community set sweep (docs/CRASH_LINK_PLAN.md): the original EA Black Dragon with every MT5 XAUUSD 2-digit set shared in the
Top Target Telegram group (data/raw/telegram/toptarget/files, git-ignored), one tester run per year 2019-2025 on RoboForex real
ticks. Copies each set as UTF-16 LE into the tester's Profiles\\Tester as cs_<id>.set (inside C:\\MT5_JEV_TEST) and writes
research/bd1/q_sets.json for tools/run_queue.py.
Timeframe from the file name (m1 / m5 / m15), otherwise M15 [ASSUMED]. Deposit: 50,000 when the set sizes by balance
(Autolot_=true), else the set's own Autolotsize_ (the balance its fixed lot was written for). No external floor: the EA alone.
Usage: python research/bd1/mk_sets_sweep.py"""
import glob, json, os, re

SRC = os.path.join("data", "raw", "telegram", "toptarget", "files")
SETS = r"C:\MT5_JEV_TEST\MQL5\Profiles\Tester"
Y = (("2019", "2019.01.02", "2020.01.01"), ("2020", "2020.01.02", "2021.01.01"), ("2021", "2021.01.04", "2022.01.01"),
     ("2022", "2022.01.03", "2023.01.01"), ("2023", "2023.01.02", "2024.01.01"), ("2024", "2024.01.02", "2025.01.01"),
     ("2025", "2025.01.02", "2025.10.24"))

def text(p):
    b = open(p, "rb").read()
    return b.decode("utf-16") if b[:2] in (b"\xff\xfe", b"\xfe\xff") else b.decode("utf-8-sig", errors="replace")

def wanted(name):
    n = name.lower()
    if "mt4" in n or "xag" in n or "btc" in n or "3d" in n or "3digit" in n: return False
    return "2d" in n or "2digit" in n or "xaublackdragonm15" in n

J = []; listed = []
for p in sorted(glob.glob(os.path.join(SRC, "*.set"))):
    name = os.path.basename(p)
    if not wanted(name): continue
    t = text(p)
    kv = dict(re.findall(r"(?m)^([A-Za-z_][\w]*)=([^|\r\n]*)", t))
    if "Martin_" not in kv: continue                                   # not a Black Dragon set
    sid = name.split("_")[0]; n = name.lower()
    tf = "M1" if re.search(r"(^|[^a-z0-9])m1([^0-9]|$)", n) else "M5" if "m5" in n else "M15"
    dep = 50000 if kv.get("Autolot_", "false").lower() == "true" else int(float(kv.get("Autolotsize_", "50000")))
    open(os.path.join(SETS, f"cs_{sid}.set"), "wb").write(b"\xff\xfe" + t.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-16-le"))
    listed.append((sid, tf, dep, name))
    for y, f, to in Y:
        J.append({"name": "Black Dragon 3", "symbol": "XAUUSD", "period": tf, "deposit": dep, "leverage": 1000,
                  "base_set": f"cs_{sid}.set", "from": f, "to": to, "expert": r"BD\EA Black Dragon.ex5",
                  "report": f"cs_{sid}_{y}", "overrides": {}})
json.dump(J, open("research/bd1/q_sets.json", "w"), indent=1)
for r in listed: print(*r)
print(len(listed), "sets,", len(J), "runs")
