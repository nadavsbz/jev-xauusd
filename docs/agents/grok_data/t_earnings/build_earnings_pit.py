#!/usr/bin/env python3
"""Point-in-time US earnings-announcement-date table from SEC EDGAR 8-K Item 2.02.

Stages (python3 build_earnings_pit.py <stage>):
  index : download EDGAR full-index form.idx 2014Q1..2026Q4, collect every CIK that filed 8-K or 8-K/A
  fetch : for each such CIK download https://data.sec.gov/submissions/CIK##########.json
          (+ overflow 'files' JSONs whose filingTo >= 2014-01-01); keep only 8-K/8-K/A/10-Q/10-K rows
          -> work/sub_rows.jsonl.gz , work/sub_meta.jsonl.gz      (resumable)
  build : build earnings_pit.csv.gz + coverage stats (stats.json)

Fair access: <= 8 requests/s, generic descriptive User-Agent without personal data.
(The bulk submissions.zip at /Archives/edgar/daily-index/bulk/ returned HTTP 403 "temporarily
unavailable / maintenance" on 17.11.2026, so the per-CIK API route is used.)
"""
import sys, os, json, gzip, time, glob, threading, re
from concurrent.futures import ThreadPoolExecutor
import requests

UA = "GrokBot-research earnings-pit-builder research-contact@example.org"  # generic, non-personal
WORK = os.environ.get("WORK", "/workspace/tmp_earn")
OUT = os.environ.get("OUT", "/workspace/claude_bridge/out_20261117/t_earnings")
KEEP_FORMS = {"8-K", "8-K/A", "10-Q", "10-K", "10-Q/A", "10-K/A", "6-K", "20-F", "40-F"}
MIN_DATE = "2014-01-01"

