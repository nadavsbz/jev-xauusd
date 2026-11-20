# RESULTS t214 — keep searching: five families, Darwin/Zulu scan

Written: 2026-11-12 10:02 Asia/Jerusalem (IST, UTC+2).

**Verdict: nothing new to deploy, nothing to PREREG, no MQL5, no strategy P&L.** All four tradable families on the brief are either **already tested and closed** or **DROP** on the frozen cost screen. The Darwin / ZuluTrade public scan found **no** strategy with ≥ 3 years of history, ≥ 3%/month honest return, and a public rule we can replicate at RoboForex.

This is the frozen method working as designed (same empty-set outcome as t211), not a skipped step. COST was written and hashed **before** any t214 P&L; there was then nothing honest to hash a PREREG for.

No accounts, terminals, testers, or `accounts.json` were touched. Unique t214 names; t199c–t213 were not overwritten. No portfolio combination. Gold and grids were not rejected a priori; none of the five items was a grid that needed a new equity-DD test.

---

## 0. Hashes and method

| File | SHA-256 |
|---|---|
| `COST_PRESCREEN_20261112_0958_t214.md` | `d3f39381033a1b72076beae4df869dcd0708e3af855473e90b283791719fd814` |

No `PREREG_*t214*`, no `code/backtest_t214*`, no `results_t214/`. Costs, already-tested table, and Darwin numbers are in the COST file (VERIFIED / OBSERVED tags there). Screen: cost / conservative edge ≤ 1/3 PASS, ≤ 0.6 MARGINAL, else DROP; cash cap 2 bp/side; closed ideas are not retested; no bar-size approximation.

---

## 1. The four tradable families

### (a) FX CS carry + momentum, weekly, “real” swap — **do not retest**

Three G10-carry attempts already exist: R1-B holdout Sharpe **0.68** (train 0.21, fails overlap); rnext `FX_CT` (carry + 12m trend) holdout **−0.67**; carry alone at 0 pp markup (post-verdict only) holdout 0.97 / overlap **0.36**. R3-J FX CS momentum was **negative even gross**. rnext’s written lesson: *“Stop testing G10 carry on RF.”* Weekly vs monthly, and multiplying two failed legs, is not a new family. Today’s RF swap card is a snapshot, not 2018–2023 income; historical carry on the box is BIS rates, already used.

### (b) Multi-asset weekly TSMOM (XAU, US500, NAS100, DAX, BTC, majors) — **DROP and/or already tested**

Moskowitz-style ~12%/year gross, conservative 6%. Index swaps (t210, VERIFIED) are **−8.6% long / −1.8% short** on US500 and USTEC, **−7.2%** long on DE40, both sides a debit. At a 70/30 long/short occupancy the swap cost is **6.56%/yr** (US) and **5.58%/yr** (DAX), ratios **1.09** and **0.93** — **DROP**. Gold long swap ~**14%/yr**; rnext `G_SHORT` was flat for the entire holdout (the 12m signal stayed long). BTC weekly 12m is **already** `BTC_WMOM`: holdout **0.72**, overlap 0.32, C1 corr 0.12, failed g1/g4; a book that includes BTC is a C1-neighbour, which the brief asked us to avoid. FX TSMOM/CS is R3-J (gross fail). R1 sleeve D already ran 12-month TSMOM on US500+DAX+Nikkei: train **−0.42**, holdout 0.49, overlap **−0.03**, overlap DD **−70.5%**. Weekly on a 12-month lookback is almost the same signal. **Not PREREGed.**

### (c) Index/gold month-end and pre-holiday, net of swap — **do not retest**

Closed in t209’s COST list: R1-C ToM (holdout 0.56); t188u D6 payday (fail), **D7 pre-holiday holdout 0.62** (book lift, not a permitted standalone), D10 OPEX (fail); month-end EURUSD (Claude R19 / R2-G). Gold month-end is the same ToM rule; gold long swap only raises the cost. **Not PREREGed.**

### (d) DAX/US500 overnight-gap fade at cash open — **DROP**, no faithful bar

t211 idea 15, first-30-minute fade: ratio **0.89** US500 / **0.67** USTEC vs frozen 0.6 — **DROP**. Box has H1 only; a 60-minute exit would change the 30-minute parameter. All-day single-name fade was DROP in t210 (Corte 25 bp is a 35-name CS). Overnight *holds* (R1 A, t210 `ON_*`) are a different, already-failed rule. **Not PREREGed.** No MQL5.

