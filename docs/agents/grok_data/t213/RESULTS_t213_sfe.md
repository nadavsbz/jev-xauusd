# RESULTS t213 — SFE Impulse ICM decode gate

Written: 2026-11-12 09:33 Asia/Jerusalem (IST, UTC+2).

**Decode-gate verdict: FAIL** (both symbols; the deployable BTC gate fails).

- **BTCUSD:** timing **p = 0.085** (169 of 2,000 weekday permutations ≥ the real mean) — does **not** beat p < 0.05. Concentration **survives** dropping BTC’s own 10 best close-days (€166.27 remains, PF 1.075). Gate requires both: **FAIL**.
- **ETHUSD:** timing **p = 0.926**, excess **−11.57 bp** vs random (worse than a same-side random weekday entry). After dropping ETH’s 10 best close-days, profit is **−€434.59**, PF 0.861 — concentration **fails**. ETH also **fails the 2 bp/side cash cap** (3.20 bp/side). Gate **FAIL**.
- Combined (BTC+ETH) concentration would survive (€388.02, PF 1.073) and is a diagnostic only; it cannot declare a pass.

**No entry-rule inference was run.** The PREREG allows inference only if BTC passes. No MQL5. The four closed t207 textbook specs were not retested.

No accounts, terminals, testers, or `accounts.json` were touched. Unique t213 names; t199c–t212 were not overwritten.

---

## 0. Method and hashes

PREREG `PREREG_20261112_0930_t213_sfe.md` was written and hashed **before** any mid-price, random-path, or inferred-rule P&L. Recorded EUR was profiled first (given data).

| File | SHA-256 |
|---|---|
| `PREREG_20261112_0930_t213_sfe.md` | `51ed0d5fa582b662eddb457dc0dbae5a638450e6b7b71d26667a2de1b8242688` |
| `code/backtest_t213_sfe.py` | `cc5c217cad7c9d178111e99a64659ad0809c4be3c85db7271241f5299a3264e0` |
| `results_t213_sfe/summary.json` | `2c5cfe1a16e841c5db26463ebf49b7939aa0b599ae402068c34c54ab8561c821` |

Pass rule (frozen, per symbol): timing one-sided p < 0.05 on equal-weight mean net bp, **and** remaining recorded EUR profit > 0 with PF ≥ 1.0 after dropping that symbol’s 10 best close-days. Inference only if **BTC** passes. ETH is never deployable (cost cap).

Costs (t207, **VERIFIED**): BTC **1.42 bp/side** (2.84 bp RT), ETH **3.20 bp/side** (6.40 bp RT, **FAIL 2 bp cap**). Swap **−4.75%/yr both sides** ≈ **1.30 bp** per 21:00 UTC in [entry, exit), weekend nights included, **no Friday triple** (schedule **ASSUMED**, annual rate VERIFIED). Broker stamps ≈ NY+7 (**ASSUMED**, as the brief).

