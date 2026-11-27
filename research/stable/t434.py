"""t434 (docs/prereg/research_t434.md): Binance BTCUSDT 1m OFI z-score (same minute-of-hour, previous 30 full days) -> 5-min trade.
Entry open t+1 (decay check: t+2), exit open 5 minutes after entry, no stacking. Gate A 2019-2022 (t431 items 1-9).
Data: data.binance.vision monthly 1m klines (public, no key). Usage: py -3.12 research/stable/t434.py"""
import os, io, json, zipfile, urllib.request
import numpy as np, pandas as pd

RAW = "data/raw/t434"; os.makedirs(RAW, exist_ok=True)
COLS = ["ot", "o", "h", "l", "c", "v", "ct", "qv", "n", "tbv", "tbq", "ig"]


def month(y, m):
    f = f"{RAW}/BTCUSDT-1m-{y}-{m:02d}.zip"
    if not os.path.exists(f):
        b = urllib.request.urlopen(urllib.request.Request(f"https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1m/BTCUSDT-1m-{y}-{m:02d}.zip",
                                                           headers={"User-Agent": "research-client"}), timeout=300).read()
        open(f, "wb").write(b)
    z = zipfile.ZipFile(f); d = pd.read_csv(z.open(z.namelist()[0]), header=None, names=COLS, usecols=["ot", "o", "qv", "tbq"])
    return d


def trades(D, lag):
    sig = D.sig.values; o = D.o.values; t = D.index; out = []; i = 0; n = len(D)
    while i < n - lag - 5:
        s = sig[i]
        if s != 0:
            e = i + lag; x = e + 5
            if t[x] - t[e] == pd.Timedelta(minutes=5) and t[e] - t[i] == pd.Timedelta(minutes=lag):
                out.append((t[e], s, s * (o[x] / o[e] - 1) * 1e4)); i = x - lag   # next signal can be read at the exit minute's bar close
                continue
        i += 1
    return pd.DataFrame(out, columns=["t", "side", "gross_bp"])


if __name__ == "__main__":
    D = pd.concat([month(y, m) for y in range(2018, 2023) for m in range(1, 13) if (y, m) >= (2018, 12)])
    D["t"] = pd.to_datetime(D.ot, unit="ms"); D = D.drop_duplicates("t").set_index("t").sort_index()
    D["ofi"] = np.where(D.qv > 0, 2 * D.tbq / D.qv - 1, np.nan)
    D["day"] = D.index.normalize(); D["mh"] = D.index.minute
    g = D.groupby(["day", "mh"]).ofi.agg(s="sum", s2=lambda x: (x ** 2).sum(), k="count").reset_index()
    stats = []
    for mh, G in g.groupby("mh"):
        G = G.set_index("day").asfreq("D").fillna({"s": 0, "s2": 0, "k": 0})   # calendar days; missing days contribute nothing
        R = G[["s", "s2", "k"]].rolling(30, min_periods=30).sum().shift(1)          # 30 previous full days, current excluded
        R["mh"] = mh; stats.append(R)
    S = pd.concat(stats).reset_index().rename(columns={"index": "day"})
    S["mu"] = S.s / S.k; S["sd"] = np.sqrt(np.maximum(S.s2 / S.k - S.mu ** 2, 0) * S.k / (S.k - 1))
    D = D.reset_index().merge(S[["day", "mh", "mu", "sd"]], on=["day", "mh"], how="left").set_index("t")
    D["z"] = (D.ofi - D.mu) / D.sd
    D["sig"] = np.where(D.z >= 2, 1, np.where(D.z <= -2, -1, 0))
    A = D["2019":"2022"]
    expected = int((pd.Timestamp("2023-01-01") - pd.Timestamp("2019-01-01")).total_seconds() // 60)
    cov = len(A) / expected
    T1, T2 = trades(D, 1), trades(D, 2)
    T1 = T1[(T1.t >= "2019-01-01") & (T1.t < "2023-01-01")].copy(); T2 = T2[(T2.t >= "2019-01-01") & (T2.t < "2023-01-01")]
    T1["year"] = T1.t.dt.year; T1["net"] = T1.gross_bp - 7; T1["str"] = T1.gross_bp - 15
    day = T1.groupby(T1.t.dt.normalize()).net.sum(); tday = day.mean() / (day.std(ddof=1) / np.sqrt(len(day)))
    yr = T1.groupby("year").net.sum() / 100                                             # % of equity, 1x per trade, summed
    sn = T1.groupby("side").net.sum(); ss = T1.side.value_counts(normalize=True); tot = T1.gross_bp.sum(); top10 = T1.gross_bp.nlargest(10).sum()
    gate = {"1_coverage>=99.9%": cov >= 0.999, "2_n>=1000_150/yr": len(T1) >= 1000 and T1.groupby("year").size().min() >= 150,
            "3_gross>=14bp": T1.gross_bp.mean() >= 14, "4_net>0_tday>=2": T1.net.mean() > 0 and tday >= 2,
            "5_years>=3/4_none<-5%": (yr > 0).sum() >= 3 and yr.min() > -5, "6_both_sides": bool(len(sn) == 2 and (sn > 0).all() and ss.min() >= 0.3),
            "7_top10<=25%": tot > 0 and top10 / tot <= 0.25, "8_stress>0": T1.str.sum() > 0, "9_decay_t+2>=7bp": T2.gross_bp.mean() >= 7}
    out = dict(coverage=round(cov, 5), n=len(T1), n_by_year={int(k): int(v) for k, v in T1.groupby("year").size().items()},
               gross_mean_bp=round(T1.gross_bp.mean(), 2), net_mean_bp=round(T1.net.mean(), 2), t_day=round(tday, 2),
               net_by_year_pct={int(k): round(v, 1) for k, v in yr.items()}, side_net_bp={int(k): round(v, 0) for k, v in sn.items()},
               side_share={int(k): round(v, 3) for k, v in ss.items()}, top10_share=round(top10 / tot, 3) if tot > 0 else None,
               gross_mean_t2_bp=round(T2.gross_bp.mean(), 2), gate={k: bool(v) for k, v in gate.items()}, PASS_A=bool(all(gate.values())))
    json.dump(out, open("docs/evidence/t434.json", "w"), indent=1); print(json.dumps(out, indent=1))
