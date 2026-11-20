# RESULTS t208 — XAUUSD short-momentum / impulse family

Written: 2026-11-12 08:35 Asia/Jerusalem (IST, UTC+2).
Round: t208. **Verdict: no deploy. All four pre-registered specs fail g1 (and all but one fail g3 and g4). No MQL5. No retune.** Gold was not a reason to reject; the official BD crash-day gate (g5) applied to every name and **all four passed it**.

This is a new family, analogous in shape to t207 but on XAUUSD, and is **not** a rerun of Gold Reaper / `GR_D96`, goldA, goldfade, short-only gold, or real-yield short. Specs were frozen in the PREREG **before any P&L**.

---

## 1. Cost pre-screen (written first)

File: `COST_PRESCREEN_20261112_0830_t208.md`.

RF XAUUSD Pro (VERIFIED, frozen gold screens / rnext, consistent with the user’s “about 1.64 bp RT plus swap”): cash **$0.12/side** ($0.24 RT = **1.36 bp** at the train mid $1,759.52). The **1.64 bp** figure in earlier screens is that 1.36 bp plus a short-hold expected-swap allowance; the backtest charges **$0.12/side plus actual swap**, so the two are not double-counted. Swap **−$0.60/oz/night long** (~14.2%/yr) and **+$0.19/oz/night short** (credit). Schedule: each 21:00 UTC in `[entry, exit)`, including synthetic weekend 21:00s, no Wednesday triple (annual rate VERIFIED; schedule ASSUMED).

Conservative edge is ASSUMED from the SFE-shaped 16% of 1.5×ATR (train-only median H1 ATR 21.8 bp → 32.7 bp of risk; half of 5.23 bp = **2.62 bp**). 0-night ratio **0.52 MARGINAL**. The user asked for the family, so we proceeded. The backtest uses actual nights, not a blended 1.64.

---

## 2. Data and method

- **Primary:** Dukascopy XAUUSD M15 bid and ask, `/workspace/algotrade/data/xauusd_m15_dukascopy_2015_2026.csv.gz`, mid = (bid+ask)/2, resampled to H1 (69,973 bars, **2015-01-01 23:00 UTC through 2026-10-26 18:00 UTC**). Best H1/M15 source on the box. The packaged H1 file is bid-only and is not official. RF $0.24 is applied around mid.
- Pre-sample **2015–2017** (three years, reported only). Train 2018–2023. Holdout 2024-01-01–**2026-10-26**. All 26 official BD crash dates (2026-04-21–2026-10-12) sit inside the file.
- PREREG `PREREG_20261112_0830_t208.md`, SHA-256 `81c5475b752538c511d785b46f6ca93974ae4edb88bf2d49eeaf0f5549005a1e`, asserted before any P&L.
- Shared: one position, SL = TP = 1.5×ATR(14), 12 h time stop, **double-touch = loss**, $0.12/side, dollar swap as above. Sharpe is calendar (weekend 0) × **√365.25**, identical to `metrics_pack`. Daily P&L sums match trade-net totals (identity passed). 10% vol and exact 25% train-DD scales frozen on train (binary search on `(1+L·r)`).
- **g5** is the official `crash_gate`: mean daily P&L on the 26 dates ≥ −0.10% and non-loss rate (including flats) ≥ 50%. Raw per-day P&L is reported. g2b (corr to C1) is reported only; it is not a fail criterion for gold.

Four frozen specs:

| Spec | Idea | Why it is not a failed family |
|---|---|---|
| `G_IMP_BAR` | H1 range ≥ 1.5×ATR, body + favourable third, next open, 12 h | Not a Donchian, not daily S/R, not MR, both sides |
| `G_VOL_EXP` | Prior ATR < 0.85 × 48-bar median, then the same impulse | Same |
| `G_IMP_PULL` | Impulse, one-bar pause that holds the extreme and midpoint, enter next open | Same |
| `G_LONDON_ORB` | Box = 08:00–09:00 **Europe/London** (IANA DST, not a searched UTC hour); **one** break attempt on the 09:00–10:00 London H1, range ≥ 1.0×ATR, SL=TP=1.5×ATR, 12 h | **Distinct from `GR_D96`:** that was a continuous rolling 24 h *M15* Donchian (96 bars), any hour, TP 3× / SL 6× ATR. This is a single-hour London opening-range break, one shot, family stops. Not goldA (no prior-day / daily Donchian). NY 09:30 ET was **not** tried (would have been a fifth / searched spec). |

Realised holds are shorter than 12 h (medians 1–4 h) because 1.5×ATR usually hits first. A tail of 60–79 h holds is Friday-into-Sunday (first bar after the 12 h deadline is Sunday’s open). Most trades pay 0 nights.

---

## 3. Results (all four, equally)

Monthly is geometric. DD is a negative fraction. Trade stats are **net** bp, assigned by entry fill. Book holdout Sharpe through 2026-10-26 is **1.518**.

