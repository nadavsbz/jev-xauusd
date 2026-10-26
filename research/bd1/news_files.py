"""News time files for DragonClone_v7 (NewsFile, docs/BD_V7_PLAN.md), in each broker's server clock.
Source: the MT5 economic calendar, USD, exported in UTC by mql5/CalendarExport.mq5 (data/derived/news/mt5_calendar_usd.csv).
Broker clocks, measured from M15 range spikes at US releases (26.10.2026): RoboForex = UTC+2, UTC+3 during US daylight saving;
EGlobal = UTC+2 all year.
Usage: python research/bd1/news_files.py [--check]   (--check: compare with the files already in data/derived/news, write nothing)"""
import shutil, sys
import pandas as pd

D = "data/derived/news/"
CF = "C:/Users/Benza/AppData/Roaming/MetaQuotes/Terminal/Common/Files/"
TOP = "Nonfarm Payrolls|^CPI|Core CPI|Fed Interest Rate Decision|FOMC Press Conference|Core PCE|GDP q/q|PPI m/m|Retail Sales m/m|Fed Chair Powell"

def us_dst(ts):
    """US daylight saving: 2nd Sunday of March 02:00 EST (07:00 UTC) to 1st Sunday of November 02:00 EDT (06:00 UTC)."""
    y = ts.year
    m = pd.Timestamp(y, 3, 1); s = m + pd.Timedelta(days=(6 - m.weekday()) % 7 + 7) + pd.Timedelta(hours=7)
    n = pd.Timestamp(y, 11, 1); e = n + pd.Timedelta(days=(6 - n.weekday()) % 7) + pd.Timedelta(hours=6)
    return s <= ts < e

def build(cal):
    tiers = {"top": cal[(cal.importance == 3) & cal.event.str.contains(TOP, regex=True)],
             "high": cal[cal.importance == 3], "med": cal[cal.importance >= 2]}
    out = {}
    for name, d in tiers.items():
        t = sorted(set(d.time))
        for br in ("rf", "eg"):
            v = [x + (2 + (1 if br == "rf" and us_dst(pd.Timestamp(x, unit="s")) else 0)) * 3600 for x in t]
            out[f"news_{name}_{br}.txt"] = "\n".join(str(x) for x in sorted(v)) + "\n"
    return out

if __name__ == "__main__":
    files = build(pd.read_csv(D + "mt5_calendar_usd.csv", encoding="latin1"))
    for f, txt in files.items():
        if "--check" in sys.argv:
            print(f, "same" if open(D + f).read() == txt else "DIFFERENT")
        else:
            open(D + f, "w").write(txt); shutil.copy(D + f, CF + f); print(f, txt.count("\n"))
