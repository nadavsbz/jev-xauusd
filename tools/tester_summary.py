"""Turn an MT5 Strategy Tester HTML report into a small JSON evidence file:
sha256 of the report, the tester settings and inputs it lists, its summary
figures, and figures recomputed from its deal table (entries, commission,
swap, trading P&L without deposits, daily returns). The report holds no login
or password (checked before committing); only this summary enters the repo."""
import hashlib, json, re, sys
import pandas as pd


def main(src, dst):
    raw = open(src, "rb").read()
    text = raw.decode("utf-16")
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S)
    cells = [[re.sub("<.*?>", "", x).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)] for r in rows]
    pairs, inputs = {}, []
    for c in cells:
        for i in range(len(c) - 1):
            if c[i].endswith(":") and c[i + 1]:
                pairs.setdefault(c[i].rstrip(":"), c[i + 1])
        for v in c:
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", v):
                inputs.append(v)
    deals = [c for c in cells if len(c) == 13 and re.match(r"\d{4}\.\d\d\.\d\d", c[0])]
    d = pd.DataFrame(deals, columns=["time", "deal", "symbol", "type", "dir", "volume", "price", "order",
                                     "commission", "swap", "profit", "balance", "comment"])
    for col in ["volume", "price", "commission", "swap", "profit", "balance"]:
        d[col] = pd.to_numeric(d[col].str.replace(",", "").str.replace(" ", ""), errors="coerce")
    d["t"] = pd.to_datetime(d.time, format="%Y.%m.%d %H:%M:%S")
    dep = d.type == "balance"
    trade = d[~dep]
    deposit = d.profit[dep].sum()
    # per WEEKDAY of the tested range: days without a closed deal count as 0
    # (P&L is booked at deal time, so this is realised P&L per day)
    day = trade.groupby(trade.t.dt.normalize())[["profit", "commission", "swap"]].sum().sum(axis=1)
    # the tested range comes from the report's period field, "M30 (2025.03.31 - 2026.10.14)",
    # so days without deals at either end still count
    period = next((v for v in pairs.values() if re.search(r"\(\d{4}\.\d\d\.\d\d - \d{4}\.\d\d\.\d\d\)", v)), None)
    if period:
        a, b = re.search(r"\((\d{4}\.\d\d\.\d\d) - (\d{4}\.\d\d\.\d\d)\)", period).groups()
        rng = pd.bdate_range(pd.Timestamp(a.replace(".", "-")), pd.Timestamp(b.replace(".", "-")))
        day = day.reindex(rng, fill_value=0.0)
    elif len(day):
        day = day.reindex(pd.bdate_range(day.index.min(), day.index.max()), fill_value=0.0)
    bal_start = deposit if deposit else float("nan")
    daily = day / bal_start * 100
    out = {
        "report_file": src.replace("\\", "/").split("/")[-1],
        "report_sha256": hashlib.sha256(raw).hexdigest(),
        "settings": {k: v for k, v in pairs.items() if k in ("יועץ אוטומטי (רובוט)", "צמד", "תקופה", "חברה", "מטבע",
                                                              "פיקדון התחלתי", "מינוף", "איכות היסטוריה")},
        "inputs": inputs,
        "summary_from_report": {k: v for k, v in pairs.items() if k in ("סך רווח נקי", "רווח ברוטו", "הפסד ברוטו",
                                "מאזן הפסד מקסימלי", "שווי הפסד מקסימלי", "מקדם רווח", "סך עסקאות")},
        "recomputed": {
            "deposit": round(deposit, 2),
            "entries": int((trade.dir == "in").sum()),
            "trading_profit_before_costs": round(trade.profit.sum(), 2),
            "commission": round(trade.commission.sum(), 2),
            "swap": round(trade.swap.sum(), 2),
            "net": round(trade.profit.sum() + trade.commission.sum() + trade.swap.sum(), 2),
            "lots_opened": round(trade.volume[trade.dir == "in"].sum(), 2),
            # per exit deal: price profit + its own commission/swap (entry commission
            # is booked on the entry deal, so it is not in these averages)
            "exit_deals": int((trade.dir == "out").sum()),
            "exit_win_rate_pct": round(float(((ex := trade[trade.dir == "out"]).profit + ex.commission + ex.swap > 0).mean() * 100), 2),
            "exit_avg_win": round(float((ex.profit + ex.commission + ex.swap)[(ex.profit + ex.commission + ex.swap) > 0].mean()), 2),
            "exit_avg_loss": round(float((ex.profit + ex.commission + ex.swap)[(ex.profit + ex.commission + ex.swap) < 0].mean()), 2),
            "daily_realised_pct_of_deposit_per_weekday": {k: round(float(v), 3) for k, v in daily.describe().items()},
            "worst_days_pct": {str(k.date()): round(float(v), 2) for k, v in daily.nsmallest(5).items()},
            "active_days": int((day != 0).sum()),
        },
    }
    # undefined statistics (e.g. no trading days) become null: NaN is not valid JSON
    def clean(v):
        if isinstance(v, dict):
            return {k: clean(x) for k, x in v.items()}
        return None if isinstance(v, float) and v != v else v
    out = clean(out)
    json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1, allow_nan=False)
    print(json.dumps(out["recomputed"], ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