### 3.1 Train (2018–2023)

| Spec | n | WR | PF | Mean net bp | Mean hold | Sharpe 1× | Vol 1× | DD 1× | Lev 10% vol | Mo. @ 10% vol | DD @ 10% vol | Lev 25% DD | Mo. @ 25% DD | DD @ 25% DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| G_IMP_BAR | 3,004 | 48.2% | 0.870 | −2.13 | 5.3 h | **−1.43** | 7.4% | −52.2% | 1.34 | **−1.23%** | −63.2% | 0.39 | **−0.35%** | −25.0% |
| G_VOL_EXP | 1,446 | 47.6% | 0.809 | −2.84 | 2.8 h | **−1.49** | 4.6% | −35.8% | 2.19 | **−1.28%** | −62.6% | 0.65 | **−0.37%** | −25.0% |
| G_IMP_PULL | 900 | 46.9% | 0.883 | −1.84 | 8.2 h | **−0.64** | 4.3% | −18.3% | 2.32 | **−0.57%** | −37.9% | 1.42 | **−0.34%** | −25.0% |
| G_LONDON_ORB | 521 | 53.0% | 1.084 | **+1.12** | 3.0 h | **+0.33** | 2.9% | −7.4% | 3.45 | **+0.24%** | −23.5% | 3.71 | **+0.25%** | −25.0% |

The first three are fair-to-losing coins after costs (train mid bp around 0 to −1, cash ~1.5 bp). `G_LONDON_ORB` is the only name with a positive train mean and PF > 1. Train years at 1× for London: 2018 +0.7%, 2019 +2.0%, 2020 +0.7%, 2021 +1.7%, 2022 +4.8%, **2023 −4.1%**. A mild, uneven edge — already negative in the last train year. The other three have every (or almost every) train year negative.

### 3.2 Holdout (2024–2026-10-26)

| Spec | n | WR | PF | Mean net bp | Sharpe 1× | Vol 1× | DD 1× | Mo. @ 10% vol | DD @ 10% vol | Mo. @ 25% tr-DD | DD @ 25% tr-DD | corr book | corr C1 | Book 1.518 + 10% vol |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| G_IMP_BAR | 1,280 | 49.9% | 1.005 | +0.11 | **+0.04** | 11.3% | −19.4% | −0.04% | −25.3% | +0.01% | −8.1% | 0.062 | 0.011 | **1.094** (no lift) |
| G_VOL_EXP | 526 | 50.4% | 1.087 | +1.48 | **+0.49** | 5.6% | −14.4% | +0.44% | −29.0% | +0.14% | −9.6% | 0.066 | 0.015 | **1.451** (no lift) |
| G_IMP_PULL | 413 | 50.4% | 0.986 | −0.32 | **−0.07** | 6.7% | −12.8% | −0.19% | −27.5% | −0.09% | −17.7% | 0.049 | −0.017 | **1.008** (no lift) |
| G_LONDON_ORB | 210 | 49.5% | 1.203 | **+3.87** | **+0.66** | 4.4% | −7.2% | **+0.74%** | −23.0% | **+0.79%** | −24.5% | 0.024 | 0.022 | **1.536** (**lift**) |

`G_LONDON_ORB` is the closest miss: holdout Sharpe **0.66 < 0.8**, book lift **passes** (1.518 → 1.536), corr is near zero, g5 passes. Holdout years at 1×: 2024 **−2.1%**, 2025 +2.2%, 2026 (through 26 Oct) +8.2%. The 2026 leg is doing most of the holdout work. At both frozen sizes the monthly figure is under 1%, not 5%.

`G_VOL_EXP` holdout Sharpe 0.49 is **not** evidence: train Sharpe is −1.49 and the pre-sample is also negative. A holdout-only green is a fail, not a second look.

### 3.3 Pre-sample (2015–2017) and overlap

| Spec | Pre n | WR | PF | Mean bp | Sharpe 1× | Overlap Sharpe |
|---|---:|---:|---:|---:|---:|---:|
| G_IMP_BAR | 1,382 | 48.6% | 0.852 | −2.41 | **−1.66** | **−0.90** |
| G_VOL_EXP | 676 | 49.3% | 0.851 | −2.15 | **−1.14** | **−0.76** |
| G_IMP_PULL | 464 | 51.3% | 0.979 | −0.31 | **−0.12** | **−0.39** |
| G_LONDON_ORB | 197 | 45.7% | 0.655 | **−5.48** | **−1.59** | **+0.46** |

This is the honesty check on the closest miss: **`G_LONDON_ORB` is clearly negative in 2015–2017** (Sharpe −1.59, PF 0.66, all three pre years red). Combined with a negative 2023 and a negative 2024, the 2018–2022 / 2025–2026 pockets are not a transferable rule. Overlap Sharpe 0.46 is well under 0.8.

---

