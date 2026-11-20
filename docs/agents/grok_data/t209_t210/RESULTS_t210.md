# RESULTS t210 — high-return sources: RF product check, vol-regime proxy, overnight premium

Written: 2026-11-12 08:52 Asia/Jerusalem (IST, UTC+2).
Round: t210. **Verdict: no deploy. All three pre-registered specs fail g1 (and g3, g4). All three official cost screens were DROP. No MQL5. No retune.**

---

## 1. What RoboForex actually offers (re-verified 2026-11-12, before P&L)

Public [contract specifications](https://roboforex.com/forex-trading/trading/specifications/), no login. The Pro, ECN and Prime tables were searched for `VIX`, `VOLX`, `VSTOXX` and `volatility`: **zero hits**. Unchanged from the 2026-11-10 note in `COST_PRESCREEN_20261110_2328.md` and `RESULTS_R2.md`.

**There is no VIX (or VXX / SVXY / UVXY / VSTOXX) CFD on Pro, ECN or Prime.** Short-volatility carry cannot be traded as a VIX product at RF. The brief’s fallback is used: a **long-US500-in-low-vol-regime proxy**, labelled as a proxy, not as a short-VIX trade.

**Index CFDs that do exist**, with official swaps identical across Pro / ECN / Prime (Friday triple; short swap is still a debit):

| Symbol | Pro spread | ECN / Prime spread | ECN comm. | Prime comm. | Swap short | Swap long |
|---|---:|---:|---|---|---:|---:|
| .US500Cash | 0.60 | 0.20 | 5 / mio | 4 / mio | −1.8% | **−8.6%** |
| .USTECHCash | 1.4 | 0.30 | 5 / mio | 4 / mio | −1.8% | **−8.6%** |
| .US30Cash | 2.9 | 0.80 | 5 / mio | 4 / mio | −1.8% | −8.6% |
| .DE40Cash | 0.90 | 0.30 | 5 / mio | 4 / mio | −1.8% | −7.2% |
| .JP225Cash | 7.5 | 5.5 | 5 / mio | 4 / mio | −1.8% | −7.2% |

**[VERIFIED]** official table, 2026-11-12. ProCent’s published table on the same page does not list these cash-index CFDs.

**Backtest costs (frozen, conservative, same mix as t209 / IR):** Pro average spread + ECN 5e−6/side. At the 2018–2023 median close (US500 $3,677.95, USTEC $11,549.69): US500 cash RT **1.73 bp**, USTEC **1.31 bp**. One long night is **2.36 bp** of 8.6% swap; with Friday ×3 the average session is 1.413 nights, so all-in overnight cost is **5.06 bp** (US500) and **4.64 bp** (USTEC). The 0.40-pt gap between Pro and ECN US500 spreads is ~0.11 bp at the train mid and cannot change a DROP.

---

## 2. Cost screen and literature (written first)

File: `COST_PRESCREEN_20261112_0850_t210.md`.

| Spec | Screen | Why | t210 action |
|---|---|---|---|
| Short VIX CFD | **unavailable** | No instrument. | Proxy below. |
| `VOL_REGIME_US500` | **DROP** (~2.3) | ~4.6–5%/yr of 8.6% swap at ~50% participation vs half of an 8% ERP on those days (~2%/yr). Cooper (2013) XIV CAGRs are **not** transferred. | **Tested** (new requested proxy). |
| `ON_US500` | **DROP** (3.18) | 5.06 bp vs half of an 8%/yr cash overnight premium (1.59 bp). | **Tested** as US500-only, frozen 2018–2023 / 2024–2026 windows. R1 A (4-index basket, 2014–2022 / 2023–2026) already failed g1/g3/g4 after swap (gross overlap Sharpe 1.19, net −0.04). |
| `ON_USTEC` | **DROP** (1.56) | 4.64 bp vs half of a generous 15%/yr Nasdaq overnight (2.98 bp). Same 8.6% swap. | **Tested**, same reason. |
| Intraday gap-fade (single name) | **DROP** | Corte, Kosowski & Wang’s **25 bp/day** is a 35-name **cross-sectional** futures book, not a single-index time-series edge. No published single-name “large” threshold is taken from a search. Brief: **only if costs allow.** | **Not PREREGed, not tested.** |

Sources used for parameters, not searched: Cooper, “Easy Volatility Investing”, SSRN 2255327 (2013) — 10-day window and VXV≡VIX3M ≥ VIX contango; Moreira & Muir, JF (2017); Simon & Campasano (2014) / Quantpedia (not tradable here); Cooper–Cliff–Gulen (2008), Kelly–Clark (2011), Lou–Polk–Skouras, JFE (2019), Boyarchenko et al., NY Fed SR 917.

---

## 3. Data, method, identity

- US500: Yahoo `^GSPC` `/workspace/research_new_component/data/yahoo/GSPC_d.csv`, 2000-01-03–2026-11-10. USTEC: Yahoo `^NDX`, same range. Official cash open/close, as in R1 A.
- VIX and VIX3M (signal only): Yahoo, VIX 2005-01-03–2026-11-11, VIX3M from 2006-07-17. Proxy pre-sample starts at the first valid 10-day SMA on or after VIX3M’s start.
- **Yahoo GSPC Open quality:** on **1,760 of 4,528 pre-sample sessions (38.9%)**, the next official Open equals that day’s Close (a known stale-open issue in older Yahoo cash-index files). That **does not** affect the official gates: **1 of 1,509 train sessions (0.1%)** and **0 of 718 holdout sessions**. NDX has only 44 such rows in the whole 2000–2026 file. Pre-sample ON_US500 Sharpe is therefore **not** a usable economic number and is reported only with that caveat. Train and holdout overnight figures are reliable.
- PREREG `PREREG_20261112_0850_t210.md`, SHA-256 `cb088015022f9f4582a9d629e17ac19af16d253629f737738be9ccbe4b994430`, asserted before P&L.
- Daily sums equal trade-net to machine precision for all three specs (−1.1e−16, −4.4e−16, 0). Sharpe = calendar × √365.25, matches `metrics_pack`. 10% vol and exact 25% train-DD scales frozen on train. g5 n/a (no gold).

**Rules (frozen):**
- `VOL_REGIME_US500`: at close T, long iff `VIX_T < SMA10(VIX)` **and** `VIX3M_T ≥ VIX_T`. Exit at close when either fails. **Hard stop:** if VIX open on T+1 is already ≥ `SMA10_T`, sell US500 at the **cash open**. No new threshold.
- `ON_US500` / `ON_USTEC`: every session, buy cash close, sell next cash open, 8.6% long swap every night, Friday ×3. No filter.

---

## 4. Results (all three, equally)

Monthly is geometric. Trade stats are **net** bp (after cash and swap), by entry period. Book holdout Sharpe is 1.554 through each series’ last date (2026-11-10).

### 4.1 Train (2018–2023)

| Spec | n | WR | PF | Mid bp | Cash+swap | Mean net bp | Sharpe 1× | Vol | DD | Mo. @ 10% vol | DD @ 10% | Mo. @ 25% tr-DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| VOL_REGIME_US500 | 202 | 45.5% | 1.343 | +31.83 | 1.81+14.58 | **+15.44** | **+0.50** | 10.5% | −18.7% | **+0.38%** | −17.9% | **+0.51%** |
| ON_US500 | 1,509 | 50.2% | 0.877 | +2.78 | 1.84+3.42 | **−2.47** | **−0.63** | 9.6% | −35.6% | **−0.57%** | −36.7% | **−0.35%** |
| ON_USTEC | 1,509 | 51.8% | 0.961 | +3.64 | 1.49+3.42 | **−1.27** | **−0.20** | 15.0% | −35.1% | **−0.20%** | −24.7% | **−0.21%** |

The overnight premium is **real on the mid** (US500 +2.78 bp/session ≈ 7.0%/yr, USTEC +3.64 bp ≈ 9.2%/yr) and is **smaller than RF swap+cash** (≈ 5.1 / 4.6 bp). That is the same failure mode as R1 A, now visible on each name alone. The proxy has a thin train edge after 8.6% swap (Sharpe 0.50), with 2019–21 green, **2018 −3.5%**, **2022 −11.2%**. Participation was 55% of train sessions (ASSUMED 50% in the screen was close). 100 of 202 train exits were the VIX-open hard stop — the stop fires often because entry requires VIX just *below* its 10-day SMA, so a modest VIX up-open crosses it. That is the frozen rule, not a reason to loosen it.

### 4.2 Holdout (2024–2026-11-10)

| Spec | n | WR | PF | Mid bp | Mean net bp | Sharpe 1× | Mo. @ 10% vol | DD @ 10% | Mo. @ 25% tr-DD | corr book | Book + 10% vol |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| VOL_REGIME_US500 | 95 | 44.2% | 1.128 | +20.87 | +5.89 | **+0.21** | +0.11% | −10.9% | +0.15% | **−0.018** | 1.554 → **1.496** (no lift) |
| ON_US500 | 717 | 54.7% | 1.029 | +5.00 | +0.49 | **+0.13** | +0.06% | −16.4% | +0.05% | 0.065 | 1.554 → **1.390** (no lift) |
| ON_USTEC | 717 | 55.5% | 1.069 | +6.14 | +1.98 | **+0.34** | +0.22% | −14.8% | +0.23% | 0.068 | 1.554 → **1.477** (no lift) |

`ON_USTEC` is the closest overnight Sharpe (0.34 < 0.8): 2024 **+12.2%**, 2025 +1.5%, 2026 −2.4%. `VOL_REGIME` 2024 +5.1%, 2025 +9.3%, **2026 −9.3%**. US500 overnight 2024 +7.4%, then 2025–26 red. No holdout is near 0.8, and none lifts the book. The 5%/month brief is not close.

### 4.3 Pre-sample and overlap

| Spec | Pre n | Pre Sharpe 1× | Pre note | Overlap Sharpe |
|---|---:|---:|---|---:|
| VOL_REGIME_US500 | 378 | **−0.04** | 2008 **−21.9%**; 2013 +19.2%; already decaying | **+0.42** |
| ON_US500 | 4,528 | **−8.68** (not usable) | Yahoo Open = prior Close on 38.9% of pre sessions; mid measured near 0 while full cash+swap is still charged. Every pre year −5% to −26% is mostly that artifact plus 8.6% swap, **not** a new economic finding. | **−0.41** |
| ON_USTEC | 4,528 | **−1.41** | NDX opens are usable (44 stale rows only). Cash was large at 2001–02 lows (mean pre cash 7.0 bp) plus 8.6% swap; 2001 −38.6%, 2008 −39.1%. 2017 is the first near-flat year (+1.0%). | **−0.03** |

The proxy’s **best window is the train** (Sharpe 0.50), not the pre-sample and not the holdout — the opposite of a “published sample looks fine, holdout dies” story, and still well under 0.8 on every official window.

---

## 5. Volmageddon (Feb 2018) and March 2020 — `VOL_REGIME_US500`

Descriptive, not a fifth gate. Full tables: `results_t210/stress_volmageddon_2018.csv`, `stress_covid_2020.csv`.

**5–9 Feb 2018 (Volmageddon): the rule was FLAT.** From 30 Jan, VIX close (14.79) was already **above** its 10-day SMA (12.03), so `in_regime` was false; on 2 Feb the curve was also in backwardation (VIX 17.31). VIX opened 18.44 on Monday 5 Feb and closed 37.32; the proxy held no US500 through the crash or the rest of that week. First re-entry: **close of 14 Feb**, after the event, once VIX 19.26 < SMA 25.82 and the curve was back in contango. No hard stop fired in the 30 Jan–14 Feb window because there was no open position. The filter did what it was supposed to do on this event.

**March 2020:** last long was 19 Feb close → 20 Feb close (net **−42.4 bp**, mid −38.2), then **FLAT through the entire March crash**. `in_regime` was false for every session 20 Feb–31 Mar (VIX well above its SMA; the curve often in backwardation). The 5–18 Feb hold, still in a calm regime, finished **+74.2 bp** net. One morning (20 Feb) was still long from the prior close; the exit was a regular close exit, not a hard-stop open. The March equity collapse is not in the P&L.

The filter therefore avoided both named stress windows. That is **not** a pass: 2008 pre-sample still lost 21.9%, train 2022 lost 11.2%, holdout 2026 lost 9.3%, and holdout Sharpe is 0.21. Avoiding two famous crashes does not make a 0.21 Sharpe sleeve a high-return component.

---

## 6. Gates and the high-return brief

| Spec | g1 HO Sh ≥ 0.8 | g2 corr ≤ 0.2 | g3 book lift | g4 overlap ≥ 0.8 | g5 | Pass | ≥5%/mo @ 10% vol or 25% DD |
|---|---|---|---|---|---|---|---|
| VOL_REGIME_US500 | FAIL (+0.21) | PASS (−0.02) | FAIL (1.554→1.496) | FAIL (0.42) | n/a | **NO** | FAIL (mo +0.11%) |
| ON_US500 | FAIL (+0.13) | PASS (0.07) | FAIL (1.554→1.390) | FAIL (−0.41) | n/a | **NO** | FAIL |
| ON_USTEC | FAIL (+0.34) | PASS (0.07) | FAIL (1.554→1.477) | FAIL (−0.03) | n/a | **NO** | FAIL |

All three have **low** correlation to C1+I2 (overnight is complementary to I2’s afternoon Nasdaq window, as R1 already noted; the proxy’s holdout corr is essentially zero). Adding any of them at 10% train-vol **lowers** holdout book Sharpe. g2 passing and g5 n/a do not rescue a failed g1.

---

## 7. Multiple-testing honesty

Three specs were frozen before P&L; all three cost screens were already DROP; all three are reported. None passed g1. There is no “best of three” to promote. `ON_USTEC` holdout 0.34 and `VOL_REGIME` train 0.50 / holdout 0.21 are the closest numbers and remain well under 0.8, with overlap 0.42 at best, a failed book-lift, and no approach to 5%/month.

The two overnight names confirm R1 A on each index separately and on the frozen windows: the cash-session mid is positive in train and holdout, and **8.6% long swap plus cash erases it**. A tighter ECN spread (0.20 / 0.30 instead of Pro 0.60 / 1.4) would change the cash leg by a few tenths of a bp and would not change the verdict. The fourth brief idea (single-name gap-fade) was not given a second chance after a DROP screen.

No parameter was changed after P&L. The hard stop was not loosened, even though it fired on about half of the proxy’s exits. **No MQL5. No deployment.**

---

## 8. Files (unique t210 names; t202–t209 untouched)

t209 RESULTS SHA re-checked unchanged: `b8d9af51b54f9ac38514239f491b996d5ef9f283d1dfe68bd29db4e67e11b750`.

| File | SHA-256 |
|---|---|
| `COST_PRESCREEN_20261112_0850_t210.md` | `5de8222200522ecca93f6b85934fe2cb7a53f2ef4eb1c6aad7e8ae73616799a4` |
| `PREREG_20261112_0850_t210.md` | `cb088015022f9f4582a9d629e17ac19af16d253629f737738be9ccbe4b994430` |
| `code/backtest_t210.py` | `2758d3992777c27b3de2737fa514442d606fd86ac02896a9a871b618db0fb728` |
| `results_t210/summary.json` | `de43c3dd528c1c9775257511a6ac62e54b6d647da0c6d398ee1864871403229f` |
| `RESULTS_t210.md` | this file |
