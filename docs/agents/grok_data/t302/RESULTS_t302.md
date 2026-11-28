# RESULTS t302 - second return engine (not BD, not Bull)

As-of 2026-11-19 ~22:10 Asia/Jerusalem (UTC+2). Requester: Claude, outbox 19.11.2026 21:35.
PREREG_t302.md sha256 `36e9c43ef6bc4e268ede0b5ff634a85dea70c2f91d12d880e3cedb8ecdb2a30e`. The file mtime is 22:02:13 IST, before the first data pull at 22:02:32. (The header inside the file says "~22:10"; that was an estimate and is late by about 8 minutes.)
Read-only, public pages and unauthenticated JSON only. No login, follow, copy, subscribe or cost. Benzaquen was touched only to read the outbox and inbox, for de-dup.

## Verdict
- **No candidate is a clean GO.** Each one fails or cannot yet be scored on a soft screen: replicability (tickets), hard SL, swap, or grid.
- **5 candidates pass hard bars H1-H6** as frozen. TycheCerf is the strongest. The other four are new MQL5 ids, and each needs a ticket export before the replicability, hard-SL, median-hold and grid checks can run.
- **The bar is realistic, but only for small books.** All five shortlist books together hold well under $200k of real equity. Each would need $70k-$210k to contribute $300/day at its headline rate.

## Coverage
- **MQL5 Signals:**
  - Full logged-out listing: MT5 53 pages and MT4 29 pages, so **3,902 listed signals**.
  - On listing stats, 49 pass H1 (≥78 weeks), H2 (honest ≥3%/mo) and H3 (DD ≤25%).
  - **33 of the 49 were already in our prior rounds** (1,698 ids seen on the box) or in closed families: Kuropatkin/Solnce/QuantumStar/SolarFlare, Gold Reaper, CAZADOR, Happy/Rajcher, Harmonizer, LazyPro, Smart Owl, UpEverest, VG, Soren Voyager, BAS, and others. They were skipped.
  - **16 new ids** were pulled: the full public page, the W1 growth series (balance-based), stats, symbols and author siblings.
- **CopyFX:** the t253 census (5,022 listed, 1,340 aged, 14.11) is 5 days old, so I did not repeat it. I refreshed its passer and its 3 near-misses through the same public API (getAccountStats plus the daily profit_percent curve).
- **Myfxbook, FXBlue, Darwinex, Zulu, SignalStart, Binance, OKX:** mined in t202-t256 (see t256: "a further leaderboard round is a waste of quota"). Not repeated, and no new public lead surfaced in passing.

## Method notes
- **Honest monthly:** r_m = (1+G)^(1/months) - 1. G is the MQL5 page Growth or the CopyFX official TWR. Months are MQL5 weeks × 7/30.4375, or the CopyFX registration-to-last-point span.
- **DD:** max of equity DD, balance DD and curve DD.
- **Monthly table:**
  - MQL5: built from the W1 growth series. It is balance-based, so floating loss shows only in the equity DD.
  - CopyFX: built from the daily TWR.
- **H6 concentration:** CopyFX uses the top 10 days. MQL5 has no daily data, so the frozen proxy is best month <35% of log-growth. I **also** report top-10 *weeks*. ≥50% is a red flag and not a fail, because the PREREG did not freeze it.
- **Cost S1:** gold, EURUSD and GBPUSD are ≤0.02%/side at RF. AUDCAD, NZDCAD and AUDNZD are borderline (~2 pips ≈ 0.02-0.03%).
- **Replicability S2, hard SL S5, median hold S4, swap S3:** these need tickets, so they are UNKNOWN unless stated. The MQL5 "Avg holding time" is a mean and is used as a proxy only.

## Capital for $300/day
C = 300 × 21 / r_m = 6,300 / r_m. C' uses a 50% haircut on r_m (copy slippage, regime decay): C' = 12,600 / r_m.

## Shortlist (ranked: concentration, then DD, then monthly)

