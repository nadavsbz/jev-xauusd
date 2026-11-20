#!/usr/bin/env python3
"""t_orbslip: ORB exit-mechanism slippage cross-check per PREREG.md (sha256 0216adb3...869b7).
Input: Dukascopy m1 bid/ask CSVs raw/<sym>-<bid|ask>-<year>.csv (dukascopy-node output).
Output: trades.csv.gz + RESULTS tables printed as markdown."""
import glob, os, sys, gc, numpy as np, pandas as pd
RAW = os.environ.get("RAW", "/workspace/tmp_orb/raw")
OUT = os.environ.get("OUT", "/workspace/claude_bridge/out_20261117/t_orbslip")
COMM = 0.0035; SLIPS = [0.0, 0.01, 0.02]
BUCKETS = [0, 0.10, 0.25, 0.50, 1.00, np.inf]; BLAB = ["<0.10", "0.10-0.25", "0.25-0.50", "0.50-1.00", ">=1.00"]

def load(sym):
    parts = {}
    for side in ("bid", "ask"):
        fs = sorted(glob.glob(f"{RAW}/{sym}-{side}-*.csv"))
        if not fs: return None
        d = pd.concat([pd.read_csv(f) for f in fs]).drop_duplicates("timestamp").set_index("timestamp").sort_index()
        parts[side] = d
    b, a = parts["bid"].align(parts["ask"], join="inner")
    m = (b + a) / 2
    m["spread"] = a["open"] - b["open"]
    m["ask_o"], m["bid_o"], m["ask_c"], m["bid_c"] = a["open"], b["open"], a["close"], b["close"]
    m["ask_h"], m["ask_l"], m["bid_h"], m["bid_l"] = a["high"], a["low"], b["high"], b["low"]
    t = pd.to_datetime(m.index, unit="ms", utc=True).tz_convert("America/New_York")
    m["date"] = t.date; m["hm"] = t.hour * 100 + t.minute
    return m[(m.hm >= 930) & (m.hm <= 1559)]

def run(sym):
    m = load(sym)
    if m is None or m.empty: return None, None
    stats = {"sym": sym, "days_raw": m.date.nunique()}
    g = m.groupby("date")
    daily = pd.DataFrame({"o": g.open.first(), "h": g.high.max(), "l": g.low.min(), "c": g.close.last(), "n": g.size()})
    flat = ((m.open == m.high) & (m.high == m.low) & (m.low == m.close) & (m.close.diff() == 0))
    stats["flat_share"] = float(flat.mean())
    # validity
    daily["gap"] = daily.o / daily.c.shift(1) - 1
    first6 = m[m.hm.isin([930, 931, 932, 933, 934, 935])].groupby("date").size()
    daily["first6"] = first6.reindex(daily.index).fillna(0)
    valid = (daily.n >= 380) & (daily.first6 == 6) & ~(daily.gap.abs() > 0.30)
    stats["drop_short_or_gappy"] = int(((daily.n < 380) | (daily.first6 < 6)).sum())
    stats["drop_split_like"] = int((daily.gap.abs() > 0.30).sum())
    dv = daily[valid].copy()
    pc = dv.c.shift(1).where(~(dv.gap.abs() > 0.30))  # previous close; split-like jumps -> use H-L only
    pc = pc.where(dv.o / dv.c.shift(1) - 1 <= 0.30).where(dv.o / dv.c.shift(1) - 1 >= -0.30)  # also across dropped days
    tr = pd.concat([dv.h - dv.l, (dv.h - pc).abs(), (dv.l - pc).abs()], axis=1).max(axis=1)
    dv["atr"] = tr.rolling(14).mean().shift(1)  # strictly prior days
    trades = []
    for d, bars in m[m.date.isin(set(dv.index[dv.atr.notna()]))].groupby("date"):
        bars = bars.set_index("hm")
        O = bars.at[930, "open"]; C = bars.at[934, "close"]
        if C == O: trades.append((sym, d, 0, np.nan, np.nan, np.nan, np.nan, 0, np.nan, np.nan)); continue
        di = 1 if C > O else -1
        atr = dv.at[d, "atr"]; R = 0.10 * atr
        e = bars.at[935, "open"]; stop = e - di * R
        rest = bars.loc[935:1559]
        if di == 1:
            hit = rest.low.values <= stop
        else:
            hit = rest.high.values >= stop
        if hit.any():
            k = int(np.argmax(hit)); op = rest.open.values[k]
            x = min(stop, op) if di == 1 else max(stop, op)
            if k == 0: x = stop  # entry bar: entry==open, so stop at stop price
            stopped = 1; xr = rest.iloc[k]
            # sensitivity B fills (cross spread at bid/ask, stop executes at stop on the side touched)
            xb = x - di * (xr.ask_o - xr.bid_o) / 2
        else:
            x = rest.close.values[-1]; stopped = 0; xr = rest.iloc[-1]
            xb = xr.bid_c if di == 1 else xr.ask_c
        eb = bars.at[935, "ask_o"] if di == 1 else bars.at[935, "bid_o"]
        gR = di * (x - e) / R; gRb = di * (xb - eb) / R
        trades.append((sym, d, di, e, x, R, gR, stopped, gRb, bars.at[935, "spread"]))
    t = pd.DataFrame(trades, columns=["sym", "date", "dir", "entry", "exit", "Rps", "grossR", "stopped", "grossR_xspread", "spread935"])
    stats["doji"] = int((t.dir == 0).sum())
    return t[t.dir != 0], stats

