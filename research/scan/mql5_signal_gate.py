"""Gate for MQL5 signals from public pages only (no login). For each candidate id: monthly returns table, balance/equity DD,
max deposit load, holding time, trades/week, algo %, top symbols. Flags: grid/martingale-like (equity DD >> balance DD or deposit
load > 40%), decay (last 6 months avg < 1/3 of overall), gaps. Output data/derived/scan/mql5sig/gate_{tag}.csv
Usage: py -3.12 research/scan/mql5_signal_gate.py signals_mt5.csv [tag]"""
import sys, re, time, json, html
import numpy as np, pandas as pd, requests
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36", "Accept-Language": "en"}
D = "data/derived/scan/mql5sig/"

def grab(txt, pat, f=float):
    m = re.search(pat, txt)
    if not m: return None
    try: return f(m.group(1).replace("\xa0", "").replace(" ", ""))
    except Exception: return None

def page(sid):
    import os
    fp = f"{D}pages/{sid}.html"
    if os.path.exists(fp) and os.path.getsize(fp) > 20000: return open(fp, encoding="utf-8").read()
    time.sleep(8)
    t = requests.get(f"https://www.mql5.com/en/signals/{sid}", headers=H, timeout=30).text
    open(f"{D}pages/{sid}.html", "w", encoding="utf-8").write(t)
    return t

def parse(t):
    txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).replace("\xa0", " ")
    mon = {}; i0 = t.find("table:{years:[")
    if i0 >= 0:
        i0 += len("table:{years:"); dep = 0
        for j in range(i0, len(t)):
            dep += {"[": 1, "]": -1}.get(t[j], 0)
            if dep == 0: break
        s = re.sub(r"(\w+):", r'"\1":', t[i0:j + 1]); s = re.sub(r",\s*([}\]])", r"\1", s)
        s = s.replace('""', '"')
        try:
            for y in json.loads(s):
                for k, v in y["months"].items(): mon[(int(y["year"]), int(k) + 1)] = float(v)
        except Exception as e: pass
    r = {"months": mon,
         "bal_dd": grab(txt, r"Relative drawdown: By Balance: ([\d.]+)%"), "eq_dd": grab(txt, r"By Equity: ([\d.]+)%"),
         "max_dd_pct": grab(txt, r"Maximal: [\d.\s]+ USD \(([\d.]+)%\)"), "load": grab(txt, r"Max deposit load: ([\d.]+)%"),
         "algo": grab(txt, r"Algo trading: ([\d.]+)%"), "tpw": grab(txt, r"Trades per week: ([\d\s]+)"),
         "hold": (re.search(r"Avg holding time: ([^:]+?) (?:Recovery|Subscribers|Sharpe|Weeks)", txt) or [None, None])[1],
         "sharpe": grab(txt, r"Sharpe Ratio: (-?[\d.]+)"), "pf": grab(txt, r"Profit Factor: ([\d.]+)"),
         "broker": (re.search(r"growth since \d{4} [\d\s]+% (\S+)", txt) or [None, None])[1],
         "since": grab(txt, r"growth since (\d{4})", int),
         "deposits": grab(t, r"deposits:([\d.]+)"), "withdrawals": grab(t, r"withdrawals:([\d.]+)"),
         "syms": " ".join(re.findall(r"Distribution Symbol Deals Sell Buy ((?:[A-Z.#a-z0-9]+ [\d\s.K]+ ){1,4})", txt)[:1]).strip()[:80]}
    return r

if __name__ == "__main__":
    import os; os.makedirs(D + "pages", exist_ok=True)
    src = sys.argv[1]; tag = sys.argv[2] if len(sys.argv) > 2 else "mt5"
    c = pd.read_csv(D + src); c = c[c.real & (c.weeks >= 78) & (c.pm >= 3) & (c.dd <= 25)]
    out = []
    for i, row in enumerate(c.itertuples()):
        try: r = parse(page(int(row.id)))
        except Exception as e: print("fail", row.id, e); continue
        m = pd.Series(r.pop("months")).sort_index()
        m = m[m.index.map(lambda k: pd.Timestamp(k[0], k[1], 1) < pd.Timestamp("2026-11-01"))]
        act = m[m != 0]
        last6 = m.iloc[-6:] if len(m) >= 6 else m
        geo = (np.prod(1 + m) ** (1 / max(len(m), 1)) - 1) * 100 if len(m) else np.nan
        out.append({"id": row.id, "name": row.name, "weeks": row.weeks, "list_pm": row.pm, "list_dd": row.dd, "subs": row.subs,
                    "n_months": len(m), "pos_share": round((m > 0).mean() * 100) if len(m) else None,
                    "geo_pm": round(geo, 2), "worst_m": round(m.min() * 100, 1) if len(m) else None,
                    "last6_pm": round((np.prod(1 + last6) ** (1 / max(len(last6), 1)) - 1) * 100, 2) if len(m) else None,
                    "top3_share": round(m.nlargest(3).sum() / m[m > 0].sum() * 100) if (m > 0).any() else None,
                    "zero_months": int((m == 0).sum()), **r})
        if i % 10 == 0: print(i, len(c), flush=True)
        pass
    g = pd.DataFrame(out)
    g["grid_flag"] = (g.eq_dd > 2 * g.bal_dd.clip(lower=1)) | (g.load > 40)
    g["decay_flag"] = g.last6_pm < g.geo_pm / 3
    g.to_csv(f"{D}gate_{tag}.csv", index=False)
    ok = g[~g.grid_flag & ~g.decay_flag & (g.pos_share >= 70) & (g.n_months >= 18) & (g.top3_share <= 50)]
    print(f"candidates {len(c)}, parsed {len(g)}, clean {len(ok)}")
    print(ok.sort_values("geo_pm", ascending=False).to_string(index=False))
