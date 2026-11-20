# RESULTS t207 — BTC momentum-impulse family (SFE Impulse / Crypto Pepper inspired)

Written: 2026-11-12 08:26 Asia/Jerusalem (IST, UTC+2).
Round: t207. **Verdict: no deploy. All four pre-registered specs fail g1, g3 and g4. No MQL5. No retune.**

This is a new family, not a retest of BTC MR, BTC_MON, BTC_MAX10, C1, or BTC_WMOM. Exact vendor rules were unpublished; the four specs are textbook impulse rules frozen from the live-stat *shape* (6–24 h holds, hard SL, R:R ≈ 1) **before any P&L**.

---

## 1. Public logic (gathered before the PREREG)

**SFE Impulse** (MQL5 signal 2049326, Market product 104102, Joel Juanpere / atractor). Live stats, VERIFIED t206: BTC+ETH, ~6 h holds, WR 58%, PF 1.37, avg win €12.91 ≈ avg loss €12.97 (SL-like, R:R ≈ 1), ~10% activity, 9 trades/week on both symbols, 38 months, equity DD 7.88%, currently −9.70%/month. Product page and comments do **not** publish an entry rule, ATR multiple, or session. `smartforexexpert.com` returned HTTP 500 this turn. Sibling names (“SFE Raw Impulse ICT”, “SFE Fr And Impulse”, “SFE Swing EA” — “medium timeframes, catch big movements, attach to one BTCUSD M5 chart”) and reviews (needs Saturday crypto sessions; weak in a quiet June 2024) only support an ASSUMED **breakout / impulse in high-vol regimes** story. **UNKNOWN** as an exact rule. Other vendors’ “impulse” presets found in search were treated as untrusted and were not used.

**Crypto Trading Pepper** (signal 1521998, Valeriia Mishchenko). Live stats, VERIFIED t206: BTC+ETH, 21 h holds, WR 47%, PF 1.18, 54 months, equity DD 7.73%, 80% of growth in 16 days (fails our concentration filter), currently −13.94%/month. Exact entry is **unpublished**. Her public blogs describe **grid** money-management for Waka Waka and night scalpers for other EAs; those are **not** Pepper’s 21 h book and were **not** copied.

Session-open / Asia-open breakout was an example in the brief but is **not** one of the four specs: a prior W1 Asia-open BTC test already failed, and trying other session hours would have been a search.

---

## 2. Cost pre-screen (written first)

File: `COST_PRESCREEN_20261112_0825_t207.md` (SHA-256 `a67ee2b53b6c774a96599d4533d3137db7dc11eb4208159b6bb891623baa8dec`).

**BTC ECN** (VERIFIED this turn, RoboForex contract page, same as the frozen C1 / rnext figure the user asked for): **1.42 bp/side**, 2.84 bp RT, swap −4.75%/yr both sides ≈ **1.30 bp/night**. Cap 0.02%/side: PASS. Frozen schedule: 1.30 bp at each 21:00 UTC the position is open at that bar’s open, weekend nights included, **no Friday triple** (annual rate VERIFIED; day-count ASSUMED).

**ETH ECN** (VERIFIED this turn): commission **300/mio = 3.00 bp/side** already, plus ~0.20 bp/side spread ≈ **3.20 bp/side, 6.40 bp RT**, same 4.75% swap. **Fails the 2 bp/side cap** on commission alone. Conservative SFE-shaped edge on ETH (half of 0.16 × 1.5 × train-median ATR ≈ 13.1 bp) vs 6 h cost 7.05 bp gives ratio **0.54** (MARGINAL); Pepper-shaped 21 h ratio **0.86** (DROP). A PASS at 1/3 would need a published expectancy ≥ ~42 bp/trade. The SFE-implied ~26 bp is not huge. **ETH is not traded.**

**BTC family:** SFE-shaped 6–12 h ratio **0.34 MARGINAL**; Pepper-shaped 18–21 h ratio **0.60 MARGINAL**. The user asked for this family, so the hashed PREREG and the backtest went ahead on BTC only.

---

## 3. Data and method

