"""Fleet status from the read-only deal snapshots (latest per account under data/raw/<name>/).
Per account, in USD (cent accounts / 100): balance now, net deposits, trading profit per day (last 30/90 days and
since start), monthly returns on the balance, worst month, symbols and magics traded, lot ratio (balance per first lot).
No account number or comment text is printed or written. Output: docs/evidence/fleet_status.json"""
import glob, json, os
import numpy as np, pandas as pd

NAMES = ["black_dragon_1", "black_dragon_2", "black_dragon_3", "black_dragon_5", "black_dragon_6", "black_dragon_8",
         "btc_bot", "btc_bot_4"]


def latest(name):
    snaps = sorted(d for d in glob.glob(f"data/raw/{name}/*/") if "rates" not in d and os.path.exists(d + "deals.csv"))
    if snaps:
        return snaps[-1] + "deals.csv"
    p = f"data/raw/{name}/deals.csv"
    return p if os.path.exists(p) else None


def one(name):
    p = latest(name)
    d = pd.read_csv(p).sort_values("time_msc")
    cents = d.symbol.dropna().astype(str).str.endswith("c").any()
    k = 100.0                       # all 8 are cent accounts (USC), also those whose symbol has no "c" suffix (manual_report, VERIFIED by balance)
    d["v"] = (d.profit + d.commission + d.swap + d.fee) / k
    d["day"] = pd.to_datetime(d.time, unit="s").dt.normalize()
    bal_ops = d[d.type == 2]; tr = d[d.type.isin([0, 1])]
    end = d.day.max(); bal = d.v.sum()
    daily = tr.groupby("day").v.sum()
    out = dict(snapshot=os.path.basename(os.path.dirname(p)) or "flat", cents=bool(cents), start=str(d.day.min().date()),
               end=str(end.date()), balance_usd=round(bal, 2), net_deposits_usd=round(bal_ops.v.sum(), 2),
               trading_profit_usd=round(tr.v.sum(), 2),
               symbols=sorted(tr.symbol.dropna().unique().tolist()), magics=sorted(int(m) for m in tr.magic.unique() if m))
    for n in (30, 90):
        out[f"usd_per_day_{n}d"] = round(tr[tr.day > end - pd.Timedelta(days=n)].v.sum() / n, 2)
    # monthly return on the balance at the start of the month (balance ops excluded from the return)
    d["bal"] = d.v.cumsum(); d["m"] = d.day.dt.to_period("M")
    rows = []
    for m, g in d.groupby("m"):
        b0 = g.bal.iloc[0] - g.v.iloc[0]; pnl = g[g.type.isin([0, 1])].v.sum()
        rows.append((str(m), round(b0, 2), round(pnl, 2), round(pnl / b0 * 100, 1) if b0 > 0 else None))
    out["months"] = rows
    ins = tr[tr.entry == 0]
    if len(ins):
        first = ins.groupby("position_id").volume.first()
        out["median_first_lot"] = float(first.tail(500).median())
    return out


res = {}
for n in NAMES:
    try:
        res[n] = one(n)
    except Exception as e:                       # noqa: BLE001
        res[n] = {"error": type(e).__name__}
    r = res[n]
    print(n, {k: r.get(k) for k in ("start", "end", "balance_usd", "net_deposits_usd", "trading_profit_usd",
                                    "usd_per_day_30d", "usd_per_day_90d", "symbols", "magics", "median_first_lot")})
    for m in r.get("months", [])[-8:]:
        print("   ", m)
json.dump(res, open("docs/evidence/fleet_status.json", "w"), indent=1)