---

## 2. Darwin / ZuluTrade public scan (the only new work)

Filter: ≥ 3 years **and** ≥ 3%/month honest, which is **(1.03)^12 − 1 = 42.6%/year**, plus a public description we can implement. Public access only; no login. `darwinex.com/darwins` is **404** this turn. List and product pages used: `darwinexzero.com/all-darwins`, `darwinex.com/invest/{ticker}`, `zulutrade.com/leaders`. Figures OBSERVED 2026-11-12, Darwinex returns **gross** of 1.2% + 20% fees.

**No Darwin on the public high-AUM / 3-year board meets 3%/month.** The honest end of the board is mid-teens to mid-twenties annualized, teens of drawdown, at a 6.5% monthly VaR target:

| Darwin | Track | Annualized | Compound monthly | DD |
|---|---|---:|---:|---:|
| THA (~12y, since 01/2015) | +818.49% | 20.3% | **1.55%** | −14.47% |
| SYO (~10y) | 10y +316.73% | 15.34% | **1.20%** | −13.09% |
| AUM #1 (since 10/2014) | +292.15% | ≈12.1% | ≈0.96% | −16.37% |
| LSP (~3y, investable 16/10/2023) | 3y +96.47% | **25.25%** | **1.89%** (best 3y seen) | — |
| EPTN (~3y) | 3y +56.98% | 16.22% | 1.26% | — |

**No public entry rule.** Darwinex help (VERIFIED): trade details are not revealed, to protect the trader’s IP. Pages give asset class, trade count, duration (LSP: 852 trades, ~1 day, WR 52%), not a specification. The TWYG interview (29/10/2026) is a *process* for testing breakouts, not a frozen rule; this program already failed textbook breakouts.

**ZuluTrade:** landing-page “top” figures are short-window or raw cumulatives (FIRE GC +3133%, ReVeR273 +1138%) that are not honest 3%/month over 3 years. Independent public study of **1,310** real-money leaders with ≥ 3 years (edgeormyth, through June 2026): following the best fifth, re-picked quarterly, **lost 7.7% per average quarter** before fees. No replicable public rule cleared the filter.

---

## 3. What to hand Claude

**No MQL5-ready spec from t214.** Nothing passed, and nothing *nearly* passed that is new. Closest misses already on the closed list — R1-B carry 0.68, `BTC_WMOM` 0.72, `BTC_HALV` 0.71, D7 0.62, t208 `G_LONDON_ORB` 0.66 — must not be retuned.

Optional, not a new official assignment (same as t211):

1. **US500 5-minute ORB** and a **small DAX cash-open ORB** on the **tester only**, if they are not a rerun of Nasdaq R11 (Sh 0.33, corr I2 0.39). The box has H1 only; H1 first-bar would change the published parameters. Grok will not approximate.
2. **First-30-minute gap fade** only if a *new* cost screen with hour-of-day spreads and M5 data puts the ratio ≤ 0.6. Official t211/t214 ratio is DROP (0.89 / 0.67).
3. **Do not** log into Darwinex or ZuluTrade for us, and do not scrape private trade lists. If a *public*, no-login trade history for a 3-year Darwin ever appears, a t212-style decode gate (profile + random-timing, PREREG first) would be the right next step — not a rule search from an interview.

`US500_3DD` already has an MQL5 spec from t199u (M1, holdout-area Sharpe 0.81, CAGR 4.5%, DD −11.8%). Nadav has said it is too small. Do not restart it here.

---

## 4. Where that leaves the search

After t207–t214 this week, the pattern is consistent: published or live-stat *shapes* that still look cheap on a 2010s futures paper lose RF swap (indices 8.6%, gold 14% long, BTC 4.75% both ways), or they were already run on 2018–2023 / 2024–2026 and failed g1. EdgeTrader (t212) has **timing skill** we have not recovered as a passing rule; SFE Impulse (t213) **fails** the same decode gate. Carry, TSMOM, ToM, pre-holiday, overnight, and gap-fade are exhausted on the box’s bars. The next useful work is either a **new** published rule that survives the cost screen, or Claude’s M5/tester looks listed above — not another weekly wrapper around a closed sleeve.
