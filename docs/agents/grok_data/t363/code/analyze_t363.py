#!/usr/bin/env python3
"""t363 analysis: locked windows, percentiles, reverse-causality from 1-min bars."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

OUT = Path("/workspace/t363/data")
ET = "America/New_York"

def load_daily(sym):
    df = pd.read_csv(OUT / f"{sym}_daily_2024_2026.csv")
    df["t"] = pd.to_datetime(df["t"], utc=True).dt.tz_convert(ET)
    df["date"] = df["t"].dt.date
    df = df.sort_values("date").drop_duplicates("date")
    return df

def load_iex_daily(sym):
    p = OUT / f"{sym}_daily_iex_recent.csv"
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_csv(p)
    df["t"] = pd.to_datetime(df["t"], utc=True).dt.tz_convert(ET)
    df["date"] = df["t"].dt.date
    return df.sort_values("date")

def load_1m(paths):
    frames = []
    for p in paths:
        if Path(p).exists():
            d = pd.read_csv(p)
            frames.append(d)
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    df["t"] = pd.to_datetime(df["t"], utc=True).dt.tz_convert(ET)
    df = df.sort_values("t").drop_duplicates("t")
    return df

def session_mask(df, start="09:30", end="16:00"):
    tod = df["t"].dt.strftime("%H:%M")
    return (tod >= start) & (tod <= end)

def bar_at_or_before(df, ts):
    ts = pd.Timestamp(ts).tz_convert(ET) if pd.Timestamp(ts).tzinfo else pd.Timestamp(ts, tz=ET)
    sub = df[df["t"] <= ts]
    if sub.empty:
        return None
    return sub.iloc[-1]

def first_bar_on_or_after(df, ts):
    ts = pd.Timestamp(ts).tz_convert(ET) if pd.Timestamp(ts).tzinfo else pd.Timestamp(ts, tz=ET)
    sub = df[df["t"] >= ts]
    if sub.empty:
        return None
    return sub.iloc[0]

def close_on(daily, date):
    d = pd.Timestamp(date).date()
    row = daily[daily["date"] == d]
    if row.empty:
        return None
    return float(row.iloc[0]["c"])

def trading_days(daily):
    return list(daily["date"])

def shift_td(dates, d, n):
    """n trading days after date d; n=0 is d if it is a trading day, else next."""
    if d in dates:
        i = dates.index(d)
    else:
        # next trading day after d
        later = [x for x in dates if x > d]
        if not later:
            return None
        i = dates.index(later[0])
        # if looking for close-before and d is not a trading day, already handled elsewhere
    j = i + n
    if j < 0 or j >= len(dates):
        return None
    return dates[j]

def prev_td(dates, d):
    earlier = [x for x in dates if x < d]
    return earlier[-1] if earlier else None

def pct_rank(series, value):
    s = pd.Series(series).dropna()
    if s.empty or value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    # percentile of values <= value (lower tail is more negative)
    return float((s <= value).mean() * 100)

def ret(a, b):
    if a is None or b is None or a == 0:
        return None
    return b / a - 1

# ---- daily universe ----
results = {"symbols": {}, "events": {}, "notes": []}
all_dates = None
for sym in ["SPY", "QQQ"]:
    d = load_daily(sym)
    iex = load_iex_daily(sym)
    # do not use iex Nov 23 as official close (session may be open)
    results["symbols"][sym] = {
        "n_days": int(len(d)),
        "first": str(d["date"].iloc[0]),
        "last_official": str(d["date"].iloc[-1]),
        "iex_recent_dates": [str(x) for x in iex["date"]] if not iex.empty else [],
        "iex_recent_closes": {str(r["date"]): float(r["c"]) for _, r in iex.iterrows()} if not iex.empty else {},
    }
    d = d.copy()
    d["ret_1d"] = d["c"].pct_change()
    d["ret_3d"] = d["c"].pct_change(3)
    d.to_csv(OUT / f"{sym}_daily_with_rets.csv", index=False)
    results["symbols"][sym]["ret_1d_mean"] = float(d["ret_1d"].mean())
    results["symbols"][sym]["ret_1d_std"] = float(d["ret_1d"].std())
    results["symbols"][sym]["n_ret_1d"] = int(d["ret_1d"].notna().sum())
    results["symbols"][sym]["n_ret_3d"] = int(d["ret_3d"].notna().sum())

# Use SPY calendar
spy = load_daily("SPY")
qqq = load_daily("QQQ")
dates = trading_days(spy)
assert trading_days(qqq) == dates

# official daily map
closes = {sym: {r["date"]: float(r["c"]) for _, r in load_daily(sym).iterrows()} for sym in ["SPY", "QQQ"]}

# Locked events
events = {
    "E1": {
        "name": "Ansari first November call",
        "event_ts": "2026-11-04 13:54:39-05:00",
        "close_before_date": "2026-11-03",
        "d1_date": "2026-11-04",
        "d3_date": "2026-11-06",
        "descriptive_session": "2026-11-05",
        "intraday_files": {
            "SPY": [str(OUT / "SPY_1m_E1.csv")],
            "QQQ": [str(OUT / "QQQ_1m_E1.csv")],
        },
    },
    "E2": {
        "name": "Ansari second November call",
        "event_ts": "2026-11-16 23:31:38-05:00",
        "close_before_date": "2026-11-16",
        "d1_date": "2026-11-17",
        "d3_date": "2026-11-19",
        "intraday_files": {
            "SPY": [str(OUT / "SPY_1m_E2.csv")],
            "QQQ": [str(OUT / "QQQ_1m_E2.csv")],
        },
    },
    "E3": {
        "name": "Ansari third November call",
        "event_ts": "2026-11-23 00:00:46-05:00",
        "close_before_date": "2026-11-20",
        "d1_date": "2026-11-23",
        "d3_date": "2026-11-25",
        "intraday_files": {
            "SPY": [str(OUT / "SPY_1m_E3_fri.csv"), str(OUT / "SPY_1m_E3_mon.csv")],
            "QQQ": [str(OUT / "QQQ_1m_E3_fri.csv"), str(OUT / "QQQ_1m_E3_mon.csv")],
        },
        "d1_incomplete": True,
        "d3_not_yet": True,
    },
}

# build 1d/3d distributions (close-to-close, using official daily only)
dist = {}
for sym in ["SPY", "QQQ"]:
    d = load_daily(sym).copy()
    d["ret_1d"] = d["c"].pct_change()
    d["ret_3d"] = d["c"].pct_change(3)
    dist[sym] = {
        "ret_1d": d["ret_1d"].dropna().tolist(),
        "ret_3d": d["ret_3d"].dropna().tolist(),
        "dates_1d": [str(x) for x in d.loc[d["ret_1d"].notna(), "date"]],
        "dates_3d": [str(x) for x in d.loc[d["ret_3d"].notna(), "date"]],
    }
    # also map date -> return ending that day
    dist[sym]["map_1d"] = {str(r["date"]): float(r["ret_1d"]) for _, r in d.dropna(subset=["ret_1d"]).iterrows()}
    dist[sym]["map_3d"] = {str(r["date"]): float(r["ret_3d"]) for _, r in d.dropna(subset=["ret_3d"]).iterrows()}

def rth_slice(df, day):
    day = pd.Timestamp(day).date()
    sub = df[df["t"].dt.date == day]
    rth = sub[session_mask(sub)]
    return sub, rth

def summarize_bar(row):
    if row is None:
        return None
    return {
        "t": str(row["t"]),
        "o": float(row["o"]),
        "h": float(row["h"]),
        "l": float(row["l"]),
        "c": float(row["c"]),
        "v": float(row.get("v", 0) or 0),
    }

out_events = {}
for eid, ev in events.items():
    ev_out = {"meta": {k: v for k, v in ev.items() if k != "intraday_files"}}
    ev_out["returns"] = {}
    ev_out["intraday"] = {}
    for sym in ["SPY", "QQQ"]:
        cb = pd.Timestamp(ev["close_before_date"]).date()
        d1 = pd.Timestamp(ev["d1_date"]).date()
        d3 = pd.Timestamp(ev["d3_date"]).date()
        c_before = closes[sym].get(cb)
        c_d1 = closes[sym].get(d1)
        c_d3 = closes[sym].get(d3)
        status_d1 = "official_close" if c_d1 is not None else "missing"
        status_d3 = "official_close" if c_d3 is not None else "missing"
        # E3: maybe iex partial
        iex_map = results["symbols"][sym]["iex_recent_closes"]
        snapshot = None
        if c_d1 is None and ev.get("d1_incomplete"):
            status_d1 = "INCOMPLETE_session_open"
            # last 1-min RTH close-ish
            mm = load_1m(ev["intraday_files"][sym])
            if not mm.empty:
                rth = mm[session_mask(mm)]
                last = rth.iloc[-1] if not rth.empty else mm.iloc[-1]
                snapshot = summarize_bar(last)
                c_d1_snap = float(last["c"])
            else:
                c_d1_snap = None
            # also record iex daily if present, still incomplete
            iex_c = iex_map.get(str(d1))
        else:
            c_d1_snap = None
            iex_c = iex_map.get(str(d1))

        r1 = ret(c_before, c_d1) if c_d1 is not None else ret(c_before, c_d1_snap)
        r3 = ret(c_before, c_d3)
        p1 = pct_rank(dist[sym]["ret_1d"], r1) if r1 is not None and status_d1 == "official_close" else None
        p3 = pct_rank(dist[sym]["ret_3d"], r3) if r3 is not None else None

        ev_out["returns"][sym] = {
            "close_before": c_before,
            "close_1d": c_d1,
            "close_3d": c_d3,
            "status_1d": status_d1,
            "status_3d": status_d3,
            "ret_1d": r1,
            "ret_3d": r3,
            "percentile_1d_vs_2024_2026": p1,
            "percentile_3d_vs_2024_2026": p3,
            "n_1d_universe": len(dist[sym]["ret_1d"]),
            "n_3d_universe": len(dist[sym]["ret_3d"]),
            "incomplete_snapshot": snapshot,
            "iex_daily_same_date": iex_c,
        }

        # descriptive Nov 5 session for E1
        if ev.get("descriptive_session"):
            ds = pd.Timestamp(ev["descriptive_session"]).date()
            prev = prev_td(dates, ds)
            ev_out["returns"][sym]["descriptive_Nov5_session_ret"] = ret(closes[sym].get(prev), closes[sym].get(ds))
            ev_out["returns"][sym]["descriptive_Nov5_percentile_1d"] = pct_rank(
                dist[sym]["ret_1d"], ret(closes[sym].get(prev), closes[sym].get(ds))
            )

        # intraday reverse causality
        mm = load_1m(ev["intraday_files"][sym])
        ts = pd.Timestamp(ev["event_ts"])
        intra = {"event_ts": ev["event_ts"]}
        if mm.empty:
            intra["error"] = "no_bars"
        else:
            # previous official close
            intra["prev_official_close"] = c_before
            # bar at/before event
            b_ev = bar_at_or_before(mm, ts)
            intra["bar_at_or_before_event"] = summarize_bar(b_ev)
            # event day RTH
            event_day = ts.date()
            # for after-close / before-open events, "event day session" may be previous or next
            # E1: event during 11/4 RTH
            # E2: after 11/16 close -> look at 11/16 RTH (before) and 11/17 RTH (after)
            # E3: before 11/23 open -> look at 11/20 RTH (before) and 11/23 so far (after)
            days_present = sorted(set(mm["t"].dt.date.tolist()))
            intra["days_present"] = [str(x) for x in days_present]
            day_stats = {}
            for day in days_present:
                allb, rth = rth_slice(mm, day)
                if rth.empty:
                    # maybe premarket only
                    day_stats[str(day)] = {
                        "n_all": int(len(allb)),
                        "n_rth": 0,
                        "first_any": summarize_bar(allb.iloc[0]) if not allb.empty else None,
                        "last_any": summarize_bar(allb.iloc[-1]) if not allb.empty else None,
                    }
                    continue
                first, last = rth.iloc[0], rth.iloc[-1]
                # move from prev close to open, open to last, and from open to time-of-event if same day
                day_stats[str(day)] = {
                    "n_rth": int(len(rth)),
                    "open": float(first["o"]),
                    "rth_high": float(rth["h"].max()),
                    "rth_low": float(rth["l"].min()),
                    "last_rth": float(last["c"]),
                    "last_rth_t": str(last["t"]),
                    "session_ret_open_to_last": float(last["c"] / first["o"] - 1),
                    "from_prev_close_to_open": (float(first["o"] / c_before - 1) if c_before and day >= cb else None),
                    "from_prev_close_to_last": (float(last["c"] / c_before - 1) if c_before else None),
                }
            intra["day_stats"] = day_stats

            # specific reverse-causality checks
            if b_ev is not None and c_before:
                intra["ret_prev_close_to_event_bar"] = float(b_ev["c"] / c_before - 1)
            # RTH open of event calendar day (or next session)
            if eid == "E1":
                _, rth = rth_slice(mm, "2026-11-04")
                if not rth.empty and b_ev is not None:
                    intra["E1_ret_open_to_event"] = float(b_ev["c"] / rth.iloc[0]["o"] - 1)
                    intra["E1_ret_event_to_close"] = float(rth.iloc[-1]["c"] / b_ev["c"] - 1)
                    # was the day already down before the post?
                    intra["E1_already_down_before_post"] = bool(b_ev["c"] < rth.iloc[0]["o"] or (c_before and b_ev["c"] < c_before))
                    intra["E1_down_from_open_before_post"] = bool(b_ev["c"] < rth.iloc[0]["o"])
                    intra["E1_down_from_prev_close_before_post"] = bool(c_before and b_ev["c"] < c_before)
                # Nov 5 open vs Nov 4 close, and around Musk 02:46
                _, rth5 = rth_slice(mm, "2026-11-05")
                c4 = closes[sym].get(pd.Timestamp("2026-11-04").date())
                if not rth5.empty and c4:
                    intra["Nov5_open"] = float(rth5.iloc[0]["o"])
                    intra["Nov5_gap_from_Nov4_close"] = float(rth5.iloc[0]["o"] / c4 - 1)
                    intra["Nov5_session_ret"] = float(rth5.iloc[-1]["c"] / rth5.iloc[0]["o"] - 1)
                # premarket Nov 5 around Musk 02:46 EST (bars may start later, ~4am or 8am)
                all5, _ = rth_slice(mm, "2026-11-05")
                musk = pd.Timestamp("2026-11-05 02:46:52-05:00")
                b_before_musk = bar_at_or_before(all5, musk) if not all5.empty else None
                b_after_musk = first_bar_on_or_after(all5, musk) if not all5.empty else None
                intra["Nov5_first_bar"] = summarize_bar(all5.iloc[0] if not all5.empty else None)
                intra["bar_at_or_before_musk"] = summarize_bar(b_before_musk)
                intra["bar_on_or_after_musk"] = summarize_bar(b_after_musk)
                # 09:30 vs first premarket bar
                if not all5.empty and c4:
                    intra["Nov5_from_Nov4close_to_first_extended_bar"] = float(all5.iloc[0]["c"] / c4 - 1)

            if eid == "E2":
                _, rth16 = rth_slice(mm, "2026-11-16")
                intra["E2_session_Nov16_already_complete_before_post"] = True
                if not rth16.empty and c_before:
                    intra["E2_Nov16_session_ret_open_to_close"] = float(rth16.iloc[-1]["c"] / rth16.iloc[0]["o"] - 1)
                    intra["E2_Nov16_from_prev_Fri_or_before"] = None
                # prev close before Nov 16
                prev16 = prev_td(dates, pd.Timestamp("2026-11-16").date())
                c_prev16 = closes[sym].get(prev16)
                intra["close_Nov13_or_prev"] = c_prev16
                intra["date_before_Nov16"] = str(prev16) if prev16 else None
                intra["E2_Nov16_close_vs_prior_close"] = ret(c_prev16, c_before)
                _, rth17 = rth_slice(mm, "2026-11-17")
                if not rth17.empty and c_before:
                    intra["E2_Nov17_gap"] = float(rth17.iloc[0]["o"] / c_before - 1)
                    intra["E2_Nov17_session"] = float(rth17.iloc[-1]["c"] / rth17.iloc[0]["o"] - 1)
                    intra["E2_Nov17_from_Nov16_close_to_close"] = float(rth17.iloc[-1]["c"] / c_before - 1)

            if eid == "E3":
                _, rth20 = rth_slice(mm, "2026-11-20")
                prev20 = prev_td(dates, pd.Timestamp("2026-11-20").date())
                c_prev20 = closes[sym].get(prev20)
                intra["date_before_Nov20"] = str(prev20) if prev20 else None
                intra["E3_Nov20_vs_prior_close"] = ret(c_prev20, c_before)
                _, rth23 = rth_slice(mm, "2026-11-23")
                all23, _ = rth_slice(mm, "2026-11-23")
                if not all23.empty:
                    intra["E3_Nov23_first_extended"] = summarize_bar(all23.iloc[0])
                    if c_before:
                        intra["E3_from_Fri_close_to_first_extended"] = float(all23.iloc[0]["c"] / c_before - 1)
                if not rth23.empty and c_before:
                    intra["E3_Nov23_open"] = float(rth23.iloc[0]["o"])
                    intra["E3_Nov23_gap"] = float(rth23.iloc[0]["o"] / c_before - 1)
                    intra["E3_Nov23_last"] = float(rth23.iloc[-1]["c"])
                    intra["E3_Nov23_last_t"] = str(rth23.iloc[-1]["t"])
                    intra["E3_Nov23_session_so_far"] = float(rth23.iloc[-1]["c"] / rth23.iloc[0]["o"] - 1)
                    intra["E3_Nov23_from_Fri_close_so_far"] = float(rth23.iloc[-1]["c"] / c_before - 1)

        ev_out["intraday"][sym] = intra

    out_events[eid] = ev_out

# also dump worst 1d days for context
for sym in ["SPY", "QQQ"]:
    d = load_daily(sym).copy()
    d["ret_1d"] = d["c"].pct_change()
    worst = d.nsmallest(10, "ret_1d")[["date", "c", "ret_1d"]]
    worst.to_csv(OUT / f"{sym}_worst10_1d.csv", index=False)
    # rank of Nov 5
    d = d.dropna(subset=["ret_1d"])
    d["rank_asc"] = d["ret_1d"].rank(method="min", ascending=True)
    for day in ["2026-11-04", "2026-11-05", "2026-11-06", "2026-11-16", "2026-11-17", "2026-11-19", "2026-11-20"]:
        row = d[d["date"] == pd.Timestamp(day).date()]
        if not row.empty:
            results.setdefault("day_ranks", {}).setdefault(sym, {})[day] = {
                "ret_1d": float(row.iloc[0]["ret_1d"]),
                "rank_worst": int(row.iloc[0]["rank_asc"]),
                "n": int(len(d)),
            }

results["events"] = out_events
# trim huge lists from saved json
save = results.copy()
# don't store full return lists in json
for sym in save["symbols"]:
    pass
Path("/workspace/t363/data/analysis.json").write_text(json.dumps(save, indent=2, default=str))
print("wrote analysis.json")

# pretty print key numbers
def fmt(x, p=4):
    if x is None:
        return "NA"
    if isinstance(x, float):
        return f"{x*100:.3f}%" if abs(x) < 2 else f"{x:.4f}"
    return str(x)

for eid, ev in out_events.items():
    print("=" * 80)
    print(eid, ev["meta"]["event_ts"])
    for sym, r in ev["returns"].items():
        print(f"  {sym} close_before={r['close_before']} d1={r['close_1d']} ({r['status_1d']}) d3={r['close_3d']} ({r['status_3d']})")
        print(f"       ret1={fmt(r['ret_1d'])} pctl1={r['percentile_1d_vs_2024_2026']}")
        print(f"       ret3={fmt(r['ret_3d'])} pctl3={r['percentile_3d_vs_2024_2026']}")
        if "descriptive_Nov5_session_ret" in r:
            print(f"       Nov5 session={fmt(r['descriptive_Nov5_session_ret'])} pctl={r['descriptive_Nov5_percentile_1d']}")
        if r.get("incomplete_snapshot"):
            print("       snapshot", r["incomplete_snapshot"])
    for sym, intra in ev["intraday"].items():
        print(f"  intra {sym} keys of interest:")
        for k, v in intra.items():
            if k in ("day_stats",):
                print("    day_stats", json.dumps(v, default=str)[:800])
            elif k.startswith("E") or k.startswith("Nov") or "ret_" in k or "already" in k or "gap" in k or "first" in k or "bar_at" in k:
                print(f"    {k}={v}")
