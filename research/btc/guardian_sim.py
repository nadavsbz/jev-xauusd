"""BTC Bot + JevGuardian, backtest simulation (docs/GUARDIAN_BACKTEST.md).
Trades: the continuous real-tick tester run at 0.01 lot (btc_size_120000.htm, Apr 2024 - Oct 2026).
Positions are paired exactly: an exit's profit gives its entry price (profit = sgn*vol*(exit-entry)*K),
matched to an open entry of the same side, volume and price. Equity = capital + realised + floating of
open positions (minute bars, worse of low/high), so the guard can act on the real path.
Guard rules (registered in the doc): equity floor F below the equity peak -> close everything at that
minute (worse side) and skip every original entry until the original grid would have been flat, then
resume with peak = equity. Optional direction block: an entry against a 1% move in the previous hour
is not taken (its exit is dropped too).
Usage: python research/btc/guardian_sim.py BARS_CSV REPORT.htm [--validate]"""
import re, sys, json
import numpy as np, pandas as pd

K = 100.0


def deals(rep):
    text = open(rep, "rb").read().decode("utf-16")
    cells = [[re.sub("<.*?>", "", x).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
             for r in re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S)]
    d = pd.DataFrame([c for c in cells if len(c) == 13 and re.match(r"\d{4}\.\d\d\.\d\d", c[0])],
                     columns=["time", "deal", "symbol", "type", "dir", "volume", "price", "order",
                              "commission", "swap", "profit", "balance", "comment"])
    for c in ["volume", "price", "commission", "swap", "profit", "balance"]:
        d[c] = pd.to_numeric(d[c].str.replace(" ", "").str.replace(",", ""), errors="coerce")
    d["t"] = pd.to_datetime(d.time, format="%Y.%m.%d %H:%M:%S").astype("int64") // 10**9
    return d[d.type != "balance"].reset_index(drop=True)


def pair(d):
    """-> DataFrame of positions: side, vol, entry t/px, exit t/px, net (profit+costs)."""
    open_pos = []; out = []
    for r in d.itertuples():
        if r.dir == "in":
            open_pos.append(dict(side=r.type, vol=r.volume, t0=r.t, p0=r.price, cost=r.commission))
        else:
            side = "buy" if r.type == "sell" else "sell"; sgn = 1 if side == "buy" else -1
            implied = r.price - sgn * r.profit / (K * r.volume) if r.volume else r.price
            cand = [i for i, p in enumerate(open_pos) if p["side"] == side and abs(p["vol"] - r.volume) < 1e-9]
            if not cand:
                continue
            i = min(cand, key=lambda j: abs(open_pos[j]["p0"] - implied))
            p = open_pos.pop(i)
            out.append(dict(side=side, vol=p["vol"], t0=p["t0"], p0=p["p0"], t1=r.t, p1=r.price,
                            net=r.profit + r.commission + r.swap + p["cost"], swap=r.swap, cost_in=p["cost"],
                            err=abs(p["p0"] - implied)))
    return pd.DataFrame(out), len(open_pos)


def equity_path(pos, bt, lo, hi, capital):
    a0 = np.searchsorted(bt, pos.t0.min(), "left"); a1 = np.searchsorted(bt, pos.t1.max(), "right")
    tt = bt[a0:a1]; f_lo = np.zeros(len(tt)); f_hi = np.zeros(len(tt)); real = np.zeros(len(tt))
    for r in pos.itertuples():
        sgn = 1 if r.side == "buy" else -1
        i = np.searchsorted(tt, r.t0, "right"); j = np.searchsorted(tt, r.t1, "left")
        f_lo[i:j] += sgn * r.vol * (lo[a0 + i:a0 + j] - r.p0) * K
        f_hi[i:j] += sgn * r.vol * (hi[a0 + i:a0 + j] - r.p0) * K
        real[np.searchsorted(tt, r.t1, "left"):] += r.net
    return tt, capital + real + np.minimum(f_lo, f_hi), capital + real + np.maximum(f_lo, f_hi)


SPREAD = 0.30   # USD per ounce paid when the guard closes at market (ASSUMED, RoboForex-Pro gold)


