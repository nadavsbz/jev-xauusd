"""Read-only export of the C1+I2 demo deals (attach to the running demo terminal, no login change, no orders).
Usage: py -3.12 research/stable/demo_export.py YYYYMMDD"""
import sys, pandas as pd, MetaTrader5 as mt5
from datetime import datetime
TERM = r"C:\MT5_JEV_DEMO\terminal64.exe"
if not mt5.initialize(path=TERM):                 # attaches to the running terminal as-is
    sys.exit(f"attach failed: {mt5.last_error()}")
try:
    acc = mt5.account_info()
    if acc is None or acc.trade_mode != 0:        # 0 = demo; refuse anything else
        sys.exit("refusing: the attached account is not a demo account")
    d = mt5.history_deals_get(datetime(2026, 11, 1), datetime(2030, 1, 1))
    D = pd.DataFrame(list(d), columns=d[0]._asdict().keys())
    D["t"] = pd.to_datetime(D.time, unit="s")
    keep = ["ticket", "order", "time", "time_msc", "type", "entry", "magic", "position_id", "reason", "volume", "price",
            "commission", "swap", "profit", "fee", "symbol", "t"]
    out = f"data/derived/demo_c1i2/deals_{sys.argv[1]}.csv"; D[keep].to_csv(out, index=False)
    pos = mt5.positions_get() or ()
    print(f"deals {len(D)} -> {out}; balance {acc.balance:.2f} equity {acc.equity:.2f}; open positions {len(pos)}")
    # C1 mark-to-market snapshot for research/stable/alert_monitor.py (PROTOCOL v1): realised C1 P&L + open C1 floating
    c1 = D[D.magic == 61001]; real = float((c1.profit + c1.swap + c1.commission + c1.fee).sum())
    flt = float(sum(p.profit + p.swap for p in pos if p.magic == 61001))
    srv = pd.Timestamp(mt5.symbol_info_tick("BTCUSD").time, unit="s")
    with open("data/derived/demo_c1i2/c1_snapshots_raw.csv", "a") as f:
        f.write(f"{srv:%Y-%m-%d %H:%M:%S},{real + flt:.2f}\n")
    print(f"C1 mtm pnl {real + flt:+.2f} at server {srv}")
    for p in pos: print(f"   open {p.symbol} {'buy' if p.type == 0 else 'sell'} {p.volume} profit {p.profit:.2f} magic {p.magic}")
finally:
    mt5.shutdown()
