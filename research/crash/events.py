"""Scheduled US releases for stage 1 (docs/CRASH_DETECT_PLAN.md), written to events.csv in UTC.
- FOMC decisions, 14:00 New York, on the LAST day of each scheduled meeting, parsed from
  federalreserve.gov (fomchistoricalYYYY.htm saved as fomcYYYY.htm for 2015-2020, fomccalendars.htm saved as fomc.htm for 2021 on).
- NFP, 08:30 New York, on the first Friday of each month. ASSUMED: the usual rule; the real
  date differs in some months (e.g. when the first Friday is very early or a holiday).
- CPI is not included: the BLS schedule pages refuse automated downloads (deviation from the plan).
Usage: python research/crash/events.py PAGES_DIR OUT_CSV"""
import glob, os, re, sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
M = "January|February|March|April|May|June|July|August|September|October|November|December"
MON3 = {m[:3]: i + 1 for i, m in enumerate(M.split("|"))}


def _mon(name):
    return MON3.get(name.split("/")[-1][:3].title())


def fomc(pages):
    """Last day of each SCHEDULED meeting (unscheduled ones were not known in advance)."""
    out = set()
    for f in glob.glob(os.path.join(pages, "fomc20*.htm")):
        txt = open(f, encoding="utf-8", errors="ignore").read()
        for mon, days, y in re.findall(r"<h5[^>]*>\s*([A-Za-z]+(?:/[A-Za-z]+)?) ([\d-]+) Meeting - (\d{4})</h5>", txt):
            if _mon(mon):
                out.add(date(int(y), _mon(mon), int(re.findall(r"\d+", days)[-1])))
    txt = open(os.path.join(pages, "fomc.htm"), encoding="utf-8", errors="ignore").read()
    for block in re.split(r"<h4[^>]*>", txt)[1:]:
        ym = re.search(r"(\d{4}) FOMC Meetings", block[:300])
        if not ym:
            continue
        y = int(ym.group(1))
        # each row runs to the next month cell; a policy meeting has a statement (a notation vote does not)
        for row in block.split("fomc-meeting__month")[1:]:
            m = re.match(r'[^>]*><strong>([A-Za-z/]+)</strong></div>\s*<div class="fomc-meeting__date[^"]*">([^<]+)<', row)
            if not m or "Statement:" not in row or "notation" in m.group(2).lower():
                continue
            mon, days = m.groups()
            dd = re.findall(r"\d{1,2}", days)
            if dd and "unscheduled" not in days.lower() and _mon(mon):
                out.add(date(y, _mon(mon), int(dd[-1])))
    return sorted(d for d in out if 2015 <= d.year <= 2026)


def nfp():
    out = []
    for y in range(2015, 2027):
        for m in range(1, 13):
            d = date(y, m, 1)
            out.append(d + timedelta(days=(4 - d.weekday()) % 7))
    return out


def main():
    pages, dst = sys.argv[1], sys.argv[2]
    rows = [(datetime(d.year, d.month, d.day, 14, 0, tzinfo=NY), "FOMC") for d in fomc(pages)]
    rows += [(datetime(d.year, d.month, d.day, 8, 30, tzinfo=NY), "NFP") for d in nfp()]
    with open(dst, "w", encoding="utf-8") as f:
        f.write("utc,kind\n")
        for t, k in sorted(rows):
            f.write(f"{t.astimezone(ZoneInfo('UTC')).strftime('%Y-%m-%d %H:%M')},{k}\n")
    print(len(rows), "events;", sum(k == "FOMC" for _, k in rows), "FOMC")


if __name__ == "__main__":
    main()
