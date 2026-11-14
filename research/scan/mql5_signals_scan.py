"""Public MQL5 signals list scraper (no login): every row of /en/signals/{mt5,mt4}/list pages ->
data/derived/scan/mql5sig/signals_{mt}.csv. Polite: 2 s between pages. Usage: py -3.12 research/scan/mql5_signals_scan.py [mt5|mt4] [max_pages]"""
import sys, re, time, html
import requests, pandas as pd
MT = sys.argv[1] if len(sys.argv) > 1 else "mt5"; MAXP = int(sys.argv[2]) if len(sys.argv) > 2 else 400
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36", "Accept-Language": "en"}

def num(s):
    s = html.unescape(s).replace("\xa0", "").replace(" ", "").replace(",", "").replace("%", "")
    m = re.match(r"(-?[\d.]+)([KM]?)", s)
    if not m: return None
    v = float(m.group(1)); return v * {"": 1, "K": 1e3, "M": 1e6}[m.group(2)]

def cell(row, cls):
    m = re.search(r'<div class="col-%s[^"]*"[^>]*>(.*?)</div>' % cls, row, re.S)
    return re.sub(r"<[^>]+>", " ", m.group(1)).strip() if m else ""

rows = []
for p in range(1, MAXP + 1):
    u = f"https://www.mql5.com/en/signals/{MT}/list/page{p}" if p > 1 else f"https://www.mql5.com/en/signals/{MT}/list"
    try: t = requests.get(u, headers=H, timeout=30).text
    except Exception as e: print("err", p, e); time.sleep(10); continue
    parts = t.split('<div class="row signal">')[1:]
    if not parts: print("no rows at page", p); break
    for r in parts:
        sid = re.search(r"/en/signals/(\d+)", r); name = re.search(r'<span class="name">(.*?)</span>', r, re.S)
        g = re.search(r'col-growth[^"]*" title="Profit/Month: (-?[\d.]+)%">(.*?)</div>', r, re.S)
        rows.append({"id": int(sid.group(1)) if sid else None, "name": html.unescape(name.group(1)) if name else "",
                     "real": "ico_state real" in r, "pm": float(g.group(1)) if g else None, "growth": num(g.group(2)) if g else None,
                     "subs": num(cell(r, "subscribers")), "weeks": num(cell(r, "weeks")), "ea_pct": num(cell(r, "experts")),
                     "trades": num(cell(r, "trades")), "win": num(cell(r, "plus")), "pf": num(cell(r, "pf")),
                     "dd": num(cell(r, "drawdown")), "lev": cell(r, "leverage"), "balance": num(cell(r, "balance")), "page": p})
    if p % 20 == 0: print("page", p, "rows", len(rows), flush=True)
    time.sleep(2)
d = pd.DataFrame(rows).drop_duplicates("id"); d.to_csv(f"data/derived/scan/mql5sig/signals_{MT}.csv", index=False)
print("total", len(d))
f = d[d.real & (d.weeks >= 78) & (d.pm >= 3) & (d.dd <= 25)]
print("real, >=78 weeks, >=3%/mo, DD<=25%:", len(f))
print(f.sort_values("pm", ascending=False).head(60).to_string(index=False))