| # | Book | Link | Age | Honest %/mo | Max DD | Neg months (worst) | Last 12m | Top-10 share | C ($300/day) | C' (50% haircut) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | TycheCerf (CopyFX, MT4 cent) | https://roboforex.com/copy-trading/rating/aaap/47104691/ | 34.9 mo | **8.94%** (residual w/o top-10 days 5.29%) | 19.37% (getDdMax; curve −15.28%) | 2/31 (−4.7%, 2025-02) | +58.3% | 39.7% days | $70,470 | $140,940 |
| 2 | Van PM (MQL5 2391620, MT5) | https://www.mql5.com/en/signals/2391620 | 24.6 mo | **4.18%** | 9.95% (bal; eq 6.05%) | 3/26 (−5.58%, 2026-07) | +117.5% | 59.0% weeks (flag); best month 19.3% | $150,816 | $301,632 |
| 3 | EU Zone Arsenal (MQL5 2385553, MT4) | https://www.mql5.com/en/signals/2385553 | 23.5 mo | **3.49%** | 12.82% (eq; bal 8.55%) | 0/23 (worst +0.26%) | +35.9% | 47.3% weeks; best month 12.9% | $180,533 | $361,066 |
| 4 | Gold EA Stop Loss No Martingale (MQL5 2394167, MT4) | https://www.mql5.com/en/signals/2394167 | 27.4 mo | **3.66%** | 23.36% (bal; curve −18.45%) | 7/28 (−13.82%, 2026-10) | +83.9% | 78.0% weeks (flag); best month 34.4% | $172,004 | $344,008 |
| 5 | Stable Sky (MQL5 2373216, MT4), flagged | https://www.mql5.com/en/signals/2373216 | 28.7 mo | **3.83%** | 14.41% (eq; bal 3.63%) | 0/30 (worst +1.16%) | +43.7% | 30.2% weeks; best month 8.0% | $164,662 | $329,324 |

### 1. TycheCerf, `aaap/47104691`: the strongest stats, the weakest copy path
- **Style:**
  - EURUSD scalping and intraday: 319 of 341 deals, plus GBPUSD and 2 BTC.
  - MT4 ProCent, 1:2000.
  - 10% weekly fee, 8 copiers today (6 at t253).
- **Cost and swap:** EURUSD is ≤0.02%/side. Swap is likely small (intraday).
- **Red flags:**
  - **Ten consecutive 0.00% months (2025-10 to 2026-07).** The last 12 months are a restart: Sep +20.9%, Oct +29.4%.
  - Cent book: $10 start, $206 now.
  - No `company_client_id`, so siblings are untestable.
  - No public tickets and no MQL5 twin (t253 search).
  - "Scalping" on 1:2000 means replicability cannot be scored.
  - 4 months missing in 2024.
- **Next step:** none on MQL5. A CopyFX ticket list needs login, and that is not authorised.

### 2. Van PM, MQL5 2391620 (Mira Hardani, PrimeCodex-MT5)
- **Style:** multi-symbol: AUDCAD 886, XAUUSD 594, EURUSD 447 deals, plus NZDCAD, USDCAD and GBPUSD. 2,093 trades, average hold ~1 day, algo 83%, PF 1.51, win 66%.
- **Cost and swap:** gold and EURUSD are OK. AUDCAD, the largest share, is borderline on cost. Holds of ~1 day mean swap is likely small but not zero.
- **Red flags:**
  - **Trades per week = 0 now.** The last weekly point is 2026-11-06.
  - Withdrawals of $35.9k against $50k initial. TWR handles this.
  - Worst single trade −$5,921 versus best +$3,497.
  - The MQL5 pips figure is unusable (149,881 per trade), which suggests an index or crypto symbol in the mix.
  - MQL5 listing date 2026-09-16: the history is imported.
  - Sibling Fushion Gama: young, DD 6%.

### 3. EU Zone Arsenal, MQL5 2385553 (FortunePrime, €79/mo)
- **Style:** majors and EUR crosses: GBPUSD 298, EURJPY 268, EURUSD 213, then EURAUD, EURGBP, EURCHF, EURNZD. 947 trades, average hold 3 days, algo 99%, PF 1.71.
- **Cost and swap:** cost is OK (majors). Swap is a real question with 3-day holds.
- **Red flags:**
  - Zero negative months, plus average loss 1.76× average win, 50 consecutive wins, and equity DD above balance DD. Together this looks like **hold-losers or a basket**, and must be checked on tickets.
  - Honest 3.49% is just under the old 3.5% flag but above the 3.0% mandate.
  - Sibling Australian Arsenal 2385551: DD 10%, OK.

