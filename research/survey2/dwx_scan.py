import re, sys, json, html, time, urllib.request, datetime as dt, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dwx", "pages")
os.makedirs(OUT, exist_ok=True)

def get(t):
    p = os.path.join(OUT, t + ".html")
    if os.path.exists(p):
        return open(p, encoding="utf-8", errors="replace").read()
    req = urllib.request.Request("https://www.darwinex.com/invest/" + t, headers={"User-Agent": "Mozilla/5.0"})
    try:
        s = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    except Exception as e:
        return ""
    open(p, "w", encoding="utf-8").write(s)
    time.sleep(0.7)
    return s

def text(s):
    s = re.sub(r"<script.*?</script>|<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s))

def metrics(t):
    s = get(t)
    m = re.search(r'"ALL":\s*(\[\[.*?\]\])', s, re.S)
    if not m:
        return None
    data = json.loads(m.group(1))
    cd = re.search(r"creationDate:\s*(\d+)", s)
    pn = re.search(r'productName:\s*"([^"]+)"', s)
    ts = [(dt.datetime.utcfromtimestamp(a / 1000), v) for a, v in data]
    first, last = ts[0], ts[-1]
    yrs = (last[0] - first[0]).days / 365.25
    cagr = (last[1] / first[1]) ** (1 / yrs) - 1 if yrs > 0 else 0
    peak, mdd, mdd_date = 0, 0, None
    for d, v in ts:
        peak = max(peak, v)
        dd = v / peak - 1
        if dd < mdd:
            mdd, mdd_date = dd, d
    # last 2y
    cut = last[0] - dt.timedelta(days=730)
    sub = [x for x in ts if x[0] >= cut]
    r2 = (sub[-1][1] / sub[0][1]) ** (1 / 2) - 1 if sub else None
    # worst calendar-year, yearly returns
    yr = {}
    for d, v in ts:
        yr.setdefault(d.year, [v, v])
        yr[d.year][1] = v
    years = {}
    prev = None
    for y in sorted(yr):
        start = prev if prev else yr[y][0]
        years[y] = round((yr[y][1] / start - 1) * 100, 1)
        prev = yr[y][1]
    tx = text(s)
    def grab(pat):
        mm = re.search(pat, tx)
        return mm.group(1) if mm else ""
    cdate = dt.datetime.utcfromtimestamp(int(cd.group(1)) / 1000).date() if cd else None
    return dict(t=t, product=pn.group(1) if pn else "", start=str(first[0].date()), end=str(last[0].date()),
                investable=str(cdate), yrs=round(yrs, 1), quote=last[1], cagr=round(cagr * 100, 1),
                mdd=round(mdd * 100, 1), mdd_date=str(mdd_date.date()) if mdd_date else "",
                cagr2y=round(r2 * 100, 1) if r2 is not None else None, years=years,
                assets=grab(r"(Forex[^.]{0,60}CFDs|Indices[^.]{0,40}CFDs|Stocks[^.]{0,40})"),
                dx_cap=grab(r"€\s?([\d,\.]+[kKmM]?)\s*(?:Darwinex|in Darwinex)") ,
                aum=grab(r"\$\s?([\d,\.]+)\s*AuM|AuM[^$€]{0,20}[$€]\s?([\d,\.]+)"),
                investors=grab(r"(\d[\d,]*)\s*investors"),
                trades=grab(r"(\d[\d,]*)\s*trades"),
                win=grab(r"([\d\.]+%)\s*winning"),
                dur=grab(r"([\dDdHhMm ,]+)\s*(?:average|avg)[^.]{0,20}duration"))

if __name__ == "__main__":
    res = []
    for t in sys.argv[1:]:
        r = metrics(t)
        if r:
            res.append(r)
            print(json.dumps({k: r[k] for k in ("t", "start", "end", "investable", "yrs", "cagr", "mdd", "mdd_date", "cagr2y")}))
        else:
            print(json.dumps({"t": t, "err": "no data"}))
    json.dump(res, open(os.path.join(os.path.dirname(OUT), "res_%d.json" % int(time.time())), "w"), indent=1)
