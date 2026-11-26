"""t409 (docs/prereg/research_t409.md): beta_clock = OLS slope of r_last (15:30->16:00 ET) on r_rest (prev close->15:30 ET),
for SPY/IWM/DIA/SMH/XLF (+QQQ control), Alpaca 30Min bars (read-only, key from git-ignored alpaca_key.json, never printed).
MEASUREMENT 2020-2023, STABILITY 2024-01..2026-10-31. Weekly-block bootstrap (B=2000, seed 409), Holm over 5 names.
Usage: py -3.12 research/stable/t409.py"""
import json, os, time, urllib.request, urllib.parse
import numpy as np, pandas as pd
K = json.load(open("alpaca_key.json")); H = {"APCA-API-KEY-ID": K["key_id"], "APCA-API-SECRET-KEY": K["secret"]}
RAW = "data/raw/alpaca/t409"; os.makedirs(RAW, exist_ok=True)
SYMS = ["SPY", "IWM", "DIA", "SMH", "XLF", "QQQ"]


def bars(sym):
    f = f"{RAW}/{sym}_30m.csv.gz"
    if os.path.exists(f): return pd.read_csv(f, parse_dates=["t"])
    rows, tok = [], None
    while True:
        q = dict(symbols=sym, timeframe="30Min", start="2019-12-20T00:00:00Z", end="2026-11-01T00:00:00Z", limit=10000, adjustment="all", feed="sip")
        if tok: q["page_token"] = tok
        for k in range(6):
            try:
                r = json.load(urllib.request.urlopen(urllib.request.Request("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q), headers=H), timeout=60)); break
            except Exception:
                time.sleep(5 * (k + 1))
        rows += r.get("bars", {}).get(sym, []) or []
        tok = r.get("next_page_token"); time.sleep(0.31)
        if not tok: break
    d = pd.DataFrame(rows).rename(columns={"t": "t"}); d["t"] = pd.to_datetime(d.t); d.to_csv(f, index=False, compression="gzip"); return d


def daily(d):
    d = d.copy(); d["et"] = d.t.dt.tz_convert("America/New_York"); d["day"] = d.et.dt.date; d["hm"] = d.et.dt.strftime("%H:%M")
    rth = d[(d.hm >= "09:30") & (d.hm < "16:00")]
    g = rth.groupby("day")
    out = pd.DataFrame({"n": g.size(), "p1530": rth[rth.hm == "15:00"].set_index("day").c, "close": g.c.last()})   # bar 15:00-15:30 closes at 15:30
    out = out[out.n == 13].dropna()                                    # full sessions only (half days have fewer bars)
    out["prev"] = out.close.shift(1); out = out.dropna()
    out["r_rest"] = out.p1530 / out.prev - 1; out["r_last"] = out.close / out.p1530 - 1
    out.index = pd.to_datetime(out.index); return out


def beta(x, y): return float(np.cov(x, y, ddof=0)[0, 1] / np.var(x))


def boot(df, B=2000, seed=409):
    rng = np.random.default_rng(seed); wk = df.index.to_period("W"); groups = [g for _, g in df.groupby(wk)]
    bs = []
    for _ in range(B):
        s = pd.concat([groups[i] for i in rng.integers(0, len(groups), len(groups))]); bs.append(beta(s.r_rest, s.r_last))
    return np.array(bs)


if __name__ == "__main__":
    res = {}
    for s in SYMS:
        D = daily(bars(s)); M = D["2020":"2023"]; S = D["2024":"2026-10-31"]
        bm, bs = beta(M.r_rest, M.r_last), beta(S.r_rest, S.r_last); BM = boot(M)
        p_one = float((BM <= 0).mean())                                 # one-sided bootstrap p for beta>0
        res[s] = dict(n_meas=len(M), n_stab=len(S), beta_meas=round(bm, 5), ci90_meas=[round(float(np.percentile(BM, 5)), 5), round(float(np.percentile(BM, 95)), 5)],
                      p_one=round(p_one, 4), beta_stab=round(bs, 5))
    tested = [s for s in SYMS if s != "QQQ"]; order = sorted(tested, key=lambda s: res[s]["p_one"])
    for i, s in enumerate(order):                                       # Holm, alpha 5%
        res[s]["holm_alpha"] = round(0.05 / (len(order) - i), 4)
    passed_prev = True
    for s in order:
        ok1 = passed_prev and res[s]["p_one"] <= res[s]["holm_alpha"]; passed_prev = ok1
        ok2 = res[s]["beta_stab"] > 0 and res[s]["beta_stab"] >= 0.5 * res[s]["beta_meas"] if res[s]["beta_meas"] > 0 else False
        res[s].update(gate1=ok1, gate2=ok2, PASS=ok1 and ok2)
    res["QQQ"]["note"] = "control, not counted"
    os.makedirs("docs/evidence", exist_ok=True); json.dump(res, open("docs/evidence/t409.json", "w"), indent=1)
    print(json.dumps(res, indent=1))
