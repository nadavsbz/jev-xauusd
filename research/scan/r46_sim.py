"""Round 46a of docs/SCAN_PLAN.md (pre-registered 14.11.2026): 44a entry + exit decoded from Happy's book
(arm at +2 pips, SL -> max(entry+0.5, peak-1.5)). Usage: py -3.12 research/scan/r46_sim.py [dev|test]"""
import sys
sys.path.insert(0, "research/scan")
import r44_sim
ARM, TR, FLOOR = 2.0, 1.5, 0.5

def manage(ts, bid, ask, i0, q, e, pip, tend, slip):
    sl = e - q * r44_sim.SLP * pip; tp = e + q * 100 * pip; peak = e; armed = False
    for i in range(i0 + 1, len(ts)):
        px = bid[i] if q > 0 else ask[i]
        if ts[i] >= tend: return q * (px - e) / pip - slip
        if (q > 0 and px <= sl) or (q < 0 and px >= sl): return q * (px - e) / pip - slip
        if (q > 0 and px >= tp) or (q < 0 and px <= tp): return q * (tp - e) / pip
        peak = max(peak, px) if q > 0 else min(peak, px)
        if q * (peak - e) / pip >= ARM: armed = True
        if armed:
            cand = max(e + FLOOR * pip, peak - TR * pip) if q > 0 else min(e - FLOOR * pip, peak + TR * pip)
            sl = max(sl, cand) if q > 0 else min(sl, cand)
    px = bid[-1] if q > 0 else ask[-1]
    return q * (px - e) / pip - slip
r44_sim.manage = manage

if __name__ == "__main__":
    src = open("research/scan/r44_sim.py", encoding="utf-8").read().split('if __name__ == "__main__":', 1)[1]
    body = "\n".join(l[4:] for l in src.splitlines())
    body = body.replace('for v in ("a", "b")', 'for v in ("a",)').replace("44{v}", "46{v}").replace("R44{v}", "R46{v}")
    exec(body, r44_sim.__dict__)
