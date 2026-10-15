"""The exact snapshots the report was computed from. Explicit folders, no
"first glob match": each file is checked against the sha256 in its
manifest, and the deals must sum to the balance recorded at pull time."""
import hashlib, json, os, sys
import pandas as pd

RAW = "data/raw/black_dragon_1"
DEALS_SNAPSHOT = "20261015T120553Z"
RATES_SNAPSHOT = "rates_XAUUSDc_M1_20261015T144411Z"
START = pd.Timestamp("2025-11-11").timestamp()   # first deal of magic 5555
MAGIC = 5555


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
    cash = (deals.profit + deals.commission + deals.swap + deals.fee).sum()
    if abs(cash - dm["balance"]) > 0.05:
        sys.exit(f"deals sum {cash:.2f} != balance {dm['balance']:.2f}")
    return deals, bars