def guarded(pos, bt, lo, hi, cl, capital, floor, block, best_first=False, kill=False):
    """Event loop over minutes: positions taken unless skipped; floor closes all and skips until the
    original grid is flat (no original position open)."""
    pos = pos.sort_values("t0").reset_index(drop=True)
    # the ORIGINAL grid (before any direction filter) decides when it would have been flat
    o_a0 = np.searchsorted(bt, pos.t0.min(), "left")
    orig_open_t, orig_close_t = pos.t0.values.copy(), pos.t1.values.copy()
    if block:
        m0 = pos.t0.values - pos.t0.values % 60          # start of the entry minute: only bars closed before it
        k = np.searchsorted(bt, m0, "left") - 1; kh = np.searchsorted(bt, m0 - 3600, "left") - 1
        ok = (k >= 0) & (kh >= 0)                       # no bar before the entry: no move known, no block
        mv = np.where(ok, (cl[np.maximum(k, 0)] - cl[np.maximum(kh, 0)]) / cl[np.maximum(kh, 0)] * 100, 0.0)
        sgn = np.where(pos.side == "buy", 1, -1)
        blk = mv * sgn <= -1.0
        # JevGuardian closes such a position right after it opens: it costs the spread, nothing else
        closed_now = pos[blk].copy()
        closed_now["t1"] = closed_now.t0; closed_now["p1"] = closed_now.p0   # never on a bar path
        closed_now["net"] = -closed_now.vol * 100 * SPREAD; closed_now["swap"] = 0.0; closed_now["cost_in"] = 0.0
        closed_now["blocked"] = True
        pos = pd.concat([pos[~blk].assign(blocked=False), closed_now]).sort_values("t0").reset_index(drop=True)
    else:
        pos = pos.assign(blocked=False)
    a0 = np.searchsorted(bt, pos.t0.min(), "left"); a1 = np.searchsorted(bt, pos.t1.max(), "right")
    tt = bt[a0:a1]
    opens = np.searchsorted(tt, pos.t0.values, "right"); closes = np.searchsorted(tt, pos.t1.values, "left")
    sgnv = np.where(pos.side == "buy", 1.0, -1.0) * pos.vol.values * K
    bal = capital; peak = capital; active = np.zeros(len(pos), bool); taken = 0; stops = []; resume_at = -1
    eq_path = np.empty(len(tt)); by_open = {}; by_close = {}
    for idx, (o, c) in enumerate(zip(opens, closes)):
        by_open.setdefault(o, []).append(idx); by_close.setdefault(c, []).append(idx)
    # original grid flat: minutes where no original position is open
    oo = np.searchsorted(tt, orig_open_t, "right"); oc = np.searchsorted(tt, orig_close_t, "left")
    cnt = np.zeros(len(tt) + 1); np.add.at(cnt, np.clip(oo, 0, len(tt)), 1); np.add.at(cnt, np.clip(oc, 0, len(tt)), -1)
    open_orig = np.cumsum(cnt)[:len(tt)]
    for m in range(len(tt)):
        for idx in by_close.get(m, []):
            if active[idx]:
                bal += pos.net.values[idx]; active[idx] = False
        if m >= resume_at:
            for idx in by_open.get(m, []):
                if pos.blocked.values[idx]:          # closed by the guard within seconds: only its cost
                    bal += pos.net.values[idx]; taken += 1
                elif closes[idx] > m:
                    active[idx] = True; taken += 1
        act = np.where(active)[0]
        # accrued costs of open positions (entry commission + swap pro rata) are part of equity
        acc = 0.0
        if len(act):
            frac = np.clip((m - opens[act]) / np.maximum(closes[act] - opens[act], 1), 0, 1)
            acc = float((pos.swap.values[act] * frac).sum() + pos.cost_in.values[act].sum())
        # bars are Bid: a buy closes at Bid (its Ask entry already holds the spread), a sell closes at Ask
        ask_add = np.where(sgnv[act] < 0, SPREAD, 0.0) if len(act) else 0.0
        fl_l = float((sgnv[act] * (lo[a0 + m] + ask_add - pos.p0.values[act])).sum()) + acc if len(act) else 0.0
        fl_h = float((sgnv[act] * (hi[a0 + m] + ask_add - pos.p0.values[act])).sum()) + acc if len(act) else 0.0
        if best_first and len(act):            # the bar's good extreme came first: raise the peak before the check
            peak = max(peak, bal + max(fl_l, fl_h))
        worst = bal + min(fl_l, fl_h)
        if floor and len(act) and worst <= peak * (1 - floor):
            # close all at the worse side; accrued costs and the closing side's spread are already inside worst
            bal = worst; active[:] = False
            stops.append((int(tt[m]), round(peak, 2), round(bal, 2)))
            nxt = np.where(open_orig[m:] == 0)[0]
            # kill=True is JevGuardian as written: after a floor stop nothing trades again (no reset)
            resume_at = len(tt) if kill else m + (int(nxt[0]) if len(nxt) else len(tt))
            peak = bal
        eq = bal + (min(fl_l, fl_h) if len(np.where(active)[0]) else 0.0)
        peak = max(peak, bal + max(fl_l, fl_h) if len(np.where(active)[0]) else bal)
        eq_path[m] = eq
        if eq <= 0:
            eq_path[m:] = eq; break
    pk = np.maximum.accumulate(eq_path)
    return {"final": round(float(eq_path[-1]), 2), "max_dd_pct": round(float(((eq_path - pk) / pk).min() * 100), 1),
            "min_equity": round(float(eq_path.min()), 2), "floor_stops": len(stops), "entries_taken": taken,
            "wiped": bool(eq_path.min() <= capital * 0.05), "stops": [(str(pd.to_datetime(s[0], unit="s")), s[1], s[2]) for s in stops[:20]]}


def main():
    bars = pd.read_csv(sys.argv[1]); bt, lo, hi, cl = bars.time.values, bars.low.values, bars.high.values, bars.close.values
    d = deals(sys.argv[2]); pos, left = pair(d)
    print(f"paired {len(pos)} positions, {left} unmatched, max entry-price error {pos.err.max():.4f}")
    if "--validate" in sys.argv:
        tt, eq_lo, _ = equity_path(pos, bt, lo, hi, 120000.0)
        pk = np.maximum.accumulate(eq_lo); print("validation: max equity drawdown $%.0f (report: $67,265)" % (pk - eq_lo).max())
        return
    res = {}
    for cap in (2000, 5000, 10000, 20000):
        for floor, block, bf, kill in ((None, False, False, False), (None, True, False, False),
                                       (0.15, False, False, False), (0.15, True, False, False),
                                       (0.15, False, True, False), (0.15, True, True, False),
                                       (0.15, False, False, True), (0.15, True, False, True)):
            key = (f"cap={cap} floor={floor} block={block} bar_order={'good_first' if bf else 'bad_first'}"
                   f" after_stop={'kill' if kill else 'reset_when_flat'}")
            res[key] = guarded(pos, bt, lo, hi, cl, float(cap), floor, block, bf, kill)
            r = res[key]; print(key, {k: r[k] for k in ("final", "max_dd_pct", "floor_stops", "wiped", "entries_taken")})
    json.dump(res, open("docs/evidence/btc_guardian_sim.json", "w"), indent=1)


if __name__ == "__main__":
    main()
