"""One definition of S5 timing for stage 1, stage 2 and the forward log (docs/CRASH_DETECT_PLAN.md):
the GVZ close of day D is treated as published at 16:00 UTC on the next US-exchange business day
(weekends and NYSE/CBOE holidays skipped). ASSUMED: FRED posts it around 17:00 Central European time,
which is 16:00 UTC in winter and 15:00 UTC in summer, so 16:00 UTC is never earlier than the posting."""
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar, GoodFriday, AbstractHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay


class Cboe(AbstractHolidayCalendar):
    """Federal holidays WITHOUT Columbus Day and Veterans Day (exchanges trade on both), plus Good Friday."""
    rules = [r for r in USFederalHolidayCalendar.rules if r.name not in ("Columbus Day", "Veterans Day")] + [GoodFriday]


BDAY = CustomBusinessDay(calendar=Cboe())
DAYS, MIN = 250, 125


def percentile(gvz):
    """Trailing percentile of each observation within the last 250 observations (as before)."""
    return gvz.rolling(DAYS, min_periods=MIN).rank(pct=True).dropna()


def published(pct):
    """Series of the same values indexed by publication time (UTC, naive)."""
    pub = (pct.index.normalize() + BDAY) + pd.Timedelta(hours=16)
    return pd.Series(pct.values, index=pub, name="s5").sort_index()


def at(times_utc, pub):
    """S5 known at each time (UTC, naive): the latest value published at or before it (NaN before any)."""
    left = pd.DataFrame({"t": pd.to_datetime(times_utc)}).reset_index()
    right = pd.DataFrame({"pub": pub.index, "v": pub.values, "obs": pub.index})
    m = pd.merge_asof(left.sort_values("t"), right, left_on="t", right_on="pub", direction="backward").sort_values("index")
    return m.v.values, m.pub.values
