# PREREG — C1 exit variants (Grok, round "r82b"), written 17.11.2026 00:06 IST (Asia/Jerusalem, UTC+2)

Written BEFORE any return computation on the data. Disclosure: before writing this I only looked at the first/last
row and row counts of `/workspace/research_new_component/data/cfd_h1/{BTCUSD,ETHUSD}.csv` and
`.../data/binance/{BTC,ETH}USDT_1h.csv` (to know the date ranges). No returns, no signals, no Sharpe computed.

## Base (must be reproduced first)
Exact port of `research/scan/r82_c1_exit.py` mode BASE (branch feat/portfolio, read from git on the box):
- Data: RF H1 history on the box `research_new_component/data/cfd_h1/BTCUSD.csv`, `ETHUSD.csv` (ASSUMED to be the same
  RF MT5 export that `loadh()` reads on Benzaquen; must be verified by Claude). Close resampled to 6h `.last().dropna()`.
- Per n in {10,20,30,60,90,150,250}: enter long at close >= n-bar rolling max close (short at <= n-bar min, LS component
  only), exit on n/2 opposite channel. State = mean of the 7. w = 0.5·state_LongOnly + 0.5·state_LS, shift(2).
- Costs: tc per unit of |Δw| = max(median 2026 relative spread, 1bp) + 0.5bp (scan.tcost for NONSTOCK; the
  `ecn_costs_20261030.csv` table is NOT on the box, so med spread is computed from the file's `spread` column with
  point = 0.01 — ASSUMPTION). Swap −4.75%/yr both sides, both assets (RF BTCUSD card; ETH ASSUMED same), charged per
  calendar time held (dt in years per bar) as in r82.
- Per asset: daily compounded net, `scale()` (90d std, min 60, ×√252, target 10%, cap 5, lagged 1 day); basket = mean
  of the 2 assets, `scale()` again. Metric `st()`: Sharpe ×√365 from first non-zero day, MDD of compounded equity.
- **Reproduction gate:** dev 2017–2022 base Sharpe within 1.52 ± 0.15 (and MDD reported vs −20.1). If it fails, STOP:
  no variant results are reported, only this prereg.

## Variants (entry identical to the base; only the per-n exit changes; re-entry only on a fresh n-bar breakout)
Fixed parameters, no scan. Exactly 3 variants = 3 trials.

- **E1 — volatility chandelier instead of the channel (LeBeau chandelier exit; Wilder ATR).**
  H6 OHLC from H1 (open first, high max, low min, close last). ATR = 22-bar simple mean of true range.
  Long exits when close_i <= (highest close since entry) − 3·ATR_i·sqrt(n/22); short mirror with the lowest close.
  The n/2 channel exit is REMOVED (replaced). Rationale: exit distance tied to volatility from the peak, not to an
  n/2 window low; sqrt(n/22) keeps the stop width proportional to each component's horizon (random-walk scaling).
- **E2 — partial exit at a target, rest on the channel (scale-out).** At entry σ = 60-bar std of H6 returns (as V1).
  When open profit of the component >= 2·σ·sqrt(n), half the component is closed (|q| 1 → 0.5); the rest exits on the
  normal n/2 channel. One partial per trade. Rationale: Nadav's question "isn't the n/2 exit giving back too much" —
  locks part of the move without cutting the tail.
- **E3 — adverse shock exit (regime / crash conditional).** In addition to the n/2 channel: exit the component when the
  single H6 bar return against the position is beyond 3·σ, σ = 60-bar std of H6 returns up to the previous bar
  (lagged, no look-ahead). Rationale: momentum crashes cluster in vol shocks (Daniel & Moskowitz 2016); crypto gap
  crashes. Funding/basis not used: box funding data covers BTC only from 2019, not the 2017–22 dev window.

## Gate (frozen, same as r82)
- dev 2017–2022: PASS iff Sharpe >= base + 0.10 AND MDD >= base MDD (not worse).
- holdout 2023–2026.11 run only for variants that pass dev: PASS iff Sharpe >= base + 0.05 AND MDD >= base MDD − 1pt.
- Secondary, NOT a gate: same variants on Binance BTCUSDT/ETHUSDT 1h (from 2017-08-17, so dev warm-up is shorter) at
  10bp/side taker; reported only as robustness, and only if the RF base reproduces.
- Multiple-testing note: 3 trials (6 cumulative with r82 V1–V3). A marginal pass is suspect.
- Any change to C1's EA is Nadav's decision; this test does not touch any terminal.