Official real bp: TSV fills minus those RF costs. Random paths: Binance spot H1 close (`BTCUSDT_1h.csv` / `ETHUSDT_1h.csv`, 2017-08-17 04:00–2026-11-09 23:00 UTC; last-trade as mid). **No M15/M1 crypto file is on the box**; H1 is the best available (intra-hour fills vs hourly random is a stated limit). Official entry pool = H1 bars in the same ISO week (broker), **Monday–Friday only** (the book has zero weekend entries). N = 2,000. Seeds 213213 (BTC timing), 213214 (ETH timing), 213215/213216 (side). p = (1 + #{perm ≥ real}) / (N+1). Coverage: **0 trades excluded** (all 439+541 sit inside the H1 range).

---

## 1. Profile (recorded EUR, 980 closed trades)

Source: `/home/box/Downloads/sfe_hist_all.tsv` and `sfe_info.txt` (Myfxbook 10842035, atractor, IC Markets MT5, EUR). 980 trades + 8 withdrawals (−€1,150) + 1 deposit (€1,000). Figures match the vendor page on profit, peak, PF, YTD, and trade counts (**OBSERVED**).

- Opens 2023-08-31 23:00 → 2026-11-09 02:48 broker; deposit 2023-08-22. **ETHUSD 541**, **BTCUSD 439**.
- Profit **€1,962.94** (BTC **€1,182.56**, ETH **€780.38**), final balance **€1,812.94**, peak **€2,493.36** at 2025-11-04 23:34 (matches “Nov 04”). Abs. gain 196.29% = profit/deposit. Vendor equity DD **27.97%**; a close-to-close balance path after that peak goes a little deeper (about −30%). Interest −€139.91, commissions €0 (their ICM book).
- WR **57.86%** (567 / 413 / 0 flats). PF **1.366**. Long 537, WR 59.0%, €1,158.42; short 443, WR 56.4%, €804.52. Vendor longs 317/537 (59%), shorts 250/443 (56%), Sharpe 0.18, Z-score −16.35 (99.99%) — match.
- Average duration **339.9 min** (exactly the claimed 5h 40m). Median 314.5 min. BTC mean 329 / median 300; ETH 349 / 333. Almost all under 1 day (2 ETH trades >1d). Profit sits in the 1–6h buckets (€1,048 + €1,405); **6–12h is −€478** (WR 48%) and 12–24h **−€298** (WR 10%).
- **No Saturday or Sunday entries.** 65 trades’ calendar span includes a weekend (they can hold through it). Mondays dominate: **316** of 980 opens (32%), €546. Entry-hour peaks at broker 18–20 (79, 98, 76 trades). Profit: hour 18 **€376**, 11 **€333**, 8 **€237**; weak: 03 −€122, 22 −€113, 07 −€70.

### Monthly returns (close-profit / start-of-month balance, withdrawals not in the numerator)

38 months with trades (2023-09–2026-11), geometric **≈ 3.24%/mo** (claimed 3.30%). 2024 was the engine: Feb +40.8%, Apr +26.6%, Jul +22.5%; June 2024 −15.8%. **2026 YTD −13.20%** exactly (−€275.82 on 240 trades, start-of-year balance €2,088.76). 2026 geometric ≈ −1.3%/mo; cumulative −13.2%.

**Recent decay is ETH, not BTC:**

| Year | BTC n | BTC € | BTC PF | ETH n | ETH € | ETH PF |
|---|---:|---:|---:|---:|---:|---:|
| 2023 | 43 | +47.82 | 1.35 | 34 | −54.04 | 0.65 |
| 2024 | 174 | **+763.12** | 2.02 | 161 | **+776.72** | 2.00 |
| 2025 | 120 | +53.68 | 1.06 | 208 | +651.46 | 1.59 |
| 2026 | 102 | **+317.94** | 1.61 | 138 | **−593.76** | 0.46 |

BTC is still profitable in 2026. ETH has given back more than its 2025 gain.

### Lot sizing and averaging

- BTC lots only **0.01–0.05**, mean 0.019, corr(lots, bal_at_open) = **−0.28** (not growing with the account). After a BTC loss, the next BTC open is bigger 62 / same 80 / smaller 35 — mixed, not a clean martingale, but not a pure step-with-balance rule either.
- ETH lots **0.09–0.81** (68 distinct), corr with balance ≈ 0. After an ETH loss, next ETH open is **bigger 147 / same 3 / smaller 84** — more often increases after a loss (recovery-sizing / soft martingale), not a strict double.
- Same-minute same-side clusters are modest: BTC 27 events (58 trades, max 4); ETH 32 (66, max 3). **Averaging-in is strong:** 238/439 BTC (54%) and 320/541 ETH (59%) entered while a same-side trade was already open; max concurrent same-side 6. Same-close baskets: BTC 44 / ETH 71. Z-score −16.35 is consistent with dependence. This is stacking, not EdgeTrader-style 7-leg same-minute baskets.

### Concentration

- **Top-10 trades:** €336.72, 17.2% of profit. Best: 2025-10-11 BTC Sell 0.01, **€53.36** (matches “Oct 11”); worst: 2024-06-15 ETH Sell 0.51, **−€51.88** (matches “Jun 15”).
- **Top-10 close-days (combined):** €1,574.92, **80.23%** of all profit (2025-09-22 €217.71, 2025-10-10 €193.25, 2024-07-05 €189.69, 2026-09-21 €168.34, …). 143 up / 141 down / 284 days. After dropping them: **€388.02**, 884 trades, WR 53.7%, **PF 1.073** — survives the frozen bar, thinly.
- **BTC own top-10 days:** €1,016.29, **85.9%** of BTC profit. After: **€166.27**, PF **1.075**, 388 trades — **survives**.
- **ETH own top-10 days:** €1,214.97, **155.7%** of ETH profit (the ten best days exceed total ETH profit). After: **−€434.59**, PF **0.861** — **fails**. ETH’s recorded edge is the ten best days.

---

## 2. Random-timing test

All 980 gold-path trades are in H1 coverage. Pools: 439 BTC and 541 ETH, none dropped.

| Test | Symbol | n | Real mean bp | Perm mean | Excess | p | Percentile |
|---|---|---:|---:|---:|---:|---:|---:|
| **Official timing** (fills+RF vs same-side same-week **weekdays**) | **BTC** | 439 | **24.280** | 15.163 | **+9.117** | **0.0850** | 91.55th (169/2000 ≥ real; sd 6.64, q95 25.96, max 40.65) |
| Official timing | **ETH** | 541 | **10.883** | 22.450 | **−11.567** | **0.9260** | 7.40th (1,852/2000 ≥ real; sd 8.10) |
| Sensitivity, 24/7 pool (not official) | BTC | 439 | 24.280 | 9.018 | +15.262 | 0.0045 | 99.6th |
| Sensitivity, 24/7 | ETH | 541 | 10.883 | 14.200 | −3.317 | 0.670 | 33.1th |
| Cluster robustness | BTC | 286 groups | 24.280 | 15.243 | +9.037 | 0.170 | 83.1th |
| Cluster robustness | ETH | 349 groups | 10.883 | 21.704 | −10.821 | 0.846 | 15.5th |
| **Random-side** (H1 mid at **real** times, fair coin) | **BTC** | 439 | **21.426** | −3.359 | **+24.785** | **0.00050** | 100th |
| Random-side | **ETH** | 541 | **15.493** | −6.591 | **+22.084** | **0.0085** | 99.2th |

Official timing **fails** for both. The 24/7 BTC sensitivity would have p = 0.0045, because adding weekend bars **lowers** the random mean (9.02 vs 15.16) — weekends were a worse backdrop for their side mix. That cannot change the official definition: they never enter on weekends, so the fair same-week alternative is a **weekday** hour, and on that test p = 0.085. Cluster robustness agrees with the fail (BTC p = 0.17, ETH p = 0.85).

**Direction at the actual timestamps is skilled** (random-side p = 0.00050 BTC, 0.0085 ETH). A coin-flip side at those times loses the RF cash (perm means −3.4 and −6.6 bp). Their sides at those times do not: mid+RF +21.4 bp BTC, +15.5 bp ETH. What **fails** is the claim that the **clock** is skilled: for BTC, same side at a random weekday in the same week is only 9 bp worse, inside the 5% cutoff given the 6.6 bp permutation sd; for ETH, a random weekday with the same side would have been **better** by 11.6 bp.

Fills vs Binance mid: BTC fills **+2.85 bp** better than mid (corr exists, both positive). ETH fills **−4.61 bp** worse than mid (ICM fill vs Binance last-trade, plus a coarser hour). ETH mid mean 15.49 still sits below the ETH random-timing perm mean of 22.45, so the “worse than random time” result is not just a fill artifact.

Random same-side paths themselves are strongly positive (BTC +15 bp, ETH +22 bp after RF costs) — 2023–2026 crypto drift plus their long bias (537/443) is a large backdrop.

---

## 3. Verdict

**FAIL.** BTC does not beat same-week weekday random entry at p < 0.05 (p = 0.085), even though its recorded edge survives the top-10-day drop. ETH fails both the timing test (and is worse than random) and the top-10-day drop, and cannot be deployed on RoboForex (3.20 bp/side > 2 bp cap).

This is a skill test of the vendor book, **not** a retest of t207. t207 already showed that textbook H1 impulse / Donchian / vol-expansion readings of SFE’s *live-stat shape* lose RF costs on 2018–2026. The actual 2023-08–2026-11 book, now in hand, does **not** clear the same decode gate EdgeTrader (t212) passed. Do not infer a rule, do not retune, do not write MQL5, do not flip the official weekday pool to 24/7 after seeing p.

What the book *does* show, and is not a pass: real **direction** skill at the times they traded; a 2024-dominated equity curve with **80% of combined profit in 10 days**; 2026 decay concentrated in ETH (−€594) while BTC stayed positive (+€318); averaging-in on both names; ETH lots that often increase after a loss.

---

## 4. Files

- `PREREG_20261112_0930_t213_sfe.md`
- `code/backtest_t213_sfe.py`
- `results_t213_sfe/` — `summary.json`, `real_trade_bp_{BTCUSD,ETHUSD}.csv`, perm arrays
- This file: `RESULTS_t213_sfe.md`
