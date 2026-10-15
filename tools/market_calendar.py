"""Expected trading days for gold CFDs (XAUUSD), used to check that an M1
download is complete day by day instead of tolerating any short gap.

Gold trades ~23h a day Monday-Friday with one daily break of about an hour.
US market holidays either close it (no bars) or shorten it (fewer bars).
The list is explicit; a weekday not in it must be a full trading day."""
from datetime import date

import numpy as np

CLOSED = {   # no bars expected
    date(2025, 12, 25): "Christmas", date(2026, 1, 1): "New Year", date(2026, 4, 3): "Good Friday",
    date(2026, 12, 25): "Christmas", date(2027, 1, 1): "New Year",
}
SHORT = {    # early close / late open: fewer bars expected
    date(2025, 9, 1): "Labor Day", date(2025, 11, 27): "Thanksgiving", date(2025, 11, 28): "Day after Thanksgiving",
    date(2025, 12, 24): "Christmas Eve", date(2025, 12, 31): "New Year's Eve", date(2026, 1, 19): "MLK Day",
    date(2026, 2, 16): "Presidents Day", date(2026, 5, 25): "Memorial Day", date(2026, 6, 19): "Juneteenth",
    date(2026, 7, 3): "Independence Day (observed)", date(2026, 9, 7): "Labor Day",
    date(2026, 11, 26): "Thanksgiving", date(2026, 11, 27): "Day after Thanksgiving", date(2026, 12, 24): "Christmas Eve",
}
FULL_DAY_MIN_BARS = 1300     # a full day has ~1380 M1 bars
SHORT_DAY_MIN_BARS = 1000
MAX_INTRADAY_GAP_MIN = 65    # the daily break is ~60 min (62 in DST-mismatch weeks)


def check_trading_days(times, first_day, last_full_day):
    """times: sorted epoch seconds of M1 bars. Returns a list of problems
    (empty when complete) for every weekday in [first_day, last_full_day]."""
    t = np.asarray(times, dtype="int64")
    days = t // 86400
    problems = []
    for d64 in np.arange(np.datetime64(first_day), np.datetime64(last_full_day) + 1):
        d = d64.astype(object)
        if d.weekday() >= 5:
            continue
        n = int(d64.astype("datetime64[D]").astype("int64"))
        sel = t[days == n]
        if d in CLOSED:
            if len(sel) > 120:
                problems.append(f"{d}: listed closed ({CLOSED[d]}) but has {len(sel)} bars")
            continue
        need = SHORT_DAY_MIN_BARS if d in SHORT else FULL_DAY_MIN_BARS
        if len(sel) < need:
            problems.append(f"{d}: {len(sel)} bars, expected at least {need}")
            continue
        gap = int(np.diff(sel).max()) // 60 if len(sel) > 1 else 0
        if gap > MAX_INTRADAY_GAP_MIN:
            problems.append(f"{d}: a {gap}-minute gap inside the trading day")
    return problems
