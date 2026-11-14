"""C1 'time machine' (user 30.10.2026: "can C1 run on the time machine?", after installing the day-trader-skill pack).
The pack's trader-timemachine replays ONE intraday stock trade 10,000 times from the stock's own 5-minute bars (bootstrap by
time of day). C1 holds positions for weeks with no stop or target, so the same idea is applied at C1's own scale, twice:
  A  equity replays: 10,000 synthetic 1-year and 5-year runs drawn from C1's MTM daily returns in the MT5 tester
     (c1r3_av10_d0, RF 2020-2025.10.24 + holdout to 30.10.2026; tester_sharpe.py with SAVE=data/derived/c1_equity), in blocks
     of BLOCK days (stationary bootstrap, Politis-Romano 1994) so streaks and drawdowns stay together.
     Answers: odds of a losing year, the spread of a year's result, how deep and how often drawdowns go.
  B  price replays: synthetic BTC+ETH H6 price paths built from the joint H6 returns 2018-2025.10.24 (same rows for both coins,
     so their correlation stays), stationary bootstrap with mean block MB bars; C1 (intraday_trend.py weights, costs, LAG) runs
     on each path. MB=1 shuffles bars one by one: trends are destroyed, so C1 should earn nothing there (a control: the edge
     must come from trend persistence, not from the drift or the cost model).
Both draw only from the seen past (2018-2026): a replay is not a forecast and does not test a regime the past never had.
Seed 19 (as the pack). Usage: python research/stable/c1_timemachine.py [A|B] [N]"""
import os, sys
import numpy as np, pandas as pd

MODE = sys.argv[1] if len(sys.argv) > 1 else "A"
N = int(sys.argv[2]) if len(sys.argv) > 2 else (10000 if MODE == "A" else 1000)
rng = np.random.default_rng(19)

def boot_idx(n_src, n_out, mean_block):
    """stationary bootstrap row indices: blocks of geometric length (mean mean_block), wrapping around the end"""
    idx = np.empty(n_out, dtype=np.int64); i = 0
    while i < n_out:
        start = rng.integers(n_src); L = min(rng.geometric(1 / mean_block), n_out - i)
        idx[i:i + L] = (start + np.arange(L)) % n_src; i += L
    return idx

def pct(a, q): return np.percentile(a, q)

if MODE == "A":
    D = "data/derived/c1_equity"; BLOCK = int(os.environ.get("BLOCK", "20"))
    for av in ("av10", "av08"):
        # two separate runs (the holdout restarts at 120,000): daily returns within each run, then joined
        r = np.concatenate([pd.read_csv(f"{D}/c1r3_{av}_d0_rf_{p}_equity.csv", index_col=0).equity.pct_change().dropna().values
                            for p in ("2020_2025", "holdout")])
        print(f"\n{av}: {len(r)} daily returns, {N:,} replays, blocks of ~{BLOCK} days, seed 19")
        for yrs in (1, 5):
            n = 365 * yrs; out = np.empty(N); mdd = np.empty(N); worst = np.empty(N)
            for k in range(N):
                x = r[boot_idx(len(r), n, BLOCK)]; e = np.cumprod(1 + x)
                out[k] = e[-1] ** (1 / yrs) - 1; mdd[k] = (e / np.maximum.accumulate(e) - 1).min()
                worst[k] = min(np.prod(1 + x[j:j + 365]) - 1 for j in range(0, n, 365))
            print(f"  {yrs}y  yearly: median {pct(out, 50)*100:+.1f}%, 5-95% {pct(out, 5)*100:+.1f}% .. {pct(out, 95)*100:+.1f}%,"
                  f" below 0: {(out < 0).mean()*100:.1f}% | MDD median {pct(mdd, 50)*100:.1f}%, 95th {pct(mdd, 5)*100:.1f}%,"
                  f" deeper than 25%: {(mdd < -.25).mean()*100:.1f}%, than 35%: {(mdd < -.35).mean()*100:.1f}%"
                  + (f" | at least one losing year: {(worst < 0).mean()*100:.1f}%, worst year median {pct(worst, 50)*100:+.1f}%" if yrs > 1 else ""))
