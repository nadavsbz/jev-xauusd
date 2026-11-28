"""t350 (docs/prereg/research_t350.md incl. amendment): do a forum analyst's text targets get hit more than base rate?
Usage: py -3.12 research/social/t350.py fetch|calls|score"""
import glob, json, os, re, sys, time, urllib.request
import numpy as np, pandas as pd

D = "data/raw/sponser"; Y = f"{D}/yahoo"; os.makedirs(Y, exist_ok=True)
YSYM = {"MAOF": "TA35.TA", "NQ": "NQ=F", "ES": "ES=F", "BTC": "BTC-USD"}
KEYS = {"MAOF": ["מעוף", "מעופי", 'ת"א 35', "תא35", 'ת"א35'], "NQ": ["נסדאק", "נאסדק", 'נאסד"ק', "NQ"],
        "ES": ["סנופי", "SPX", "אס אנד פי"], "BTC": ["ביטקוין"],
        "TSLA": ["טסלה"], "PLTR": ["פלנטיר"], "NVDA": ["אנבידיאה", "אנבידה"], "MRNA": ["מודרנה"], "AAPL": ["אפל"],
        "MSFT": ["מיקרוסופט"], "AMZN": ["אמזון"], "GOOGL": ["גוגל"], "META": ["מטא"]}
PAST = re.compile(r"הגיע ליעד|הגיעה ליעד|השיג|ביעד|היה יעד")
CALL = re.compile(r"יעד.{0,40}?(\d+(?:\.\d+)?)", re.S)
H = 10


def fetch():
    for k, s in YSYM.items():
        u = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(s)}?period1=1546300800&period2=1795000000&interval=1d"
        j = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60))["chart"]["result"][0]
        q = j["indicators"]["quote"][0]; tz = j["meta"]["exchangeTimezoneName"]
        df = pd.DataFrame(dict(o=q["open"], h=q["high"], l=q["low"], c=q["close"]), index=pd.to_datetime(j["timestamp"], unit="s", utc=True).tz_convert(tz).date)
        df.dropna().to_csv(f"{Y}/{k}.csv"); print(k, len(df)); time.sleep(2)


def bars(inst):
    if inst in YSYM: b = pd.read_csv(f"{Y}/{inst}.csv", index_col=0, parse_dates=True)
    else:
        R = []
        for f in sorted(glob.glob("data/raw/alpaca/daily/*.csv.gz")):
            a = pd.read_csv(f, usecols=["s", "t", "o", "h", "l"]); a = a[a.s == inst]
            if len(a): R.append(a)
        a = pd.concat(R); a.index = pd.to_datetime(a.t.str[:10]); b = a[["o", "h", "l"]]
    b = b[~b.index.duplicated()].sort_index()
    return b[b.index >= "2019-01-01"]


def calls():
    tick = {x["symbol"] for x in json.load(open("data/raw/alpaca/assets.json"))}
    P = pd.read_json(f"{D}/hadar_all.jsonl", lines=True, dtype={"id": str}).drop_duplicates("id")
    out, drop = [], {"past": 0, "inst0": 0, "instN": 0, "nocall": 0}
    for r in P.itertuples():
        t = f"{r.subject} | {r.text}"
        m = CALL.search(t)
        if not m: drop["nocall"] += 1; continue
        if PAST.search(t): drop["past"] += 1; continue
        found = {k for k, ws in KEYS.items() if any(re.search(rf"(?<![א-ת\w]){re.escape(w)}", t) for w in ws)}
        found |= {w for w in re.findall(r"\b[A-Z]{2,5}\b", t) if w in tick and w not in ("NQ", "SPX", "ES", "RSI", "AI", "ATH", "EMA", "SMA", "MACD")}
        if len(found) == 0: drop["inst0"] += 1; continue
        if len(found) > 1: drop["instN"] += 1; continue
        out.append(dict(id=r.id, ts=str(r.ts)[:19], inst=found.pop(), target=float(m.group(1))))
    C = pd.DataFrame(out); C.to_csv(f"{D}/t350_calls.csv", index=False)
    print("calls by instrument:", C.inst.value_counts().to_dict(), "dropped:", drop); return C


def score():
    C = pd.read_csv(f"{D}/t350_calls.csv"); C["date"] = pd.to_datetime(C.ts.str[:10]); rows = []
    cache = {}
    for r in C.itertuples():
        if r.inst not in cache:
            try: cache[r.inst] = bars(r.inst)
            except Exception: cache[r.inst] = None
        b = cache[r.inst]
        if b is None or not len(b): continue
        k = b.index.searchsorted(r.date + pd.Timedelta(days=1))
        if k + H > len(b): continue
        ref = b.o.iloc[k]; dist = r.target / ref - 1
        if abs(dist) > 0.5 or dist == 0: continue
        w = b.iloc[k:k + H]
        hit = (w.h.max() >= r.target) if dist > 0 else (w.l.min() <= r.target)
        o = b.o.values; hh = pd.Series(b.h.values[::-1]).rolling(H).max().values[::-1]; ll = pd.Series(b.l.values[::-1]).rolling(H).min().values[::-1]
        ok = ~np.isnan(hh)
        p = float(np.mean(hh[ok] / o[ok] - 1 >= dist)) if dist > 0 else float(np.mean(ll[ok] / o[ok] - 1 <= dist))
        rows.append(dict(id=r.id, date=r.date, inst=r.inst, dist=dist, hit=bool(hit), p=p))
    S = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    def g(x):
        if not len(x): return {}
        e = x.hit.mean() - x.p.mean(); z = (x.hit.sum() - x.p.sum()) / np.sqrt((x.p * (1 - x.p)).sum())
        return dict(n=len(x), hit=round(float(x.hit.mean()), 3), base=round(float(x.p.mean()), 3), edge_pp=round(float(e * 100), 1), z=round(float(z), 2),
                    up_share=round(float((x.dist > 0).mean()), 2), med_dist_pct=round(float(x.dist.abs().median() * 100), 2))
    h = len(S) // 2
    out = dict(all=g(S), first_half=g(S.iloc[:h]), second_half=g(S.iloc[h:]), by_inst={k: g(v) for k, v in S.groupby("inst") if len(v) >= 5},
               maof=g(S[S.inst == "MAOF"]), maof_halves=[g(S[S.inst == "MAOF"].iloc[:len(S[S.inst == "MAOF"]) // 2]), g(S[S.inst == "MAOF"].iloc[len(S[S.inst == "MAOF"]) // 2:])])
    S.to_csv(f"{D}/t350_scored.csv", index=False); print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    {"fetch": fetch, "calls": calls, "score": score}[sys.argv[1]]()
