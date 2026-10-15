"""The exact snapshots the report was computed from. Explicit folders, no
"first glob match": each file is checked against the sha256 in its
manifest, and the deals must sum to the balance recorded at pull time."""
import hashlib, json, os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from market_calendar import check_trading_days  # noqa: E402

RAW = "data/raw/black_dragon_1"
# The report's snapshots. The forward test (docs/BD1_GUARD_FORWARD.md) points
# at newer pulls through the environment; the report itself never does.
DEALS_SNAPSHOT = os.environ.get("JEV_DEALS_SNAPSHOT", "20261015T120553Z")
RATES_SNAPSHOT = os.environ.get("JEV_RATES_SNAPSHOT", "rates_XAUUSDc_M1_20261015T144411Z")
START = pd.Timestamp("2025-11-11").timestamp()   # first deal of magic 5555
MAGIC = 5555
# Forward paper test, registered 2026-10-15 before any of its data existed (docs/BD1_GUARD_FORWARD.md)
FORWARD_START = "2026-10-16"   # inclusive, by basket start (t0, server time)
FORWARD_END = "2027-04-16"     # exclusive: baskets started up to and including 2027-04-15


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load():
    dd = os.path.join(RAW, DEALS_SNAPSHOT); rd = os.path.join(RAW, RATES_SNAPSHOT)
    dm = json.load(open(os.path.join(dd, "manifest.json"), encoding="utf-8"))
    rm = json.load(open(os.path.join(rd, "manifest.json"), encoding="utf-8"))
    if _sha(os.path.join(dd, "deals.csv")) != dm["files"]["deals.csv"]["sha256"]:
        sys.exit("deals.csv does not match its manifest")
    if _sha(os.path.join(rd, "bars.csv")) != rm["sha256"]:
        sys.exit("bars.csv does not match its manifest")
    deals = pd.read_csv(os.path.join(dd, "deals.csv")).sort_values(["time_msc", "ticket"]).reset_index(drop=True)
    bars = pd.read_csv(os.path.join(rd, "bars.csv"))
    first = pd.Timestamp(rm["since_utc"]).date()
    last_full = (pd.Timestamp(rm["pulled_utc"]) - pd.Timedelta(days=1)).date()
    problems = check_trading_days(bars.time.values, first, last_full)
    if problems:
        sys.exit("bars incomplete against the trading calendar: " + "; ".join(problems))
    cash = (deals.profit + deals.commission + deals.swap + deals.fee).sum()
    if abs(cash - dm["balance"]) > 0.05:
        sys.exit(f"deals sum {cash:.2f} != balance {dm['balance']:.2f}")
    return deals, bars


def max_drawdown(r, trough, runup_before=None, runup=None):
    """Max drawdown of compounded equity measured from the highest equity seen,
    including floating values inside baskets. Per basket, as fractions of
    equity at its start: r = return at close, trough = worst floating return,
    runup_before = best floating return before the trough (a peak the trough
    is measured against), runup = best floating return in the whole basket
    (a peak for later baskets). Without run-ups only closed peaks are used."""
    import numpy as np
    r = np.asarray(r, float); n = len(r)
    trough = np.minimum(np.asarray(trough, float), r)
    rb = np.zeros(n) if runup_before is None else np.maximum(np.asarray(runup_before, float), 0)
    ru = np.zeros(n) if runup is None else np.maximum(np.asarray(runup, float), np.maximum(r, 0))
    eq = np.cumprod(1 + r)
    peak, start, worst = 1.0, 1.0, 0.0
    for i in range(n):
        p_in = max(peak, start * (1 + rb[i]))
        worst = min(worst, start * (1 + trough[i]) / p_in - 1, eq[i] / max(p_in, eq[i]) - 1)
        peak = max(peak, start * (1 + ru[i]), eq[i])
        start = eq[i]
    return eq, worst * 100


def peak_before_cut(lows, cid, level_pct):
    """Floating peak (in % of basket start) seen before the basket first
    reached level_pct (negative). lows[cid] = rows of (record low, peak so far)."""
    a = lows.get(str(cid))
    if a is None:
        return 0.0
    hit = np.where(a[:, 0] <= level_pct)[0]
    return float(a[hit[0], 1]) if len(hit) else float(a[-1, 1])


def forward_coverage():
    """Do the pinned snapshots cover the whole forward window? Both pulls must be
    made after its last day, and no magic position opened inside it may still be open."""
    dd = os.path.join(RAW, DEALS_SNAPSHOT); rd = os.path.join(RAW, RATES_SNAPSHOT)
    end = pd.Timestamp(FORWARD_END, tz="UTC")
    pulled = [pd.Timestamp(json.load(open(os.path.join(d, "manifest.json"), encoding="utf-8"))["pulled_utc"])
              for d in (dd, rd)]
    deals = pd.read_csv(os.path.join(dd, "deals.csv"))
    m = deals[deals.magic == MAGIC]
    opened = set(m[(m.entry == 0) & (m.time < end.timestamp())].position_id)
    closed = set(deals[deals.entry.isin((1, 3))].position_id)
    still_open = len(opened - closed)
    return all(t >= end for t in pulled) and still_open == 0, still_open