- **Primary (all official numbers):** Binance spot `BTCUSDT` H1, `/workspace/research_new_component/data/binance/BTCUSDT_1h.csv`, 80,797 bars, **2017-08-17 04:00 UTC through 2026-11-09 23:00 UTC**, columns include volume. Last-trade treated as mid; 1.42 bp/side applied on top. **Best H1 source on the box.** No native BTC M15 file is present.
- CFD `data/cfd_h1/BTCUSD.csv` is H1 only from 2016-12-13 (daily/weekend bars before that) and has no Binance-style volume. **Not used** (would mix feeds).
- **Pre-sample:** 2017-08-17–2017-12-31 (~4.5 months), reported only, not used to choose a spec.
- **Train:** 2018-01-01–2023-12-31. **Holdout:** 2024-01-01–2026-11-09.
- PREREG `PREREG_20261112_0825_t207.md`, SHA-256 `42f24b6e0426f249321c634ed89781ef1650b0d9bb03b45f19ef8e189e7af2c2`, asserted in `code/backtest_t207.py` **before any P&L**.
- Shared engine (frozen): one position, SL = TP = 1.5 × ATR(14) (SMA of True Range), R:R 1, time stop 12 h (18 h on `DONCH_IMP`), **double-touch within a bar = loss at SL**, gap-through fills at the open, 1.42 bp/side cash, 1.30 bp per 21:00 UTC night. Sharpe is calendar days including weekends, mean / sample-std × **√365.25**. Confirmed identical to `metrics_pack(..., crypto_calendar=True)`. Daily P&L sums match the trade-net totals to the tick (identity check passed).
- Scales frozen on **train only**: leverage so train vol = 10%; leverage so train equity DD = **25% exactly** (binary search on `(1+L·r)` , not the linear `0.25/|DD_1x|` approximation).
- Book: `/workspace/independent_review/results/combined_daily.csv` (`c1`, `i2`, `pnl`). Book holdout Sharpe **1.557**.

Four frozen specs (textbook, no search):

| Spec | Idea | Time stop |
|---|---|---|
| `IMP_BAR` | H1 range ≥ 1.5×ATR, body + close in the favourable third, enter next open | 12 h |
| `DONCH_IMP` | Close beyond the prior 24-hour Donchian, range ≥ 1.0×ATR and volume ≥ 20-bar SMA | 18 h |
| `VOL_EXP` | ATR(14) on the prior bar < 0.85 × its 48-bar median, then a 1.5×ATR impulse bar as in `IMP_BAR` | 12 h |
| `IMP_PULL` | Same impulse, then a one-bar pause that holds the impulse extreme and midpoint; enter the following open | 12 h |

g2b risk on `DONCH_IMP` was stated in the PREREG before P&L (short-horizon Donchian can still look like C1). Realised holdout corr to C1 is 0.15, which **passes** g2b; the failure is the missing edge, not a C1 clone.

Realised holds are **shorter** than the 6–24 h design (medians 2–4 h) because 1.5×ATR SL/TP usually hits before the time stop. Activity is **higher** than SFE’s ~10% for `IMP_BAR` and `DONCH_IMP` (train hours in market ≈ 26% and 25%); `VOL_EXP` ≈ 8% and `IMP_PULL` ≈ 13% are closer. **k was not raised after the fact to match 10%.** Long and short are both taken (slightly more longs, ~52–54%).

---

## 4. Results (all four, equally)

Sharpe, vol and monthly returns use the calendar series (weekends included). Monthly is geometric, `(1+CAGR)^(1/12)−1`. Max equity DD is a negative fraction. Trade stats use **net** bp (after 1.42 bp/side and swap) and are assigned by **entry** fill.

### 4.1 Train (2018–2023)

| Spec | Trades | WR | PF | Mean net bp | Mean hold | Sharpe 1× | Vol 1× | DD 1× | Lev 10% vol | Mo. @ 10% vol | DD @ 10% vol | Lev 25% DD | Mo. @ 25% DD | DD @ 25% DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| IMP_BAR | 3,204 | 49.9% | 0.982 | −1.17 | 4.3 h | **−0.19** | 36.7% | −65.8% | 0.272 | **−0.20%** | −22.2% | 0.311 | **−0.23%** | −25.0% |
| DONCH_IMP | 2,638 | 50.0% | 0.946 | −4.12 | 4.9 h | **−0.53** | 35.5% | −80.4% | 0.282 | **−0.48%** | −32.0% | 0.214 | **−0.36%** | −25.0% |
| VOL_EXP | 1,221 | 49.1% | 0.998 | −0.12 | 3.6 h | **−0.04** | 18.8% | −50.7% | 0.533 | **−0.08%** | −30.2% | 0.432 | **−0.06%** | −25.0% |
| IMP_PULL | 1,213 | 47.9% | 0.899 | −6.85 | 5.5 h | **−0.66** | 22.0% | −68.4% | 0.455 | **−0.59%** | −39.0% | 0.270 | **−0.34%** | −25.0% |

