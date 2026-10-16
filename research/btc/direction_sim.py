"""BTC Bot direction block, run once (docs/DIRECTION_BLOCK_BTC.md): a new entry against a gold move
of 1.0% or more over the previous hour is removed; the remaining entries of its basket close at the
basket's volume-weighted exit price and last exit time. Equity is re-priced minute by minute.
Usage: python research/btc/direction_sim.py BARS_CSV OUT_JSON REPORT.htm [REPORT.htm ...]"""
import json, re, sys
import numpy as np, pandas as pd

K = 100.0            # USD per 1.0 price move per lot, XAUUSD (100 oz)
DEPOSIT = 2000.0
H_MIN, X_PCT = 60, 1.0


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


def baskets(d):
    """Per side: from the first entry with no open volume to the moment the side is flat again."""
    open_vol = {"buy": 0.0, "sell": 0.0}; cur = {"buy": None, "sell": None}; out = []
    for r in d.itertuples():
        if r.dir == "in":
            side = r.type
            if cur[side] is None:
                cur[side] = {"side": side, "entries": [], "exits": [], "net": 0.0}
            cur[side]["entries"].append((r.t, r.volume, r.price, r.commission))
            open_vol[side] += r.volume
            cur[side]["net"] += r.commission
        else:
            side = "buy" if r.type == "sell" else "sell"          # an exit deal is opposite to its position
            b = cur[side]
            if b is None:
                continue
            b["exits"].append((r.t, r.volume, r.price))
            b["net"] += r.profit + r.commission + r.swap
            b["swap"] = b.get("swap", 0.0) + r.swap
            b["exit_comm"] = b.get("exit_comm", 0.0) + r.commission
            open_vol[side] = round(open_vol[side] - r.volume, 4)
            if open_vol[side] <= 1e-9:
                out.append(b); cur[side] = None; open_vol[side] = 0.0
    return out, [b for b in cur.values() if b is not None]


def run(rep, bt, cl, lo, hi):
    d = deals(rep)
    bs, unfinished = baskets(d)
    net_report = float((d.profit + d.commission + d.swap).sum())
    net_baskets = sum(b["net"] for b in bs) + sum(b["net"] for b in unfinished)
    if abs(net_report - net_baskets) > 1.0:
        return {"report": rep, "error": f"basket sum {net_baskets:.2f} != report {net_report:.2f}"}
    t0, t1 = int(d.t.min()), int(d.t.max())
    a0, a1 = np.searchsorted(bt, t0, "left"), np.searchsorted(bt, t1, "right")
    tt = bt[a0:a1]
    res = {}
    for mode in ("actual", "rule"):
        fl_lo = np.zeros(len(tt)); fl_hi = np.zeros(len(tt)); real = np.zeros(len(tt)); blocked = 0
        for b in bs:
            sgn = 1 if b["side"] == "buy" else -1
            tx = max(e[0] for e in b["exits"])
            xv = sum(e[1] for e in b["exits"]); xp = sum(e[1] * e[2] for e in b["exits"]) / xv
            vol_total = sum(e[1] for e in b["entries"])
            kept = []
            for (te, v, p, c) in b["entries"]:
                if mode == "rule":
                    k = np.searchsorted(bt, te, "left") - 1; kh = np.searchsorted(bt, te - H_MIN * 60, "left") - 1
                    mv = (cl[k] - cl[max(kh, 0)]) / cl[max(kh, 0)] * 100 if k >= 0 else 0.0
                    if mv * sgn <= -X_PCT:
                        blocked += 1; continue
                kept.append((te, v, p, c))
            if not kept:
                continue
            if mode == "actual":
                pnl = b["net"]
            else:   # kept entries close at the basket's average exit; costs scale with kept volume
                kv = sum(v for _, v, _, _ in kept)
                pnl = (sum(sgn * v * (xp - p) * K + c for _, v, p, c in kept)
                       + (b.get("swap", 0.0) + b.get("exit_comm", 0.0)) * kv / vol_total)
            for (te, v, p, c) in kept:
                i = np.searchsorted(tt, te, "right"); j = np.searchsorted(tt, tx, "left")
                fl_lo[i:j] += sgn * v * (lo[a0 + i:a0 + j] - p) * K
                fl_hi[i:j] += sgn * v * (hi[a0 + i:a0 + j] - p) * K
            real[np.searchsorted(tt, tx, "left"):] += pnl
        eq = DEPOSIT + real + np.minimum(fl_lo, fl_hi)
        wiped = bool((eq <= DEPOSIT * 0.05).any())
        stop = int(np.argmax(eq <= DEPOSIT * 0.05)) if wiped else len(eq) - 1
        peak = np.maximum.accumulate(eq[:stop + 1])
        res[mode] = {"wiped": wiped, "profit_to_end_or_wipe": round(float(eq[stop] - DEPOSIT), 2),
                     "max_dd_pct": round(float(((eq[:stop + 1] - peak) / peak).min() * 100), 1),
                     "blocked_entries": blocked}
    res["report"] = rep.split("\\")[-1]
    return res


def main():
    bars = pd.read_csv(sys.argv[1])
    bt, cl, lo, hi = bars.time.values, bars.close.values, bars.low.values, bars.high.values
    out = [run(r, bt, cl, lo, hi) for r in sys.argv[3:]]
    json.dump(out, open(sys.argv[2], "w"), indent=1)
    for r in out:
        print(r)
    ok = [r for r in out if "error" not in r]
    wa = sum(r["actual"]["wiped"] for r in ok); wr = sum(r["rule"]["wiped"] for r in ok)
    pa = sum(r["actual"]["profit_to_end_or_wipe"] for r in ok); pr = sum(r["rule"]["profit_to_end_or_wipe"] for r in ok)
    print(f"wipes: actual {wa}, with rule {wr} | profit actual {pa:.0f}, with rule {pr:.0f}")


if __name__ == "__main__":
    main()