def summ(t):
    return pd.Series({"n": len(t), "meanR": t.grossR.mean(), "medianR": t.grossR.median(), "win": (t.grossR > 0).mean(),
                      "stop%": t.stopped.mean()})

def main():
    syms = sorted({os.path.basename(f).split("-")[0] for f in glob.glob(f"{RAW}/*.csv")})
    allt, allst = [], []
    for s in syms:
        t, st = run(s)
        if t is None: continue
        allt.append(t); allst.append(st); print(s, len(t), flush=True, file=sys.stderr); gc.collect()
    T = pd.concat(allt); S = pd.DataFrame(allst).set_index("sym")
    T["year"] = pd.to_datetime(T.date).dt.year
    for s in SLIPS:
        T[f"costR_{s:.2f}"] = 2 * (s + COMM) / T.Rps
        T[f"netR_{s:.2f}"] = T.grossR - T[f"costR_{s:.2f}"]
    T["bucket"] = pd.cut(T.Rps, BUCKETS, labels=BLAB, right=False)
    T.to_csv(f"{OUT}/trades.csv.gz", index=False, float_format="%.6g", compression={"method": "gzip", "mtime": 0})
    out = []
    P = lambda *a: out.append(" ".join(str(x) for x in a))
    P("## Overall (gross, mid prices)"); P(summ(T).to_frame("all").T.round(4).to_markdown())
    rows = []
    for s in SLIPS:
        rows.append({"slip $/sh/side": s, "mean costR (incl. comm)": T[f"costR_{s:.2f}"].mean(),
                     "median costR": T[f"costR_{s:.2f}"].median(), "mean netR": T[f"netR_{s:.2f}"].mean(),
                     "median netR": T[f"netR_{s:.2f}"].median(), "net win%": (T[f"netR_{s:.2f}"] > 0).mean()})
    rows.append({"slip $/sh/side": "xspread (sens. B, no comm)", "mean netR": T.grossR_xspread.mean(),
                 "median netR": T.grossR_xspread.median(), "net win%": (T.grossR_xspread > 0).mean()})
    P("\n## Overall cost in R"); P(pd.DataFrame(rows).round(4).to_markdown(index=False))
    rows = []
    for b, g in T.groupby("bucket", observed=True):
        r = {"R$ bucket": b, "n": len(g), "share": len(g) / len(T), "median R$": g.Rps.median(), "mean grossR": g.grossR.mean(),
             "median grossR": g.grossR.median(), "win%": (g.grossR > 0).mean()}
        for s in SLIPS:
            r[f"costR@{s:.2f}"] = g[f"costR_{s:.2f}"].mean(); r[f"netR@{s:.2f}"] = g[f"netR_{s:.2f}"].mean()
        r["netR xspread"] = g.grossR_xspread.mean()
        rows.append(r)
    P("\n## By risk-per-share bucket (R$ = 0.10*ATR14)"); P(pd.DataFrame(rows).round(4).to_markdown(index=False))
    rows = []
    for y, g in T.groupby("year"):
        r = summ(g).to_dict(); r["year"] = y; r["median R$"] = g.Rps.median()
        for s in SLIPS: r[f"netR@{s:.2f}"] = g[f"netR_{s:.2f}"].mean()
        rows.append(r)
    P("\n## By year"); P(pd.DataFrame(rows).set_index("year").round(4).to_markdown())
    rows = []
    for sy, g in T.groupby("sym"):
        r = summ(g).to_dict(); r["sym"] = sy; r["median R$"] = g.Rps.median()
        r["med spread935 $"] = g.spread935.median(); r["med spread/R$"] = (g.spread935 / g.Rps).median()
        for s in SLIPS: r[f"netR@{s:.2f}"] = g[f"netR_{s:.2f}"].mean()
        r["flat_share"] = S.at[sy, "flat_share"]; r["dropped days"] = S.at[sy, "drop_short_or_gappy"] + S.at[sy, "drop_split_like"]
        r["doji"] = S.at[sy, "doji"]
        rows.append(r)
    P("\n## By stock"); P(pd.DataFrame(rows).set_index("sym").round(4).to_markdown())
    P("\n## Data stats"); P(S.to_markdown())
    text = "\n".join(out)
    open(f"{OUT}/RESULTS.md", "w").write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
