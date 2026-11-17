"""Round 95 (prereg docs/prereg/r95_i2_coppergold.md): copper/gold 20d change as a long/short weight filter on I2.
Usage: py -3.12 research/stable/r95_i2_coppergold.py fetch|dev|hold"""
import sys, os, json, glob, datetime as dt, contextlib, io
import numpy as np, pandas as pd
PART = sys.argv[1]; RAW = "data/raw/coppergold"
if PART == "fetch":
    import urllib.request
    os.makedirs(RAW, exist_ok=True)
    for s in ("HG=F", "GC=F"):
        u = f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?period1=1483228800&period2={int(dt.datetime.now().timestamp())}&interval=1d"
        d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60))
        f = f"{RAW}/{s[:2]}_{dt.date.today():%Y%m%d}.json"; json.dump(d, open(f, "w")); print("saved", f)
    sys.exit()
sys.path.insert(0, "research/btc"); sys.path.insert(0, "research/stable")
with contextlib.redirect_stdout(io.StringIO()):
    from x2_check import deals

def ser(p):
    r = json.load(open(sorted(glob.glob(f"{RAW}/{p}_*.json"))[-1]))["chart"]["result"][0]
    s = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s").normalize())
    return s.dropna().groupby(level=0).last()
R = pd.concat([ser("HG"), ser("GC")], axis=1, join="inner").dropna(); R = R.iloc[:, 0] / R.iloc[:, 1]
d20 = R / R.shift(20) - 1

def sig_for(day):                                     # last close strictly before `day`
    i = d20.index.searchsorted(day) - 1
    return d20.iloc[i] if i >= 0 else np.nan

rows = []
for y in range(2020, 2027):
    x = deals(f"C:/MT5_JEV_TEST/in2dst_t_{y}.htm"); x = x[x.symbol == ".USTECHCash"].copy()
    x["day"] = pd.to_datetime(x.t, unit="s").dt.normalize()
    lng = ((x.type == "buy") & (x.dir == "in")) | ((x.type == "sell") & (x.dir == "out"))
    sht = ((x.type == "sell") & (x.dir == "in")) | ((x.type == "buy") & (x.dir == "out"))
    x["side"] = np.where(lng, 1, np.where(sht, -1, 0)); x["pnl"] = x.profit + x.swap + x.commission
    rows.append(x[["day", "side", "pnl"]])
X = pd.concat(rows)
sg = X.day.map(lambda d: sig_for(d))
w = np.where(sg > 0, np.where(X.side < 0, 0.5, 1.0), np.where(sg < 0, np.where(X.side > 0, 0.5, 1.0), 1.0))
X["pf"] = X.pnl * w

def daily(col):
    out = []
    for y, g in X.groupby(X.day.dt.year):
        p = g.groupby("day")[col].sum(); eq = 120000 + p.cumsum(); out.append(p / eq.shift(1).fillna(120000))
    return pd.concat(out)
def st(r):
    eq = (1 + r).cumprod(); return r.mean() / r.std() * np.sqrt(252), (eq / eq.cummax() - 1).min() * 100, {y: round(g.sum() * 100) for y, g in r.groupby(r.index.year)}
a, b = ("2020", "2022") if PART == "dev" else ("2023", "2026")
base, flt = daily("pnl")[a:b], daily("pf")[a:b]
days = pd.Series(X.day.unique()); days = days[(days >= a) & (days < str(int(b) + 1))]
share = (days.map(sig_for) > 0).mean()
sb, mb, yb = st(base); sf, mf, yf = st(flt)
valid = 0.2 <= share <= 0.8
ok = valid and ((sf >= sb + 0.10 and mf >= mb) if PART == "dev" else (sf >= sb + 0.05 and mf >= mb - 1))
print(f"{PART} {a}-{b}: trade days {len(days)}, d20>0 share {share:.2%} -> {'valid' if valid else 'INVALID'}")
print(f"  BASE Sh {sb:.2f} MDD {mb:.1f} | {yb}")
print(f"  FILT Sh {sf:.2f} ({sf - sb:+.2f}) MDD {mf:.1f} -> {'PASS' if ok else 'FAIL'} | {yf}")
