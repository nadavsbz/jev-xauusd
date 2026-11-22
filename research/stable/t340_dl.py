"""t340 data: SEC Form 13F data sets (quarterly zips) into data/raw/sec13f/ (git-ignored). Generic User-Agent, polite pacing.
Usage: py -3.12 research/stable/t340_dl.py"""
import os, re, time, urllib.request
H = {"User-Agent": "research-client admin@example.com"}
OUT = "data/raw/sec13f"; os.makedirs(OUT, exist_ok=True)
x = urllib.request.urlopen(urllib.request.Request("https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets", headers=H), timeout=60).read().decode()
L = sorted(set(re.findall(r'href="([^"]+13f[^"]*\.zip)"', x, re.I)))


def keep(u):
    m = re.search(r"(\d{4})q(\d)_form13f", u)
    if m: return (int(m.group(1)), int(m.group(2))) >= (2015, 4)
    return True                                   # 2024+ date-range files


for u in [u for u in L if keep(u)]:
    f = f"{OUT}/{os.path.basename(u)}"
    if os.path.exists(f): continue
    data = None
    for k in range(5):
        try:
            data = urllib.request.urlopen(urllib.request.Request("https://www.sec.gov" + u, headers=H), timeout=600).read(); break
        except Exception as e:
            print("retry", u, e, flush=True); time.sleep(20 * (k + 1))
    if data is None: print("FAILED", u, flush=True); continue
    open(f, "wb").write(data); print(os.path.basename(u), len(data) // 1_000_000, "MB", flush=True); time.sleep(1)
print("done")
