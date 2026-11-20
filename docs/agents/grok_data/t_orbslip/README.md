# t_orbslip — ORB exit-mechanism slippage in R (2018–2025)

Independent cross-check requested by Claude on 17.11.2026 20:05. This is **not** a test of the Concretum “stocks in play” strategy: there is no relative-volume / “in play” filter. The only question is how many R the exit mechanism (10% ATR14 stop, 16:00 exit) loses once realistic per-share slippage is added, on large liquid names.

Rules were frozen in `PREREG.md` before the run (sha256 in `PREREG.md.sha256`).

## Data [VERIFIED]
- Public Dukascopy 1-minute bid and ask for 30 US stock CFDs, 2018-01-01 through 2025-12-31, downloaded with `dukascopy-node` 1.51.1, no account.
- Universe (CFD id → ticker): AAPL, MSFT, AMZN, GOOGL, META (fbususd), NVDA, TSLA, NFLX, INTC, CSCO, JPM, BAC, C, WFC, GS, XOM, CVX, JNJ, PFE, KO, PG, DIS, HD, V, T, BA, AMD, MU, CAT, AAL.
- 480 files, ~6.2 GB raw, kept on the box under `/workspace/tmp_orb/raw/` (not copied to Benzaquen). See `RAW_MANIFEST.csv`.
- These are **CFD quotes**, not SIP equity prints. Spreads are Dukascopy’s, typically wider than the cash tape, so the “cross the spread” sensitivity is a conservative (worse-fill) bound, not a cash-market estimate.
- The Hugging Face `mito0o852/OHLCV-1m` dump mentioned in the t_concretum / broker survey was **not** used (licence unclear).

## Mechanism (see PREREG.md)
5-minute ORB (09:30–09:34), entry at 09:35 mid open, stop = 0.10 × ATR14 (ATR from prior RTH days only), otherwise exit at the 15:59 mid close. Commission $0.0035/share/side. Slippage $0, $0.01, $0.02 per share per side. Sensitivity B: fill at bid/ask (cross the quoted spread) instead of mid, no extra slippage.

## Outputs
- `RESULTS.md` — overall / by year / by stock / by R$ bucket.
- `trades.csv.gz` — one row per trade, with gross R and net R at each slippage.
- `orbslip.py` — the exact script.

## Headline result
58,873 unfiltered trades, mean gross **+0.050 R**. After commission, mean net R is +0.011 / **−0.100** / **−0.212** at $0 / $0.01 / $0.02 per share per side. The R$ < $0.25 buckets (45% of trades) are cost-killed at 1¢. See `RESULTS.md`. This is not a test of the RelVol “stocks in play” scanner.

## Caveats (short)
Dukascopy CFD quotes, not SIP. Spreads are wider than cash. Prices are not split-adjusted, so the R$ ≥ $1 bucket (pre-split AMZN/GOOGL/NVDA/AAPL/TSLA) understates cost-in-R. The low-R$ result is the one to use.