Closest to flat on train is `VOL_EXP` (mean −0.12 bp, PF 0.998, Sharpe −0.04). Gross mid for that name is +2.94 bp, which **does not clear** 2.84 bp cash + 0.22 bp swap. `IMP_BAR` gross mid is only +1.96 bp, also short of costs. Avg win ≈ avg loss on all four (as designed); WR sits at or just under 50%, not SFE’s live 58%.

Train years at 1× (not a selection device):

- IMP_BAR: 2018 −6.3%, 2019 +12.8%, 2020 −32.5%, 2021 +20.5%, 2022 −24.9%, 2023 −31.7%.
- DONCH_IMP: every train year negative (2021 −50.8% the worst).
- VOL_EXP: 2018 +33.3%, 2019 +4.3%, then 2020–2023 all negative (2022 −26.0%). One good year, then decay. **Not** a reason to keep the spec.
- IMP_PULL: every train year negative.

### 4.2 Holdout (2024–2026-11-09)

| Spec | Trades | WR | PF | Mean net bp | Mean hold | Sharpe 1× | Vol 1× | DD 1× | Mo. @ 10% vol | DD @ 10% vol | Mo. @ 25% tr-DD | DD @ 25% tr-DD | corr C1 | corr book | Book + 10% vol Sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| IMP_BAR | 1,957 | 48.6% | 0.929 | −3.23 | 3.6 h | **−0.89** | 24.9% | −56.2% | **−0.52%** | −18.8% | **−0.60%** | −21.2% | 0.074 | 0.097 | 1.557 → **1.044** |
| DONCH_IMP | 1,415 | 50.3% | 0.952 | −2.35 | 4.2 h | **−0.50** | 23.4% | −51.5% | **−0.29%** | −17.9% | **−0.22%** | −13.9% | 0.153 | 0.156 | 1.557 → **1.181** |
| VOL_EXP | 732 | 48.2% | 0.899 | −3.86 | 2.9 h | **−0.77** | 12.9% | −38.3% | **−0.46%** | −22.4% | **−0.37%** | −18.5% | 0.003 | 0.011 | 1.557 → **1.117** |
| IMP_PULL | 627 | 48.3% | 0.924 | −3.45 | 4.6 h | **−0.53** | 14.4% | −36.0% | **−0.30%** | −18.0% | **−0.18%** | −11.0% | 0.055 | 0.089 | 1.557 → **1.200** |

Holdout years at 1×: IMP_BAR 2024 −18.9%, 2025 −34.7%, 2026 (through 9 Nov) −8.2%. DONCH_IMP 2024 **+9.5%**, 2025 −31.3%, 2026 −11.8% — one green year does not pass a 2.9-year holdout. VOL_EXP 2024 −20.3%, 2025 −15.7%, 2026 +9.6%. IMP_PULL all three negative.

### 4.3 Pre-sample (2017-08-17–2017-12-31) and overlap

| Spec | Pre trades | WR | PF | Mean bp | Sharpe 1× | Train corr C1 | Overlap Sharpe 1× |
|---|---:|---:|---:|---:|---:|---:|---:|
| IMP_BAR | 202 | 46.5% | 0.779 | −33.1 | **−2.28** | 0.055 | **−0.35** |
| DONCH_IMP | 164 | 50.6% | 0.765 | −36.8 | **−2.34** | 0.129 | **−0.51** |
| VOL_EXP | 74 | 55.4% | 1.033 | +3.63 | **+0.50** | 0.021 | **−0.22** |
| IMP_PULL | 82 | 46.3% | 0.855 | −21.2 | **−0.81** | 0.002 | **−0.62** |

The only positive pre-sample cell is `VOL_EXP` (Sharpe 0.50, 74 trades, 4.5 months). That is short, below the 0.8 bar, and is **followed by a negative train and a worse holdout**. It is not a pass and was not used to promote the spec.

Double-touch losses (conservative, counted as SL): train 36 / 35 / 19 / 9 across the four specs; holdout 16 / 10 / 8 / 2. Swap nights average 0.15–0.26 per trade (most holds die before 21:00 UTC).

---

## 5. Gates and the high-return brief