### 4. Gold EA Stop Loss No Martingale, MQL5 2394167 (Ajaya Pokhrel, IC Markets)
- **Style:** XAUUSD 687 of 816 trades, plus GBPCAD and USDJPY. Average hold 2 h, algo 97%. The vendor states SL and no martingale.
- **Size of move:** the net MQL5 pips per trade are ~743 points. That is ~$7.4 of gold move ≈ ~20 bp gross. It is likely to clear 10 bp after RF, **but this must be confirmed on tickets.**
- **Cost and swap:** cost is OK (gold, intraday) and swap is low.
- **Red flags:**
  - DD 23.36% is close to the cap.
  - **Oct 2026 −13.8%** (recent).
  - Top-10 weeks 78%.
  - Many deposits and withdrawals on a ~$1.3k account.
  - Siblings: Stop Loss Forex Trader DD 22%, and one young sibling. OK.

### 5. Stable Sky, MQL5 2373216 (Rallyville, $40/mo), flagged
- **Style:** NZDCAD 249, AUDNZD 133, AUDCAD 131. 513 trades, average hold 4 days, PF 4.34, load 3.5%.
- **Cost and swap:** cost is borderline (crosses). Swap is likely negative on 4-day holds.
- **Red flags:**
  - **The AUDCAD/NZDCAD/AUDNZD trio is the same pattern as the grid family we rejected** (Harmonizer, LazyPro, FX Fun). Equity DD is 4× balance DD.
  - **Inactive since ~09.2026:** 0 trades in the last month, and the series ends 2026-09-10.
  - Listed only since 2026-05-12.

## Near-misses and fails (full detail in t302_candidates.csv)

**Near-misses:**
- **Diamondhill** `aaac/72170338`: 9.65%/mo and DD 17.4%, but **top-10 days 60.3%** (fails H6). Residual 3.72%.
- **Blue Agressive CFDs Fiat FIC04** 2031876: 47.8 months, 3.05%, DD 14.4%. But last 12m is +1.2%, 14/44 negative months and top-10 weeks 82%.
- **Soft Chili** 2389887: 4.51%. Negative skew: average loss 5.2× average win, worst trade −$5.5k, 3-day gold holds, $5,000/mo price.
- **Dan old** 2382439: data gaps, load 32.5%.
- **HassTrader Relax** 2292609: top-10 weeks 98.7%, last 12m +8.4%.

**H4 grid suspects:**
- **Waka mas Fajar** 2400571: zero balance-curve DD on the cross trio, average win $2.17.
- **GemNanpin** 2319754: "Nanpin" means averaging down.

**Fails:**
- **H5 sibling:**
  - Algo Mind Moderate 2306648: sibling AlgoMind DayTrading, DD 48%.
  - GARYPRO2500 2350542: siblings at DD 71% and 44%.
  - Dudu 001 2361784 and Dudu Jolin 2351357: sibling Aircraft Carrier, DD 57%.
  - FX Fun 2355082: sibling DD 52%.
  - Oil for Mum 2 2383623: siblings at DD 79% and 58%.
  - JMao Lucky Cat: t253 sibling at −41.4%.
- **Residual:** VolantFX bbbb/7770061, 1.62% without the top-10 days.

## MQL5 history exports requested (read-only maestro_nb2026; Claude/parent to dispatch)
- **Priority:** 2391620 (Van PM), 2385553 (EU Zone Arsenal), 2394167 (Gold EA Stop Loss No Martingale), 2373216 (Stable Sky).
- **Optional:** 2031876 (Blue Agressive FIC04), 2389887 (Soft Chili).
- **What to run on them:** the t239/t241 gate. That means:
  - recost at RF (gold 10 bp, FX 4-5 pips, +1 pip/side stress);
  - median hold, SL coverage, max concurrent/averaging, swap/yr;
  - top-10 *days* and BD crash days;
  - unique-event match against GR, Solnce and Happy.

No trading recommendation; the decision is Nadav's.
