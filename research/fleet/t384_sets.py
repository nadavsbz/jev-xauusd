"""t384 v2: one tester set per Lars segment, from bd2afterpoint.set (2-digit RF set) with the segment lot and floor.
Clone sets (t384_c_*) carry G_FloorPct/G_FloorDays/G_FloorFrom; BD sets (t384_b_*) carry no floor (the original EA has none).
Also writes data/derived/lars/t384_queue.txt: name:expert:set:from:to:deposit (git-ignored; deposits are balances).
Usage: py -3.12 research/fleet/t384_sets.py"""
import pandas as pd

TESTER = "C:/MT5_JEV_TEST/MQL5/Profiles/Tester/"
BASE = TESTER + "bd2afterpoint.set"


def load(p):
    t = open(p, "rb").read()
    t = t.decode("utf-16") if t[:2] in (b"\xff\xfe", b"\xfe\xff") else t.decode("utf-8")
    return [l for l in t.replace("\r\n", "\n").split("\n") if l.strip()]


def write(name, lines):
    open(TESTER + name + ".set", "wb").write(b"\xff\xfe" + ("\r\n".join(lines) + "\r\n").encode("utf-16-le"))


def setv(lines, key, val):
    out = [l for l in lines if not l.split("=")[0] == key]
    return out + [f"{key}={val}"]


if __name__ == "__main__":
    base = load(BASE)
    s = pd.read_csv("data/derived/lars/segments_t384.csv", parse_dates=["start", "start_live", "cut_live", "end_live"])
    import hashlib
    sha = {e: hashlib.sha256(open(f"C:/MT5_JEV_TEST/MQL5/Experts/{p}", "rb").read()).hexdigest()[:16] for e, p in
           (("DragonClone_v7", "Jev/DragonClone_v7.ex5"), ("BD\EA Black Dragon", "BD/EA Black Dragon.ex5"))}
    q = [f"# ex5 sha256[:16]: {sha}"]; skipped = []
    for i, r in enumerate(s.itertuples(), 1):
        lot = r.lot if pd.notna(r.lot) else r.live_min_lot
        tag = f"{r.acct}_{i:02d}"
        b = setv(base, "Lot_Init_", f"{lot:.2f}")
        write(f"t384_b_{tag}", b)
        c = b
        if pd.notna(r.floor):
            pct = 100 * (1 - r.floor / r.e_start_live)                  # v2.1: against the live equity at start (Grok P1-1)
            if pct <= 0: skipped.append(tag); continue                  # v2.1 P0-1: floor at/above start equity -> excluded from M1/M2, reported apart
            c = setv(c, "G_FloorPct", f"{pct:.4f}")
            c = setv(c, "G_FloorDays", "999"); c = setv(c, "G_FloorFrom", r.start_live.strftime("%Y%m%d"))
        write(f"t384_c_{tag}", c)
        fr = r.start_live.strftime("%Y.%m.%d"); to = (r.end_live - pd.Timedelta(seconds=1)).strftime("%Y.%m.%d")
        write(f"t384_s_{tag}", setv(c, "MaxSpred", "50"))               # sensitivity: MaxSpred 50 (clone only)
        for kind, ex in (("c", "DragonClone_v7"), ("b", "BD\EA Black Dragon"), ("s", "DragonClone_v7")):
            q.append(f"t384_{kind}_{tag}:{ex}:t384_{kind}_{tag}:{fr}:{to}:{r.e_start_live:.0f}")
    open("data/derived/lars/t384_queue.txt", "w").write("\n".join(q) + "\n")
    print(len(s), "segments ->", len(q) - 1, "runs; excluded (floor >= start equity):", skipped, "; ex5:", sha)
