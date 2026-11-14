"""Descriptive (GR period only): what does the market look like at Gold Reaper's entries vs random minutes at the same hour,
same direction, on other days within +-60 days. All features use only bars that closed before the entry minute."""
import sys; sys.path.insert(0, "research/scan/gr")
import numpy as np, pandas as pd
from gr_common import m1, gr, baskets
m = m1(); idx = m.index; O, H, L, C = (m[k].values for k in ("open", "high", "low", "close"))
dayopen = m.open.groupby(m.index.normalize()).transform("first").values
def feats(t, q):
    i = idx.searchsorted(t)                              # bar of the entry minute; use bars < i
    if i < 3000 or i >= len(idx) or idx[i] != t: return None
    p = O[i]; f = {}
    for n in (1, 5, 15, 60, 240, 1440):
        f[f"ret{n}"] = q * (p / C[i - n - 1 + 1 - 1] - 1) * 1e4 if n > 1 else q * (p / O[i - 1] - 1) * 1e4
    for n in (15, 60, 240, 720, 1440):
        hh, ll = H[i - n:i].max(), L[i - n:i].min(); rng = hh - ll
        f[f"pos{n}"] = (p - ll) / rng if q > 0 else (hh - p) / rng          # 1 = at the extreme in trade direction
        f[f"brk{n}"] = q * (p - (hh if q > 0 else ll)) / p * 1e4            # >0 = beyond the n-min extreme
    f["rng60"] = (H[i - 60:i].max() - L[i - 60:i].min()) / p * 1e4
    f["rng1440"] = (H[i - 1440:i].max() - L[i - 1440:i].min()) / p * 1e4
    f["vol15_vs_1440"] = np.std(np.diff(np.log(C[i - 16:i]))) / np.std(np.diff(np.log(C[i - 1441:i])))
    f["dopen"] = q * (p / dayopen[i] - 1) * 1e4
    f["lastbar"] = q * (C[i - 1] - O[i - 1]) / p * 1e4
    f["since_ext60"] = (i - (i - 60 + (np.argmax(H[i - 60:i]) if q > 0 else np.argmin(L[i - 60:i])))) # minutes since 60-min extreme
    return f
if __name__ == "__main__":
    b = baskets(gr()); rng = np.random.default_rng(5); A, N = [], []
    for _, r in b.iterrows():
        f = feats(r.o, r.q)
        if f is None: continue
        A.append(f)
        for k in rng.choice([k for k in range(-60, 61) if k], 8, replace=False):
            g = feats(r.o + pd.Timedelta(days=int(k)), r.q)
            if g: N.append(g)
    A, N = pd.DataFrame(A), pd.DataFrame(N)
    out = pd.DataFrame({"GR_med": A.median(), "null_med": N.median(), "GR_p25": A.quantile(.25), "GR_p75": A.quantile(.75),
                        "d": (A.mean() - N.mean()) / N.std(), "AUC": [((A[c].values[:, None] > N[c].values[None, :]).mean()) for c in A]})
    print(f"GR baskets {len(A)}, null minutes {len(N)}")
    print(out.round(3).sort_values("AUC").to_string())
    A.to_csv("data/derived/scan/gr_entry_feats.csv"); N.to_csv("data/derived/scan/gr_null_feats.csv")