else:
    os.environ["CRY"] = "BTCUSD,ETHUSD"; sys.argv = [sys.argv[0]]
    sys.path.insert(0, "research/stable"); import intraday_trend as T
    cols = ["BTCUSD", "ETHUSD"]
    src = T.C[cols].loc["2018":"2025-10-24"].dropna(); Rsrc = src.pct_change().dropna().values
    tc = np.array([T.TC[s] for s in cols]); fl = np.array([T.fin(s, 1) for s in cols]); fs = np.array([T.fin(s, -1) for s in cols])

    def c1(C):
        """C1 net bar returns on a price frame C (same steps as intraday_trend.weights/net, 0.5 long-only + 0.5 long-short)"""
        R = C.pct_change(); vol = R.rolling(60, min_periods=40).std() * np.sqrt(T.PER_YEAR); F = 0
        for lo in (True, False):
            W = pd.DataFrame({s: T.donch(C[s], lo) * (0.10 / vol[s]).clip(upper=3) / 2 for s in cols}).fillna(0)
            r0 = (W.shift(T.LAG) * R).sum(axis=1); v = r0.rolling(int(T.PER_YEAR / 4), min_periods=60).std() * np.sqrt(T.PER_YEAR)
            F = F + 0.5 * W.mul((T.TARGET / v).clip(upper=3).fillna(0), axis=0)
        h = F.shift(T.LAG).fillna(0).values; Rv = R.fillna(0).values
        return (h * Rv).sum(1) - (np.abs(np.diff(h, axis=0, prepend=0)) * tc).sum(1) - (np.clip(h, 0, None) * fl + np.clip(-h, 0, None) * fs).sum(1) / T.PER_YEAR

    def stats(x, warm):
        x = x[warm:]; e = np.cumprod(1 + x); yrs = len(x) / T.PER_YEAR; Y = int(T.PER_YEAR)
        yr = [np.prod(1 + x[j:j + Y]) - 1 for j in range(0, len(x) - Y + 1, Y)]
        return e[-1] ** (1 / yrs) - 1, (e / np.maximum.accumulate(e) - 1).min(), x.mean() / x.std() * np.sqrt(T.PER_YEAR), np.mean(np.array(yr) < 0)

    warm = 320   # C1's MinBars: the first bars of a path have no full channels / vol yet
    real = stats(c1(src), warm)
    print(f"real 2018-2025 (sanity): CAGR {real[0]*100:.1f}% MDD {real[1]*100:.1f}% Sharpe {real[2]:.2f} losing years {real[3]*100:.0f}%")
    for MB in [int(m) for m in os.environ.get("MB", "120,480,1").split(",")]:
        res = []
        for k in range(N):
            x = Rsrc[boot_idx(len(Rsrc), len(Rsrc), MB)]
            P = pd.DataFrame(np.cumprod(1 + x, axis=0) * src.iloc[0].values, columns=cols)
            res.append(stats(c1(P), warm))
        a = np.array(res)
        print(f"MB {MB:4d} bars (~{MB*6/24:.0f} days), {N} paths, seed 19: CAGR median {pct(a[:,0],50)*100:+.1f}% (5-95% {pct(a[:,0],5)*100:+.1f}..{pct(a[:,0],95)*100:+.1f}),"
              f" CAGR>0 {np.mean(a[:,0] > 0)*100:.0f}% | Sharpe median {pct(a[:,2],50):.2f} (5% {pct(a[:,2],5):.2f}) | MDD median {pct(a[:,1],50)*100:.1f}%,"
              f" 95th {pct(a[:,1],5)*100:.1f}% | losing-year share median {pct(a[:,3],50)*100:.0f}%", flush=True)
