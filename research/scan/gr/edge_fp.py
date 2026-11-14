"""Descriptive (EdgeTrader period 8.2024-11.2026 only): time alignment of the vendor fills with RF M1, then the entry
fingerprint vs random minutes (same hour and side, other days within +-60) - the tool used for Gold Reaper (entry_fp.py).
Usage: py -3.12 research/scan/gr/edge_fp.py"""
import sys; sys.path.insert(0, "research/scan/gr")
import numpy as np, pandas as pd
import entry_fp as E
t = pd.read_csv("docs/agents/grok_data/t212/real_trade_bp.csv", parse_dates=["open_broker"])
m = E.m; LO, HI = m.low, m.high
for h in (-2, -1, 0, 1, 2):
    ts = t.open_broker + pd.Timedelta(hours=h)
    ok = (t.open_px.values >= LO.reindex(ts).values - 0.5) & (t.open_px.values <= HI.reindex(ts).values + 0.5)
    print(f"shift {h:+d}h: fill inside RF M1 bar {np.nanmean(ok) * 100:.1f}%")
if __name__ == "__main__":
    b = t.groupby(["open_broker", "side"]).size().reset_index()[["open_broker", "side"]]
    rng = np.random.default_rng(212); A, N = [], []
    for _, r in b.iterrows():
        f = E.feats(r.open_broker, r.side)
        if f is None: continue
        A.append(f)
        for k in rng.choice([k for k in range(-60, 61) if k], 8, replace=False):
            g = E.feats(r.open_broker + pd.Timedelta(days=int(k)), r.side)
            if g: N.append(g)
    A, N = pd.DataFrame(A), pd.DataFrame(N)
    out = pd.DataFrame({"ET_med": A.median(), "null_med": N.median(), "ET_p25": A.quantile(.25), "ET_p75": A.quantile(.75),
                        "AUC": [((A[c].values[:, None] > N[c].values[None, :]).mean()) for c in A]})
    print(f"ET baskets {len(A)}, null minutes {len(N)}"); print(out.round(3).sort_values("AUC").to_string())
    A.to_csv("data/derived/scan/et_entry_feats.csv"); N.to_csv("data/derived/scan/et_null_feats.csv")
