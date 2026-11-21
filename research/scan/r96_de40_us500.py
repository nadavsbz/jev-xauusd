"""Round 96 (prereg docs/prereg/r96_de40_us500_nyopen.md): DE40 vs beta*US500 gap from 08:00 Frankfurt to 09:35 ET -> fade on DE40 09:40-11:25 ET.
Usage: py -3.12 research/scan/r96_de40_us500.py dev|hold"""
import sys
import numpy as np, pandas as pd
from pandas.tseries.holiday import (AbstractHolidayCalendar, Holiday, GoodFriday, EasterMonday, USMartinLutherKingJr, USPresidentsDay,
                                    USMemorialDay, USLaborDay, USThanksgivingDay, nearest_workday)
sys.path.insert(0, "research/scan")
from scan import tcost, E
from scan2 import mismatch
PART = sys.argv[1]; TD = pd.Timedelta; FB = "fb" in sys.argv          # fb: sensitivity only (09:05 fallback for the 08:00 Frankfurt bar), not a gate

class NYSE(AbstractHolidayCalendar):
    rules = [Holiday("NY", month=1, day=1, observance=nearest_workday), USMartinLutherKingJr, USPresidentsDay, GoodFriday, USMemorialDay,
             Holiday("J19", month=6, day=19, start_date="2022-01-01", observance=nearest_workday), Holiday("J4", month=7, day=4, observance=nearest_workday),
             USLaborDay, USThanksgivingDay, Holiday("X", month=12, day=25, observance=nearest_workday)]
class FRA(AbstractHolidayCalendar):
    rules = [Holiday("NY", month=1, day=1), GoodFriday, EasterMonday, Holiday("M1", month=5, day=1)] + [Holiday(f"D{d}", month=12, day=d) for d in (24, 25, 26, 31)]
HOL = set(NYSE().holidays("2017", "2027")) | set(FRA().holidays("2017", "2027"))

def load(s):
    m = pd.read_csv(f"data/derived/scan/m5/{s}.csv"); m.index = pd.to_datetime(m.time, unit="s"); return m[~m.index.duplicated()]
de, us, eu = load("DE40Cash"), load("US500Cash"), load("EURUSD")
tc = tcost("DE40Cash", de.resample("1h").last().dropna()); pt = E.loc[".DE40Cash", "point"]
cost = lambda t: max(tc, de.spread[t] * pt / de.open[t])

rows = []
for d in sorted(set(de.index.normalize())):
    if d.dayofweek > 4 or d in HOL: continue
    k = 6 if mismatch(d) else 7
    t0 = d + TD(hours=9)
    if FB and t0 not in de.index: t0 = t0 + TD(minutes=5)
    t1, te, tx = d + TD(hours=9 + k, minutes=35), d + TD(hours=9 + k, minutes=40), d + TD(hours=11 + k, minutes=25)
    if not all(t in x.index for x in (de, us) for t in (t0, t1)) or not all(t in de.index for t in (te, tx)) or not all(t in eu.index for t in (t0, t1)): continue
    rows.append(dict(d=d, rde=de.open[t1] / de.open[t0] - 1, rus=us.open[t1] / us.open[t0] - 1, feu=abs(eu.open[t1] / eu.open[t0] - 1) > 0.01,
                     ret=de.open[tx] / de.open[te] - 1, c=cost(te) + cost(tx)))
D = pd.DataFrame(rows).set_index("d")
z = pd.Series(np.nan, D.index)
for i in range(40, len(D)):
    w = D.iloc[max(0, i - 60):i]
    b = np.cov(w.rde, w.rus)[0, 1] / w.rus.var(); e = w.rde - b * w.rus
    z.iloc[i] = (D.rde.iloc[i] - b * D.rus.iloc[i] - e.mean()) / e.std()
sig = pd.Series(np.where(z > 2, -1, np.where(z < -2, 1, 0)), D.index).where(~D.feu, 0)
a, b = ("2018", "2022") if PART == "dev" else ("2023", "2026")
T = D.assign(s=sig)[a:b]; T = T[T.s != 0]
net = T.s * T.ret - T.c; gross = T.s * T.ret
tst = net.mean() / net.std() * np.sqrt(len(net)); yrs = net.groupby(net.index.year).sum()
pf = net[net > 0].sum() / -net[net < 0].sum(); nc = net.sum() / T.c.sum()
print(f"{PART} {a}-{b}: days {len(D[a:b])}, eurusd-skip {int(D[a:b].feu.sum())}, trades {len(T)} (long {(T.s > 0).sum()}, short {(T.s < 0).sum()})")
print(f"  gross/trade {gross.mean() * 1e4:.1f}bp  net/trade {net.mean() * 1e4:.1f}bp  cost/trade {T.c.mean() * 1e4:.1f}bp  t {tst:.2f}  PF {pf:.2f}  net/cost {nc:.2f}")
print("  years (net %):", {y: round(v * 100, 2) for y, v in yrs.items()}, "| n/yr", net.groupby(net.index.year).size().to_dict())
ok = (len(T) >= 30 and tst >= 2.0 and (yrs > 0).mean() >= 0.6 and nc >= 2) if PART == "dev" else (net.mean() > 0 and tst >= 1.0 and pf >= 1.2)
print("  ->", "PASS" if ok else "FAIL")
