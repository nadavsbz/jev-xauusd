"""Round 44 of docs/SCAN_PLAN.md (pre-registered 13.11.2026): news straddle (44a, Happy News spec) and delayed momentum (44b)
on RF real ticks cached by r44_fetch.py. Usage: py -3.12 research/scan/r44_sim.py [dev|test]"""
import sys, glob, os, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
import r28_30
from r28_30 import corr_rep
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"; r28_30.PER = PER
SPAN = r28_30.SPAN = ("2019-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
COMM, SLP, LOCK, TRAIL, SLI = 0.3, 18.0, 3.0, 3.0, 1.0

def manage(ts, bid, ask, i0, q, e, pip, tend, slip):
    """from tick i0 (fill), stop-managed exit; returns pips (before commission)"""
    sl = e - q * SLP * pip; tp = e + q * 100 * pip; peak = e; armed = False
    for i in range(i0 + 1, len(ts)):
        px = bid[i] if q > 0 else ask[i]
        if ts[i] >= tend: return q * (px - e) / pip - slip
        if (q > 0 and px <= sl) or (q < 0 and px >= sl): return q * (px - e) / pip - slip
        if (q > 0 and px >= tp) or (q < 0 and px <= tp): return q * (tp - e) / pip
        peak = max(peak, px) if q > 0 else min(peak, px)
        if q * (peak - e) / pip >= LOCK: armed = True
        if armed:
            cand = max(e + pip, peak - TRAIL * pip) if q > 0 else min(e - pip, peak + TRAIL * pip)
            sl = max(sl, cand) if q > 0 else min(sl, cand)
    px = bid[-1] if q > 0 else ask[-1]
    return q * (px - e) / pip - slip

def sim(f, variant, slip):
    d = pd.read_csv(f)
    if len(d) < 5: return None
    s = os.path.basename(f).split("_")[0]; pip = 0.01 if "JPY" in s else 0.0001
    T = pd.Timestamp(d.srv_T.iloc[0]); t0 = int(T.timestamp() * 1000)
    ts, bid, ask = d.time_msc.values - t0, d.bid.values, d.ask.values      # ms relative to release
    pre = np.where(ts <= -2000)[0]
    if not len(pre): return None
    M = (bid[pre[-1]] + ask[pre[-1]]) / 2
    if variant == "a":
        B, S = M + 10 * pip, M - 10 * pip
        for i in range(pre[-1] + 1, len(ts)):
            if ts[i] > 60000: return 0.0, "nofill"
            if ask[i] >= B: e = ask[i] + slip * pip; return manage(ts, bid, ask, i, 1, e, pip, 900000, slip) - 2 * COMM, "long"
            if bid[i] <= S: e = bid[i] - slip * pip; return manage(ts, bid, ask, i, -1, e, pip, 900000, slip) - 2 * COMM, "short"
        return 0.0, "nofill"
    j = np.where(ts <= 10000)[0]
    if not len(j): return None
    j = j[-1]; mv = ((bid[j] + ask[j]) / 2 - M) / pip
    if abs(mv) < 5: return 0.0, "nosig"
    q = 1 if mv > 0 else -1; e = (ask[j] + slip * pip) if q > 0 else (bid[j] - slip * pip)
    return manage(ts, bid, ask, j, q, e, pip, 180000, slip) - 2 * COMM, "long" if q > 0 else "short"

if __name__ == "__main__":
    files = sorted(glob.glob("data/derived/scan/news_ticks/*.csv"))
    for v in ("a", "b"):
        for slip in (0.0, SLI):
            rows = []
            for f in files:
                r = sim(f, v, slip)
                if r is None: continue
                T = pd.Timestamp(int(os.path.basename(f).split("_")[1][:-4]), unit="s")
                rows.append({"T": T, "sym": os.path.basename(f).split("_")[0], "pips": r[0], "kind": r[1]})
            o = pd.DataFrame(rows); o = o[(o["T"] >= SPAN[0]) & (o["T"] <= SPAN[1])]
            tr = o[o.kind.isin(["long", "short"])]
            print(f"===== 44{v} slip {slip} {PER}: events-symbols {len(o)}, trades {len(tr)}, mean {tr.pips.mean():.2f} pips, "
                  f"median {tr.pips.median():.2f}, hit {(tr.pips > 0).mean()*100:.0f}%, by sym {tr.groupby('sym').pips.mean().round(2).to_dict()}")
            print("    by year mean pips:", tr.groupby(tr['T'].dt.year).pips.mean().round(2).to_dict(), "| n:", tr.groupby(tr['T'].dt.year).size().to_dict())
            if slip == 0.0:
                R = tr.assign(r=tr.pips / SLP * 0.01).groupby(tr['T'].dt.normalize()).r.sum()
                full = pd.Series(0.0, index=pd.bdate_range(SPAN[0], min(pd.Timestamp(SPAN[1]), pd.Timestamp.now()))); full.loc[full.index.intersection(R.index)] = R
                corr_rep(full, f"R44{v}_news", f"round 44{v} news (1% risk per trade, base costs)")