_lock = threading.Lock(); _last = [0.0]
def get(url, tries=5):
    for t in range(tries):
        with _lock:  # global rate limiter, 8 req/s
            wait = _last[0] + 0.125 - time.time()
            if wait > 0: time.sleep(wait)
            _last[0] = time.time()
        try:
            r = requests.get(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip, deflate"}, timeout=60)
            if r.status_code == 200: return r
            if r.status_code == 404: return None
            time.sleep(2 * (t + 1))
        except requests.RequestException:
            time.sleep(2 * (t + 1))
    return None

def stage_index():
    ciks = set()
    for y in range(2014, 2027):
        for q in (1, 2, 3, 4):
            f = f"{WORK}/form_{y}Q{q}.idx"
            if not os.path.exists(f) or os.path.getsize(f) == 0:
                r = get(f"https://www.sec.gov/Archives/edgar/full-index/{y}/QTR{q}/form.idx")
                if r is None: continue
                open(f, "wb").write(r.content)
            for line in open(f, encoding="latin-1"):
                if line.startswith("8-K ") or line.startswith("8-K/A "):
                    ciks.add(int(line.split()[-3]))
    open(f"{WORK}/ciks_8k.txt", "w").write("\n".join(map(str, sorted(ciks))))
    print("ciks", len(ciks))

def cols_to_rows(d, cik):
    out = []
    n = len(d.get("accessionNumber", []))
    for i in range(n):
        form = d["form"][i]
        if form not in KEEP_FORMS: continue
        fd = d["filingDate"][i]
        if fd < MIN_DATE: continue
        out.append({"cik": cik, "acc": d["accessionNumber"][i], "form": form, "filingDate": fd,
                    "reportDate": d.get("reportDate", [""] * n)[i], "accept": d["acceptanceDateTime"][i],
                    "items": d.get("items", [""] * n)[i]})
    return out

def fetch_one(cik):
    r = get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json")
    if r is None: return cik, None, []
    j = r.json()
    rows = cols_to_rows(j["filings"]["recent"], cik)
    for f in j["filings"].get("files", []):
        if f.get("filingTo", "9999") >= MIN_DATE:
            r2 = get("https://data.sec.gov/submissions/" + f["name"])
            if r2 is not None: rows += cols_to_rows(r2.json(), cik)
    meta = {k: j.get(k) for k in ("cik", "name", "tickers", "exchanges", "sic", "sicDescription", "entityType",
                                  "category", "stateOfIncorporation", "fiscalYearEnd", "formerNames")}
    meta["cik"] = cik
    return cik, meta, rows

def stage_fetch():
    ciks = [int(x) for x in open(f"{WORK}/ciks_8k.txt").read().split()]
    done = set()
    if os.path.exists(f"{WORK}/done.txt"):
        done = {int(x) for x in open(f"{WORK}/done.txt").read().split()}
    todo = [c for c in ciks if c not in done]
    print("todo", len(todo), flush=True)
    fr = gzip.open(f"{WORK}/sub_rows.jsonl.gz", "at"); fm = gzip.open(f"{WORK}/sub_meta.jsonl.gz", "at")
    fd = open(f"{WORK}/done.txt", "a")
    with ThreadPoolExecutor(6) as ex:
        for k, (cik, meta, rows) in enumerate(ex.map(fetch_one, todo)):
            if meta is not None:
                fm.write(json.dumps(meta) + "\n")
                for r in rows: fr.write(json.dumps(r) + "\n")
            fd.write(f"{cik}\n")
            if k % 500 == 0:
                print(k, time.strftime("%H:%M:%S"), flush=True); fr.flush(); fm.flush(); fd.flush()
    fr.close(); fm.close(); fd.close()

def stage_build():
    import pandas as pd, numpy as np
    rows = pd.read_json(f"{WORK}/sub_rows.jsonl.gz", lines=True, dtype={"acc": str, "items": str, "reportDate": str})
    meta = pd.read_json(f"{WORK}/sub_meta.jsonl.gz", lines=True).drop_duplicates("cik").set_index("cik")
    rows = rows.drop_duplicates("acc")
    periodic = rows[rows.form.isin(["10-Q", "10-K", "10-Q/A", "10-K/A"])].groupby("cik").size()
    e = rows[rows.form.isin(["8-K", "8-K/A"]) & rows["items"].fillna("").str.contains(r"(?:^|,)\s*2\.02")].copy()
    e["acceptance_utc"] = pd.to_datetime(e.accept, utc=True)   # VERIFIED: JSON 'Z' is true UTC (AAPL header check)
    e["acceptance_ts_ny"] = e.acceptance_utc.dt.tz_convert("America/New_York")
    hm = e.acceptance_ts_ny.dt.hour * 100 + e.acceptance_ts_ny.dt.minute
    e["timing"] = np.where(hm < 930, "before_open", np.where(hm >= 1600, "after_close", "during_market"))
    e["accept_date_ny"] = e.acceptance_ts_ny.dt.date.astype(str)
    e["weekday_ny"] = e.acceptance_ts_ny.dt.dayofweek
    e["is_amendment"] = (e.form == "8-K/A").astype(int)
    e = e.sort_values(["cik", "acceptance_utc"]).reset_index(drop=True)
    # ---- point-in-time helper columns (only past filings of the same CIK are used) ----
    orig = e[e.is_amendment == 0]
    prox, pdiff, prev_gap, n365 = {}, {}, {}, {}
    for cik, g in orig.groupby("cik"):
        t = g.acceptance_utc.values.astype("datetime64[s]").astype(np.int64) / 86400.0
        d = g.accept_date_ny.values; idx = g.index.values
        for i in range(len(g)):
            past = t[:i]
            prev_gap[idx[i]] = (t[i] - past[-1]) if i else np.nan
            n365[idx[i]] = int(((t[i] - past) <= 365).sum()) if i else 0
            if i:
                lag = t[i] - past
                ok = np.where((lag >= 320) & (lag <= 410))[0]   # same fiscal quarter one year back (+-45 d)
                if len(ok):
                    j = ok[np.argmin(np.abs(lag[ok] - 365))]
                    prox[idx[i]] = d[j]; pdiff[idx[i]] = round(lag[j], 2)
    e["prior_year_announce_date"] = pd.Series(prox)
    e["prior_year_lag_days"] = pd.Series(pdiff)
    e["expected_date_proxy"] = [ (pd.Timestamp(p) + pd.DateOffset(years=1)).date().isoformat() if isinstance(p, str) else ""
                                 for p in e.prior_year_announce_date ]
    e["days_since_prev_202"] = pd.Series(prev_gap).round(2)
    e["n_202_prev_365d"] = pd.Series(n365)
    e["likely_dup_or_nonearnings"] = ((e.days_since_prev_202 < 30) & (e.is_amendment == 0)).astype(int)
    # ---- identifiers ----
    tick = {}
    try:
        ct = requests.get("https://www.sec.gov/files/company_tickers.json", headers={"User-Agent": UA}, timeout=60).json()
        for v in ct.values(): tick.setdefault(int(v["cik_str"]), []).append(v["ticker"])
    except Exception as ex:
        print("company_tickers.json failed", ex)
    def tk(c):
        a = tick.get(c) or (meta.at[c, "tickers"] if c in meta.index and isinstance(meta.at[c, "tickers"], list) else [])
        return "|".join(a)
    e["ticker"] = [tk(c) for c in e.cik]
    e["company_name"] = [meta.at[c, "name"] if c in meta.index else "" for c in e.cik]
    e["exchange"] = ["|".join(x for x in (meta.at[c, "exchanges"] or []) if x) if c in meta.index and isinstance(meta.at[c, "exchanges"], list) else "" for c in e.cik]
    e["sic"] = [meta.at[c, "sic"] if c in meta.index else "" for c in e.cik]
    e["files_10q_10k"] = [int(periodic.get(c, 0) > 0) for c in e.cik]
    cols = ["ticker", "cik", "company_name", "exchange", "sic", "acc", "form", "is_amendment", "items", "filingDate",
            "reportDate", "acceptance_ts_ny", "accept_date_ny", "weekday_ny", "timing", "expected_date_proxy",
            "prior_year_announce_date", "prior_year_lag_days", "days_since_prev_202", "n_202_prev_365d",
            "likely_dup_or_nonearnings", "files_10q_10k"]
    e = e.rename(columns={"acc": "accession"}); cols[cols.index("acc")] = "accession"
    out = e[cols].copy(); out["acceptance_ts_ny"] = out.acceptance_ts_ny.dt.strftime("%Y-%m-%d %H:%M:%S%z")
    out.to_csv(f"{OUT}/earnings_pit.csv.gz", index=False, compression={"method": "gzip", "mtime": 0})
    # ---- stats ----
    out["year"] = out.accept_date_ny.str[:4].astype(int)
    st = {"rows": len(out), "ciks": int(out.cik.nunique()), "ciks_fetched": int(len(meta))}
    st["per_year"] = out.groupby("year").agg(filings=("accession", "size"), originals=("is_amendment", lambda x: int((x == 0).sum())),
        amendments=("is_amendment", "sum"), unique_ciks=("cik", "nunique"),
        share_with_ticker=("ticker", lambda x: round(float((x != "").mean()), 4)),
        share_with_proxy=("expected_date_proxy", lambda x: round(float((x != "").mean()), 4)),
        before_open=("timing", lambda x: int((x == "before_open").sum())),
        during_market=("timing", lambda x: int((x == "during_market").sum())),
        after_close=("timing", lambda x: int((x == "after_close").sum())),
        likely_dup=("likely_dup_or_nonearnings", "sum")).reset_index().to_dict("records")
    o = out[out.is_amendment == 0]
    st["timing_all"] = o.timing.value_counts(normalize=True).round(4).to_dict()
    st["weekend_share"] = round(float((o.weekday_ny >= 5).mean()), 4)
    okp = o[o.expected_date_proxy != ""].copy()
    if len(okp):
        dlt = (pd.to_datetime(okp.accept_date_ny) - pd.to_datetime(okp.expected_date_proxy)).dt.days
        ad = dlt.abs()
        st["proxy_absdiff_days"] = {
            "n_with_proxy": int(len(okp)),
            "share_originals_with_proxy": round(float(len(okp) / max(len(o), 1)), 4),
            "mean_signed": round(float(dlt.mean()), 2),
            "median_signed": round(float(dlt.median()), 2),
            "mean_abs": round(float(ad.mean()), 2),
            "median_abs": round(float(ad.median()), 2),
            "p90_abs": round(float(ad.quantile(0.90)), 2),
            "within_1d": round(float((ad <= 1).mean()), 4),
            "within_7d": round(float((ad <= 7).mean()), 4),
            "within_14d": round(float((ad <= 14).mean()), 4),
        }
    else:
        st["proxy_absdiff_days"] = None
    st["share_originals_with_ticker"] = round(float((o.ticker != "").mean()), 4)
    st["notes"] = {
        "source": "SEC EDGAR submissions API (data.sec.gov/submissions) + full-index form.idx 2014Q1-2026Q4",
        "item_filter": "8-K or 8-K/A whose items field contains 2.02",
        "timezone": "acceptanceDateTime is UTC (Z); converted to America/New_York",
        "timing_rule": "before_open if NY time < 09:30; after_close if >= 16:00; else during_market",
        "expected_date_proxy": "same-CIK original (non-amendment) 2.02 filing 320-410 days earlier, plus 1 calendar year; no look-ahead",
        "ticker_caveat": "ticker is CURRENT (company_tickers.json, then submissions tickers[]); CIK is the point-in-time identifier",
        "bulk_zip": "submissions.zip returned HTTP 403 on 17.11.2026; per-CIK API used instead",
        "year_range": "2014 included so 2015 proxies have a prior-year anchor; requested range was 2015-2026",
    }
    for path in (f"{WORK}/stats.json", f"{OUT}/stats.json"):
        json.dump(st, open(path, "w"), indent=1, default=str)
    print(json.dumps(st, indent=1, default=str)[:4000])

if __name__ == "__main__":
    st = sys.argv[1]
    if st == "index": stage_index()
    elif st == "fetch": stage_fetch()
    elif st == "build": stage_build()
