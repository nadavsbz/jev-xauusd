"""Anatomy of a Bull Scalper tester report: how the bot actually trades (goal: understand it well enough
to rebuild it). Pairs entries and exits, then describes sides, position stacking, spacing between stacked
entries, holding time, exit distance from entry, win/loss shape, hour of day, weekday, and costs.
Usage: python research/bull/anatomy.py REPORT.htm OUT_JSON"""
import os, sys, json, hashlib
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "btc"))
import guardian_sim as g  # noqa: E402


def pair_k(d, k):
    g.K = k
    pos, left = g.pair(d)
    return pos, left


def main():
    rep, out = sys.argv[1], sys.argv[2]
    d = g.deals(rep)
    # contract size: the K that makes the implied entry price match a real entry best
    best = None
    for k in (1.0, 10.0, 100.0):
        pos, left = pair_k(d, k)
        e = float(pos.err.median()) if len(pos) else 1e9
        if best is None or e < best[0]:
            best = (e, k, pos, left)
    _, K, pos, left = best
    pos = pos.sort_values("t0").reset_index(drop=True)
    pos["hold_min"] = (pos.t1 - pos.t0) / 60
    sgn = np.where(pos.side == "buy", 1, -1)
    pos["move"] = sgn * (pos.p1 - pos.p0)                       # exit minus entry in price, in the trade direction
    pos["gross"] = pos.net - pos.swap - pos.cost_in            # rough: profit before costs of the exit deal side too
    # stacks: overlapping positions of the same side, like the basket logic for grids
    pos["stack"] = -1; n = 0
    for side in ("buy", "sell"):
        idx = pos.index[pos.side == side]
        ev = sorted([(pos.t0[i], 1, i) for i in idx] + [(pos.t1[i], -1, i) for i in idx], key=lambda x: (x[0], -x[1]))
        openn, cur = 0, None
        for t, kk, i in ev:
            if kk == 1:
                if openn == 0:
                    cur = n; n += 1
                pos.loc[i, "stack"] = cur; openn += 1
            else:
                openn -= 1
    st = pos.groupby("stack").agg(side=("side", "first"), n=("vol", "size"), t0=("t0", "min"), t1=("t1", "max"),
                                  net=("net", "sum"), lots=("vol", "sum"))
    # spacing between consecutive entries inside a stack, and whether each new entry is lower (DCA) or higher (add on strength)
    gaps = []
    for s, x in pos.groupby("stack"):
        x = x.sort_values("t0")
        if len(x) > 1:
            sg = 1 if x.side.iloc[0] == "buy" else -1
            gaps += list(sg * np.diff(x.p0.to_numpy()))
    gaps = pd.Series(gaps, dtype=float)
    ts = pd.to_datetime(pos.t0, unit="s")
    q = lambda s: {str(k): round(float(v), 3) for k, v in s.quantile([0.05, 0.25, 0.5, 0.75, 0.95]).items()}
    res = {
        "report": os.path.basename(rep), "report_sha256": hashlib.sha256(open(rep, "rb").read()).hexdigest(),
        "contract_K": K, "positions": int(len(pos)), "unmatched_entries": int(left),
        "sides": pos.side.value_counts().to_dict(),
        "net_total": round(float(pos.net.sum()), 2), "swap_total": round(float(pos.swap.sum()), 2),
        "win_rate_pct": round(float((pos.net > 0).mean() * 100), 2),
        "avg_win": round(float(pos.net[pos.net > 0].mean()), 2), "avg_loss": round(float(pos.net[pos.net <= 0].mean()), 2),
        "hold_minutes_quantiles": q(pos.hold_min),
        "exit_move_price_quantiles": q(pos.move),
        "share_held_overnight_pct": round(float((pd.to_datetime(pos.t1, unit="s").dt.date != ts.dt.date).mean() * 100), 1),
        "lot_sizes": pos.vol.value_counts().head(8).to_dict(),
        "stacks": int(len(st)), "positions_per_stack_quantiles": q(st.n), "max_positions_in_stack": int(st.n.max()),
        "stack_net_quantiles": q(st.net), "losing_stacks": int((st.net < 0).sum()),
        "stack_duration_hours_quantiles": q((st.t1 - st.t0) / 3600),
        "entry_gap_in_stack_price_quantiles (positive = new entry is BETTER priced, i.e. DCA down for buys)": q(gaps) if len(gaps) else None,
        "share_adds_lower_pct (DCA)": round(float((gaps > 0).mean() * 100), 1) if len(gaps) else None,
        "entries_by_hour_server": ts.dt.hour.value_counts().sort_index().to_dict(),
        "entries_by_weekday": ts.dt.dayofweek.value_counts().sort_index().to_dict(),
        "worst_positions": pos.nsmallest(5, "net")[["side", "vol", "p0", "p1", "net", "hold_min"]].round(2).to_dict("records"),
        "monthly_net": pos.groupby(pd.to_datetime(pos.t1, unit="s").dt.strftime("%Y-%m")).net.sum().round(0).to_dict(),
    }
    json.dump(res, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
    print(json.dumps(res, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
