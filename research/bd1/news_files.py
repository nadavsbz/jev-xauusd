"""News time files for DragonClone_v7 (NewsFile, docs/BD_V7_PLAN.md), in each broker's server clock.
Source: the MT5 economic calendar, USD, exported in UTC by mql5/CalendarExport.mq5 (data/derived/news/mt5_calendar_usd.csv).
Broker clocks, measured from M15 range spikes at US releases (26.10.2026): RoboForex = UTC+2, UTC+3 during US daylight saving;
EGlobal = UTC+2 all year.
Usage: python research/bd1/news_files.py [--check | --refresh]
  --check:   compare with the files already in data/derived/news, write nothing
  --refresh: first copy the latest CalendarExport output (Common\\Files\\news_usd_all.csv) over mt5_calendar_usd.csv, then build
             (the weekly demo refresh, docs/BD_REGIME2_PLAN.md; Codex PR 42, P1: the export never reached the build input)"""
import shutil, sys
import pandas as pd

D = "data/derived/news/"
CF = "C:/Users/Benza/AppData/Roaming/MetaQuotes/Terminal/Common/Files/"
TOP = "Nonfarm Payrolls|^CPI|Core CPI|Fed Interest Rate Decision|FOMC Press Conference|Core PCE|GDP q/q|PPI m/m|Retail Sales m/m|Fed Chair Powell"

def us_dst(ts):
    """US daylight saving: 2nd Sunday of March 02:00 EST (07:00 UTC) to 1st Sunday of November 02:00 EDT (06:00 UTC)."""
    y = ts.year
    m = pd.Timestamp(y, 3, 1); s = m + pd.Timedelta(days=int((6 - m.weekday()) % 7 + 7)) + pd.Timedelta(hours=7)
    n = pd.Timestamp(y, 11, 1); e = n + pd.Timedelta(days=int((6 - n.weekday()) % 7)) + pd.Timedelta(hours=6)
    return s <= ts < e

def check_utc(cal):
    """The calendar times must be UTC (Codex PR 41, P1: MT5 returns trade-server time). Anchor: every NFP is 08:30 New York,
    i.e. 13:30 UTC in winter and 12:30 UTC in US daylight saving. Known exception in the MT5 calendar: the delayed September 2025
    report (after the shutdown) released 20.11.2025 08:30 New York = 13:30 UTC is listed at 12:30 UTC, an hour early (a calendar
    error, not a clock shift); it is kept as listed, so that one window opens an hour early."""
    nfp = cal[cal.event == "Nonfarm Payrolls"]
    bad = [x for x in nfp.time if (pd.Timestamp(x, unit="s").hour, pd.Timestamp(x, unit="s").minute) != ((12 if us_dst(pd.Timestamp(x, unit="s")) else 13), 30)]
    bad = [x for x in bad if x != 1763641800]   # 2025-11-20 12:30 UTC, the known exception
    assert len(nfp) > 0 and not bad, f"calendar not in UTC: {len(bad)} of {len(nfp)} NFP releases off 08:30 New York"
    return len(nfp)

def build(cal):
    check_utc(cal)
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
    if "--refresh" in sys.argv:
        shutil.copy(CF + "news_usd_all.csv", D + "mt5_calendar_usd.csv")
    files = build(pd.read_csv(D + "mt5_calendar_usd.csv", encoding="latin1"))
    for f, txt in files.items():
        if "--check" in sys.argv:
            print(f, "same" if open(D + f).read() == txt else "DIFFERENT")
        else:
            open(D + f, "w").write(txt); shutil.copy(D + f, CF + f); print(f, txt.count("\n"))
    if "--check" not in sys.argv:   # coverage: the demo needs the last top event at least 14 days ahead
        last = max(int(x) for x in files["news_top_eg.txt"].split())
        days = (last - pd.Timestamp.now(tz="UTC").timestamp()) / 86400
        print(f"last top event {pd.Timestamp(last, unit='s')} (EGlobal clock), {days:.0f} days ahead", "OK" if days >= 14 else "SHORT: export again")
