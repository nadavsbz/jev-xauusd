"""t375 (docs/prereg/research_t375.md): I2 entry buffer 4bp vs 0bp, per year 2020-2025 + retro window. Gates 1-5 from the prereg.
I2 is flat at every session close, so daily realized P&L = daily MTM P&L. Usage: py -3.12 research/stable/t375.py"""
import sys, re, json
import numpy as np, pandas as pd
sys.path.insert(0, "research/btc"); from guardian_sim import deals
DEP = 120000.0; HALF_SPREAD = 0.0001; CS = 1.0   # 1bp half-spread (prereg gate 4); .USTECHCash contract 1 per lot [ASSUMED]
YEARS = ["2020", "2021", "2022", "2023", "2024", "2025"]


def summary(rep):
    t = open(f"C:/MT5_JEV_TEST/{rep}.htm", "rb").read().decode("utf-16")
    t = re.sub(r"[|\s]*\|[|\s]*", "|", re.sub("<[^>]+>", "|", t)); g = lambda k: t[t.find(k):].split("|")[1]
    return dict(quality=g("איכות היסטוריה:"), net=float(g("סך רווח נקי:").replace(",", "").replace(" ", "")),
                mdd_pct=round(float(re.search(r"\(([\d.]+)%\)", g("שווי הפסד מקסימלי:")).group(1)), 2))


def run(rep, cost_mult=1.0):
    d = deals(f"C:/MT5_JEV_TEST/{rep}.htm"); d = d[d.symbol == ".USTECHCash"].copy()
    d["day"] = pd.to_datetime(d.t, unit="s").dt.normalize()
    d["cash"] = d.profit + d.commission + d.swap
    if cost_mult != 1.0:
        d["cash"] += (cost_mult - 1) * (d.commission + d.swap - d.volume * d.price * CS * HALF_SPREAD)
    pnl = d.groupby("day").cash.sum()
    days = pd.bdate_range(pnl.index.min(), pnl.index.max()); pnl = pnl.reindex(days).fillna(0)
    eq = DEP + pnl.cumsum(); r = (pnl / eq.shift(1).fillna(DEP))
    ins = d[d.dir == "in"].t.values; outs = d[d.dir == "out"].t.values
    hrs = float(sum(o - i for i, o in zip(ins, outs)) / 3600) if len(ins) == len(outs) else None
    return r, dict(n_deals=int(len(d)), hours_in_pos=round(hrs, 1) if hrs else None)


def sh(r): return round(float(r.mean() / r.std() * np.sqrt(252)), 3)


if __name__ == "__main__":
    out = {"per_year": {}}
    R = {b: [] for b in (0, 4)}; R2 = {b: [] for b in (0, 4)}
    for y in YEARS + ["retro"]:
        row = {}
        for b in (0, 4):
            rep = f"t375_b{b}_{y}"; r, info = run(rep); r2, _ = run(rep, 2.0)
            row[f"b{b}"] = dict(summary(rep), sharpe=sh(r), sharpe_x2=sh(r2), **info)
            if y != "retro": R[b].append(r); R2[b].append(r2)
        out["per_year"][y] = row
    q_ok = [y for y in YEARS if all(out["per_year"][y][f"b{b}"]["quality"].startswith("טיקים אמיתיים") and
                                     int(re.search(r"(\d+)%", out["per_year"][y][f"b{b}"]["quality"]).group(1)) >= 99 for b in (0, 4))]
    P = {b: pd.concat([R[b][YEARS.index(y)] for y in q_ok]) for b in (0, 4)}
    P2 = {b: pd.concat([R2[b][YEARS.index(y)] for y in q_ok]) for b in (0, 4)}
    pooled = {b: sh(P[b]) for b in (0, 4)}; pooled2 = {b: sh(P2[b]) for b in (0, 4)}
    need = int(np.ceil(2 / 3 * len(q_ok)))
    wins = sum(out["per_year"][y]["b4"]["sharpe"] >= out["per_year"][y]["b0"]["sharpe"] for y in q_ok)
    worst = {b: max(out["per_year"][y][f"b{b}"]["mdd_pct"] for y in q_ok) for b in (0, 4)}
    rt = out["per_year"]["retro"]
    G = dict(years_used=q_ok, g1_pooled_sharpe=pooled, g1=pooled[4] - pooled[0] >= 0.10,
             g2_years_better=f"{wins}/{len(q_ok)} (need {need})", g2=wins >= need,
             g3_worst_mdd=worst, g3=worst[4] <= worst[0],
             g4_pooled_sharpe_x2=pooled2, g4=pooled2[4] >= pooled2[0],
             g5_retro_sharpe={"b0": rt["b0"]["sharpe"], "b4": rt["b4"]["sharpe"]}, g5=rt["b4"]["sharpe"] >= rt["b0"]["sharpe"])
    G["enough_years"] = len(q_ok) >= 3
    out["gate"] = G
    out["VERDICT"] = "GO-candidate (retrospective; forward needed)" if G["enough_years"] and all(G[k] for k in ("g1", "g2", "g3", "g4", "g5")) else "NO-GO"
    print(json.dumps(out, indent=1, ensure_ascii=False))
