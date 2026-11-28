"""t430 (docs/prereg/research_t430.md): Top-5 earnings-night long on QQQ. Entry = close of the 5-min bar ending 15:55 ET
on the event day, exit = close of the 5-min bar ending 09:35 ET next session. Earnings timing = EDGAR 8-K Item 2.02
acceptance time. Cost 8bp/trade. Gate A on 2018-2022; gate B (2023-2026.10) only if A passes.
Alpaca key from git-ignored alpaca_key.json (never printed). Generic EDGAR User-Agent. Usage: py -3.12 research/stable/t430.py"""
import json, os, time, urllib.request, urllib.parse
import pandas as pd, numpy as np

RAW = "data/raw/t430"; os.makedirs(RAW, exist_ok=True)
TOP5 = {2018: "AAPL GOOGL MSFT AMZN META", 2019: "MSFT AAPL AMZN GOOGL META", 2020: "AAPL MSFT GOOGL AMZN META",
        2021: "AAPL MSFT AMZN GOOGL META", 2022: "AAPL MSFT GOOGL AMZN TSLA", 2023: "AAPL MSFT GOOGL AMZN TSLA",
        2024: "AAPL MSFT GOOGL AMZN NVDA", 2025: "AAPL NVDA MSFT GOOGL AMZN", 2026: "NVDA AAPL GOOGL MSFT AMZN"}
CIK = {"AAPL": 320193, "MSFT": 789019, "GOOGL": 1652044, "AMZN": 1018724, "META": 1326801, "TSLA": 1318605, "NVDA": 1045810}
COST = 8.0
SEC_H = {"User-Agent": "research-client admin@example.com"}


def get(url, headers, tries=6):
    for k in range(tries):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60))
        except Exception:
            time.sleep(3 * (k + 1))
    raise RuntimeError("fetch failed: " + url.split("?")[0])


def edgar_events(tk):
    f = f"{RAW}/edgar_{tk}.json"
    if not os.path.exists(f):
        d = get(f"https://data.sec.gov/submissions/CIK{CIK[tk]:010d}.json", SEC_H); rows = []
        blocks = [d["filings"]["recent"]] + [get("https://data.sec.gov/submissions/" + x["name"], SEC_H) for x in d["filings"].get("files", [])]
        for b in blocks:
            for form, items, acc in zip(b["form"], b["items"], b["acceptanceDateTime"]):
                if form == "8-K" and "2.02" in str(items): rows.append(acc)
            time.sleep(0.2)
        json.dump(rows, open(f, "w"))
    t = pd.to_datetime(pd.Series(json.load(open(f))), utc=True).dt.tz_convert("America/New_York")
    return t[(t >= "2017-12-01") & (t < "2026-11-01")]


def qqq():
    f = f"{RAW}/QQQ_5m.csv.gz"
    if os.path.exists(f): return pd.read_csv(f, parse_dates=["t"])
    K = json.load(open("alpaca_key.json")); H = {"APCA-API-KEY-ID": K["key_id"], "APCA-API-SECRET-KEY": K["secret"]}
    rows, tok = [], None
    while True:
        q = dict(symbols="QQQ", timeframe="5Min", start="2017-12-01T00:00:00Z", end="2026-11-01T00:00:00Z", limit=10000, adjustment="all", feed="sip")
        if tok: q["page_token"] = tok
        r = get("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q), H)
        rows += r.get("bars", {}).get("QQQ", []) or []; tok = r.get("next_page_token"); time.sleep(0.31)
        if not tok: break
    d = pd.DataFrame(rows); d["t"] = pd.to_datetime(d.t); d.to_csv(f, index=False, compression="gzip"); return d


if __name__ == "__main__":
    B = qqq(); B["et"] = B.t.dt.tz_convert("America/New_York"); B["day"] = B.et.dt.date; B["hm"] = B.et.dt.strftime("%H:%M")
    rth = B[(B.hm >= "09:30") & (B.hm < "16:00")]
    nbar = rth.groupby("day").size(); full = nbar[nbar >= 75].index            # full sessions (78 bars; half days ~42)
    sessions = sorted(rth.day.unique())
    entry = rth[rth.hm == "15:50"].set_index("day").c                        # bar 15:50-15:55 closes at 15:55
    exitp = rth[rth.hm == "09:30"].set_index("day").c                        # bar 09:30-09:35 closes at 09:35
    nxt = {sessions[i]: sessions[i + 1] for i in range(len(sessions) - 1)}
    prev = {sessions[i + 1]: sessions[i] for i in range(len(sessions) - 1)}
    ev = []
    for tk in sorted(CIK):
        for ts in edgar_events(tk):
            if tk not in TOP5.get(ts.year, "").split(): continue
            hm = ts.strftime("%H:%M"); d = ts.date()
            if hm >= "16:00": day = d if d in nxt else None
            elif hm < "09:30": day = prev.get(d) if d in set(sessions) else None
            else: day = None                                                  # intraday release: excluded
            ev.append(dict(tk=tk, acc=str(ts), day=day))
    E = pd.DataFrame(ev); excl = int(E.day.isna().sum()); E = E.dropna()
    E = E[E.tk.isin([t for t in CIK])]
    nights = E.groupby("day").tk.apply(lambda s: ",".join(sorted(set(s)))).reset_index()
    T = []
    for _, r in nights.iterrows():
        d = r.day; n = nxt.get(d)
        if n is None or d not in full or n not in full or d not in entry.index or n not in exitp.index: continue
        g = (exitp[n] / entry[d] - 1) * 1e4; T.append(dict(day=pd.Timestamp(d), tks=r.tk, gross_bp=g, net_bp=g - COST))
    T = pd.DataFrame(T); T["year"] = T.day.dt.year
    T.to_csv(f"{RAW}/t430_trades.csv", index=False)

    def stats(X):
        y = X.groupby("year").net_bp.sum()
        top5 = X.gross_bp.nlargest(5).sum(); tot = X.gross_bp.sum()
        contrib = {tk: X[X.tks.str.contains(tk)].gross_bp.sum() for tk in CIK}
        best = max(contrib, key=contrib.get); wo = X[~X.tks.str.contains(best)].net_bp.sum()
        return dict(n=len(X), years_pos=f"{int((y > 0).sum())}/{len(y)}", net_by_year_bp={int(k): round(v, 1) for k, v in y.items()},
                    mean_gross_bp=round(X.gross_bp.mean(), 2), mean_net_bp=round(X.net_bp.mean(), 2),
                    top5_share=round(top5 / tot, 3) if tot > 0 else None, best_tk=best, net_without_best_bp=round(wo, 1)), y, top5, tot, wo
    A = T[T.year.between(2018, 2022)]; sA, yA, t5, tot, wo = stats(A)
    gA = dict(years=(yA > 0).sum() >= 4, mean16=A.gross_bp.mean() >= 16, conc=(tot > 0 and t5 / tot <= 0.5), drop_best=wo > 0)
    out = dict(excluded_intraday_or_unmatched=excl, A=sA, gateA=gA, PASS_A=all(gA.values()))
    if out["PASS_A"]:
        Bp = T[T.year >= 2023]; sB, yB, *_ = stats(Bp)
        out["B"] = sB; out["PASS_B"] = bool((yB[yB.index <= 2025] > 0).sum() >= 2 and Bp.net_bp.mean() > 0)
    os.makedirs("docs/evidence", exist_ok=True); json.dump(out, open("docs/evidence/t430.json", "w"), indent=1, default=str)
    print(json.dumps(out, indent=1, default=str))
