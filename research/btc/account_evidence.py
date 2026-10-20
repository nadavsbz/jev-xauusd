"""Evidence file for the real BTC Bot account (docs/DAY_20261016_SUMMARY.md, section 3):
daily realised P&L per robot (magic of the opening deal), from the investor pull in
data/raw/btc_bot (not in the repo). Writes no login, no transfer comments (they hold other
account numbers), only the sha256 of the raw file and per-day sums.
Usage: python research/btc/account_evidence.py OUT_JSON"""
import hashlib, json, sys
import pandas as pd

RAW = "data/raw/btc_bot/deals.csv"
d = pd.read_csv(RAW)
d["day"] = pd.to_datetime(d.time, unit="s").dt.strftime("%Y-%m-%d")
d["net"] = d.profit + d.commission + d.swap + d.fee
tr = d[d.type != 2]
opening = tr[tr.entry == 0].groupby("position_id").magic.first()
tr = tr.assign(robot=tr.position_id.map(opening).fillna(tr.magic).astype(int))
daily = tr.groupby(["day", "robot"]).net.sum().round(2).reset_index()
bal = d[d.type == 2]
out = {
    "source_sha256": hashlib.sha256(open(RAW, "rb").read()).hexdigest(),
    "deals": int(len(d)), "symbols": sorted(tr.symbol.dropna().unique().tolist()),
    "sum_of_all_deals": round(float(d.net.sum()), 2),
    "balance_operations": [{"day": r.day, "amount": round(float(r.profit), 2)} for r in bal.itertuples()],
    "daily_net_by_robot": daily.to_dict("records"),
    "note": "robot = magic of the position's opening deal; 0 = manual or other",
}
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(out["deals"], out["sum_of_all_deals"], len(out["daily_net_by_robot"]))
