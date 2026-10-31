"""Exploration on all of 2013..2025-10-24 (S2 costs). NOT a clean test: the 2019-2025 window was already seen (S1 test, 30.10.2026).
Only the holdout 25.10.2025-today and EGlobal stay clean. Variants of the crypto Donchian ensemble, long-only vs long-short,
alone and with the metals ensemble, each scaled to 20% annual vol. Usage: python research/stable/explore2.py"""
import sys
sys.argv = ["s2", "dev"]
exec(open("research/stable/s2.py", encoding="utf-8").read().split("P = pd.DataFrame(comp)")[0])

def rep(r, nm):
    x = r.loc["2013":"2025-10-24"]; eq = (1 + x).cumprod(); y = x.groupby(x.index.year).apply(lambda z: (1 + z).prod() - 1) * 100
    yrs = (x.index[-1] - x.index[0]).days / 365.25
    print(f"{nm:14s} CAGR {((eq.iloc[-1] ** (1 / yrs)) - 1) * 100:5.1f}% Sh {x.mean() / x.std() * 252 ** .5:4.2f} MDD {(eq / eq.cummax() - 1).min() * 100:5.1f}% |",
          " ".join(f"{int(k) % 100:02d}:{v:+.0f}" for k, v in y.items()))

cr = [s for s in C.columns if s in CRY]
WLS = pd.DataFrame({s: donch(C[s].dropna(), False).reindex(C.index) * (0.10 / vol[s]).clip(upper=3) / len(cr) for s in cr})
comp["F2_cryLS"] = scale(run(WLS.fillna(0)))
for k in ("F_cryDon", "F2_cryLS"): rep(scale(comp[k], 0.20), k)
rep(scale((comp["F2_cryLS"] + comp["H_metDon"]) / 2, 0.20), "F2+H")
rep(scale((comp["F_cryDon"] + comp["F2_cryLS"] + comp["H_metDon"]) / 3, 0.20), "F+F2+H")