## 4. BD crash-day gate (official list, 26 dates, all in the 2026 holdout)

Official g5: mean ≥ −0.10% and non-loss rate ≥ 50%. **All four pass.** Raw non-flat days for the closest miss, and counts for all:

| Spec | Mean | Non-loss | Pos / Neg / Flat | g5a | g5b | Pass |
|---|---:|---:|---:|---|---|---|
| G_IMP_BAR | +0.045% | 53.8% | 13 / 12 / 1 | PASS | PASS (barely) | **PASS** |
| G_VOL_EXP | +0.098% | 80.8% | 7 / 5 / 14 | PASS | PASS | **PASS** |
| G_IMP_PULL | −0.007% | 73.1% | 6 / 7 / 13 | PASS | PASS | **PASS** |
| G_LONDON_ORB | +0.046% | 92.3% | 4 / 2 / 20 | PASS | PASS | **PASS** |

`G_LONDON_ORB` non-flat crash days (1× daily return): 2026-04-30 **+0.202%**, 2026-05-01 **−0.461%**, 2026-06-30 **−0.817%**, 2026-07-30 **+1.060%**, 2026-08-21 **+0.582%**, 2026-09-22 **+0.625%**. The other 20 dates are flat (no London-ORB trade that UTC day). It does **lose** on two crash days; the official gate allows that so long as the mean is almost non-negative and non-loss ≥ 50%. Per Nadav, gold is welcome; this gate is the constraint that stayed, and it is met.

---

## 5. Gates and the high-return brief

| Spec | g1 HO Sh ≥ 0.8 | g2 corr book ≤ 0.2 | g3 book lift | g4 overlap ≥ 0.8 | g5 BD crash | Pass | ≥5%/mo and ≤25% DD @ 10% vol | same @ 25% train-DD |
|---|---|---|---|---|---|---|---|---|
| G_IMP_BAR | FAIL (+0.04) | PASS (0.06) | FAIL (1.518→1.094) | FAIL (−0.90) | PASS | **NO** | FAIL | FAIL |
| G_VOL_EXP | FAIL (+0.49) | PASS (0.07) | FAIL (1.518→1.451) | FAIL (−0.76) | PASS | **NO** | FAIL | FAIL |
| G_IMP_PULL | FAIL (−0.07) | PASS (0.05) | FAIL (1.518→1.008) | FAIL (−0.39) | PASS | **NO** | FAIL | FAIL |
| G_LONDON_ORB | FAIL (+0.66) | PASS (0.02) | **PASS** (1.518→1.536) | FAIL (+0.46) | PASS | **NO** | FAIL (mo +0.74%) | FAIL (mo +0.79%) |

---

## 6. Multiple-testing honesty and the closest miss

Four specs were frozen before P&L and **all four are reported**. None passed g1. `G_LONDON_ORB` is the closest (holdout Sharpe 0.66, g2/g3/g5 pass, mild positive train PF 1.08) and is **still a fail**. Treating it as “almost the system” would be a post-P&L promotion of 1 of 4, and the **2015–2017 pre-sample is a clear reject** (Sharpe −1.59), as are 2023 and 2024. We did **not** then try NY 09:30 ET, a different box width, or a different ATR multiple. That would be a new, unregistered search.

The first three names have no mid-price edge on train (or a small negative) and lose the $0.24 cash + occasional swap, the same story as t207 on BTC. A textbook H1 gold impulse with R:R 1 does not survive RF costs on 2015–2026 Dukascopy mid.

**No MQL5 spec. No deployment. No fifth look.**

---

## 7. Files (unique t208 names; t202–t207 untouched)

t207 hashes re-checked unchanged: `RESULTS_t207.md` `0c93477064435023dafe395c7003b4a51d5c6902f110827c4ee1f8d608392614`; `PREREG_20261112_0825_t207.md` `42f24b6e0426f249321c634ed89781ef1650b0d9bb03b45f19ef8e189e7af2c2`.

| File | SHA-256 |
|---|---|
| `COST_PRESCREEN_20261112_0830_t208.md` | `0e52f697159dd0c214946b90879e1d7b4bbcfb5429c9ae7b69db5bec06aa6dad` |
| `PREREG_20261112_0830_t208.md` | `81c5475b752538c511d785b46f6ca93974ae4edb88bf2d49eeaf0f5549005a1e` |
| `code/backtest_t208.py` | `85e85cbf6934c4fef7930ada90657479a9dff6e1cd1ad01aedd4c0ced435008d` |
| `results_t208/summary.json` | `ca2d32fa3c5277c559983ab5e4fff70960a6d8db36fac4004a5310e324cb3e03` |
| `RESULTS_t208.md` | this file |

Engine: `code/backtest_t208.py` (imports `backtest_rnext` and `backtest_goldreaper` only; does not import `backtest_t199u.py` or `backtest_t199b.py`). `mkdir(..., exist_ok=False)` for `results_t208`.