| Spec | g1 HO Sh ≥ 0.8 | g2 corr book ≤ 0.2 | **g2b corr C1 ≤ 0.2** | g3 book lift | g4 overlap Sh ≥ 0.8 | g5 | Pass | ≥5%/mo and ≤25% DD @ 10% vol | same @ 25% train-DD size |
|---|---|---|---|---|---|---|---|---|---|
| IMP_BAR | FAIL (−0.89) | PASS (0.10) | PASS (0.07) | FAIL (1.557→1.044) | FAIL (−0.35) | n/a | **NO** | FAIL (mo −0.52%, DD OK) | FAIL (mo −0.60%) |
| DONCH_IMP | FAIL (−0.50) | PASS (0.16) | PASS (0.15) | FAIL (1.557→1.181) | FAIL (−0.51) | n/a | **NO** | FAIL (mo −0.29%) | FAIL (mo −0.22%) |
| VOL_EXP | FAIL (−0.77) | PASS (0.01) | PASS (0.00) | FAIL (1.557→1.117) | FAIL (−0.22) | n/a | **NO** | FAIL (mo −0.46%) | FAIL (mo −0.37%) |
| IMP_PULL | FAIL (−0.53) | PASS (0.09) | PASS (0.06) | FAIL (1.557→1.200) | FAIL (−0.62) | n/a | **NO** | FAIL (mo −0.30%) | FAIL (mo −0.18%) |

g2 and g2b **pass for every spec**. These impulse rules are **not** C1 in disguise. Adding any of them at the 10% train-vol size **lowers** the book’s holdout Sharpe. The high-return brief (≥5%/month at a size that keeps DD ≤ 25%) is not close: at both frozen sizes the monthly figure is slightly negative.

---

## 6. Multiple-testing honesty and what this does (and does not) say

Four specs were frozen before P&L and **all four are reported**. None passed g1. This is **not** a “best of four” story and does not need a Bonferroni apology for a single lucky holdout — the family failed cleanly, in train as well as holdout, after a cost screen that already called the edge MARGINAL.

What we showed:

- A textbook H1 impulse with R:R 1 and 6–18 h time stops, on the best BTC H1 we have, with RF ECN costs, is approximately a **fair coin on mid** (train gross +2 to +3 bp on the two least-bad names, ~0 to −4 bp on the others) and **loses the 2.84 bp cash + swap** every time. Holdout is as bad or worse.
- That does **not** prove SFE Impulse or Pepper have no edge. Their exact rules are unpublished. It does show that the obvious impulse / Donchian / vol-expansion / pullback-continuation readings of their *live-stat shape* do not survive our costs and our gates on 2018–2026 Binance H1.
- We did not raise `k`, change R:R, switch session hours, add ETH, or drop a spec after seeing P&L. Doing any of those now would be a new, unregistered search.
- SFE’s live book is itself at −9.70%/month in the t206 snapshot; Pepper is at −13.94%/month and already failed concentration. The holdout here is consistent with “this shape is not currently paying,” not with “we decoded a hidden winner.”

**No MQL5 spec. No deployment. No fifth look.**

---

## 7. Files (unique t207 names; t202–t206 untouched)

t206 hashes re-checked unchanged: `RESULTS_t206.md` `9e72e21875eec8fc3b112f3b4161e0a0d92ad73d86796466663e481b74f69d0b`; `shortlist_t206.md` `e4fcd8b910dfda501cf3d9a8f7137c527ad8db3544f81f15e1eedd1d2e0af56c`.

| File | SHA-256 |
|---|---|
| `COST_PRESCREEN_20261112_0825_t207.md` | `a67ee2b53b6c774a96599d4533d3137db7dc11eb4208159b6bb891623baa8dec` |
| `PREREG_20261112_0825_t207.md` | `42f24b6e0426f249321c634ed89781ef1650b0d9bb03b45f19ef8e189e7af2c2` |
| `code/backtest_t207.py` | `5843846f50ad0b09897d85ec661317370d98b0f582f2a314b71833a90e3f645f` |
| `results_t207/summary.json` | (see directory; trades and daily CSVs per spec) |
| `RESULTS_t207.md` | this file, hashed after write |

`results_t207/` holds `trades_{SPEC}.csv`, `daily_{SPEC}.csv`, `summary.json`, `summary.csv`. Engine: `code/backtest_t207.py` (imports `backtest_rnext` helpers only; does not import `backtest_t199u.py` or `backtest_t199b.py`). `mkdir(..., exist_ok=False)` for `results_t207`.
