"""Portfolio mix search (docs/PORTFOLIO_PLAN.md). Selection on 2025-11-11..2026-05-31 only;
the chosen mix is run once on 2026-06-01..2026-10-14 with --test.
Mechanics (fixed in the plan): weights of account1 / btc / bull / cash in 10% steps summing to 100%,
never account1 and btc together (one gold grid); account1 lot scale f in {0.1..0.5} (returns and
troughs scale linearly, ASSUMED); bull at its tested lot per $50k (scenario A) or absent (B);
each tool stops for good when its equity falls 15% below its own peak (loss booked as it came);
optional weekly sweep: every Monday a tool's equity above its starting allocation goes to cash.
Floating: account1 uses its intraday trough; bull/btc only realised, so their report max equity
drawdown (share of their capital) is added to the portfolio drawdown as if on the same day.
Usage: python research/portfolio/optimize.py CURVES_CSV [--btc-dd X] [--test "acc,btc,bull,f,sweep"]"""
import itertools, sys
import numpy as np, pandas as pd

SEL = (pd.Timestamp("2025-11-11"), pd.Timestamp("2026-05-31"))
TEST = (pd.Timestamp("2026-06-01"), pd.Timestamp("2026-10-14"))
FLOOR = 0.15
# Bull's floating drawdown is not available per period (the report gives one figure for the whole run,
# holdout included), so it is NOT added; Bull counts with realised P&L only. ASSUMED limitation (plan).
BULL_DD = 0.0


def simulate(c, w_acc, w_btc, w_bull, f, sweep, btc_dd):
    tools = {"acc": (w_acc, c.account1.values * f, c.account1_trough.values * f),
             "btc": (w_btc, c.btc.values if "btc" in c else np.zeros(len(c)), None),
             "bull": (w_bull, c.bull.values, None)}
    eq = {k: v[0] for k, v in tools.items()}; peak = dict(eq); alive = {k: True for k in tools}
    cash = 1.0 - w_acc - w_btc - w_bull
    total_peak, worst = 1.0, 0.0
    mondays = c.index.weekday == 0
    for i in range(len(c)):
        if sweep and mondays[i]:
            for k, (w, _, _) in tools.items():
                if alive[k] and eq[k] > w:
                    cash += eq[k] - w; eq[k] = w; peak[k] = w
        low_total = cash
        for k, (w, r, tr) in tools.items():
            if not alive[k] or eq[k] <= 0:
                low_total += max(eq[k], 0); continue
            if tr is not None:       # account 1: returns are shares of its own balance (lot follows balance)
                day_low = eq[k] * (1 + tr[i])
                close = eq[k] * (1 + r[i])
            else:                    # bull / btc: fixed lot, daily P&L as a share of the STARTING deposit
                day_low = eq[k] + w * min(r[i], 0)
                close = eq[k] + w * r[i]
            # the floor is path-dependent: applied only where a daily trough exists (account 1);
            # bull/btc have realised P&L only, so their floor is not simulated (plan, review 4).
            # The trough is checked against the peak from BEFORE the day (review: a same-day close
            # cannot raise the peak first); on a breach the tool is closed at the floor and keeps
            # none of the day's later recovery.
            line = peak[k] * (1 - FLOOR)
            if tr is not None and min(day_low, close) <= line:
                eq[k] = min(line, close); alive[k] = False
                low_total += min(day_low, eq[k])
            else:
                eq[k] = close; low_total += day_low
            peak[k] = max(peak[k], eq[k])
        total = cash + sum(max(v, 0) for v in eq.values())
        worst = min(worst, low_total / total_peak - 1, total / total_peak - 1)
        total_peak = max(total_peak, total)
    worst -= w_bull * BULL_DD + w_btc * btc_dd          # conservative: their floating at the same time
    return total, worst * 100


def main():
    c = pd.read_csv(sys.argv[1], index_col=0, parse_dates=True)
    c.loc[c.account1_crosses_split.astype(bool), ["account1", "account1_trough"]] = 0.0   # purged
    if "btc" in c and "--btc-dd" not in sys.argv:
        sys.exit("a BTC curve is present: --btc-dd (its worst equity drawdown up to 31.5.2026, as a share) is required")
    btc_dd = float(sys.argv[sys.argv.index("--btc-dd") + 1]) if "--btc-dd" in sys.argv else 0.0
    if "--test" in sys.argv:
        a, b, u, f, s = sys.argv[sys.argv.index("--test") + 1].split(",")
        t = c[(c.index >= TEST[0]) & (c.index <= TEST[1])]
        print("TEST:", simulate(t, float(a), float(b), float(u), float(f), s == "1", btc_dd))
        return
    sel = c[(c.index >= SEL[0]) & (c.index <= SEL[1])]
    steps = [i / 10 for i in range(11)]
    has_btc = "btc" in c
    for scen, bull_ok in (("A", True), ("B", False)):
        rows = []
        for wa, wb, wu in itertools.product(steps, steps if has_btc else [0.0], steps if bull_ok else [0.0]):
            if wa + wb + wu > 1.0 + 1e-9 or (wa > 0 and wb > 0) or wa + wb + wu == 0:
                continue
            for f in ((0.1, 0.2, 0.3, 0.4, 0.5) if wa > 0 else (0.0,)):
                for sw in (False,):       # weekly sweep removed from the search (plan, review 4)
                    m, dd = simulate(sel, wa, wb, wu, f, sw, btc_dd)
                    rows.append((wa, wb, wu, f, sw, m, dd))      # full precision; rounded only for printing
        t = pd.DataFrame(rows, columns=["acc", "btc", "bull", "f", "sweep", "mult", "dd"])
        ok = t[t.dd >= -15].sort_values("mult", ascending=False)
        if ok.empty:
            print(f"scenario {scen}: no mix within -15%"); continue
        best = ok.iloc[0]
        tie = ok[ok["mult"] >= best["mult"] * 0.95].sort_values("dd", ascending=False).iloc[0]
        print(f"scenario {scen}: {len(t)} mixes, {len(ok)} within -15%. top 5:")
        print(ok.head(5).round({"mult": 4, "dd": 3}).to_string(index=False))
        print(f"chosen ({scen}): acc={tie.acc} btc={tie.btc} bull={tie.bull} f={tie.f} sweep={tie.sweep} -> x{tie['mult']:.4f} / {tie.dd:.3f}%")


if __name__ == "__main__":
    main()
