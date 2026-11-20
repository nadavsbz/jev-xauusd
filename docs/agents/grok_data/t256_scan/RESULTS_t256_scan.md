# RESULTS t256 — new-angle web scan + OwnGold v2 idea list

Written 2026-11-15 ~10:40 Asia/Jerusalem (UTC+2). PREREG_t256.md sha256 e0f3a70e84eeccc3a69c7b029edc95f53e11791d13c84bb9c80cd0451665c1ab (hashed before any data pull).
Read-only, public pages / unauthenticated JSON only. No login, sign-up, follow, copy. Raw data in results_t256/raw, scripts + outputs in results_t256/analysis.

## Headline
**0 passers.** 1 numeric near-miss, which fails replicability: the Alpari PAMM **Harmonizer Mid Risk**, a known AUDCAD/NZDCAD grid. Two new crypto copy universes were mined and closed: Binance and OKX. Four published ideas were tested quickly on free hourly data, and none clears the 10 bp net-per-trade bar. Two ideas remain for Claude to test on RF ticks.

## A. Binance Copy Trading (new, public bapi JSON, 8,978 public lead portfolios)
- Crawled `home-page/query-list`, timeRange 365D, sorted by ROI, down to ROI 38%: 1,020 books. Of those, 364 had 365D ROI ≥42.6% (= 3%/month) **and** 365D MDD ≤25%.
- `lead-portfolio/detail` gives `startTime`. Only **17** of the 364 started on or before 2025-05-15, the 18-month cutoff.
- For each of the 17, pulled the 365D daily ROI chart, performance and full position history.
- Limitation: the public API shows at most 365D. History before that, and DD over the whole history, cannot be seen.
- **All 17 fail top-10 days.** Shares run 64%–186% of log-growth; most are ≥110%. Several have 1–5 trades a year.

| Book | Start | 12-month monthly | 365D DD | Top-10 share | Notes |
| --- | --- | --- | --- | --- | --- |
| YesItsAGreatStrategy | 2024-09 | 12.7% | −18.3% | 64% | HYPEUSDT only (not on RF), API bot |
| Quiet_Harbor_LowRisk | 2023-12 | 9.9% | — | 81% | 2 BTC trades |
| MoneyBoxTM | — | 5.9% | — | 114% | HYPE |
| Tradixor | — | 4.3% | — | 128% | — |

- Verdict: Binance is mined. Copy-crypto books are concentrated in a few trades, and many trade alt or HYPE perps that RF does not offer.

## B. OKX Copy Trading (new, public v5 API)
- `public-lead-traders` returns only 51 listed traders; 27 of them have leadDays ≥548.
- Best honest monthly: **Trader KS** (746 days, +119.65%, 3.26%/month, AUM ~$0.5M).
  - From `public-pnl` 365D: **curve DD −72%** (Jun 2026) and a −57% week (9 Nov 2026). **Fail.**
- Next best: Herzi, 2.23%/month. All others are <2.1%. Mined.

## C. Broker PAMM / social monitors
- **Alpari PAMM leaderboard:** JS app; no unauthenticated API found. Used the Oct-2026 snapshot (soodup.com) plus the matching public MQL5 signal pages.
- **Near-miss: Harmonizer Mid Risk PAMM** (Amir Hossein Moharreri, Alpari MT5). Alpari leaderboard "trading from 24 Nov 2024". https://www.mql5.com/en/signals/2388397
  - The MQL5 weekly growth series starts 2024-11-24. Age 23.7 months, growth 201.5%, so **4.77%/month**.
  - MQL5 relative equity DD 12.44% and balance DD 20.89%. Top-10 *weeks* 19% (weekly series only); residual 3.85%/month.
  - **Fails Claude's gate:**
    - Grid with lot escalation and basket exits; no hard SL.
    - Net ≈51 points ≈5.1 pips per trade on AUDCAD/NZDCAD crosses, about 2.5× RF cost against the 5× required.
    - Average hold is 3 days, so swaps apply; the Alpari PAMM appears swap-free.
    - The equity series exists only from 2026-08-26, when monitoring started, so floating DD before that is unknown.
    - The developer's own backtests show DD of 41% on the Mid preset and 82% on Extreme.
    - The family was already listed as a grid reject in t215, t232/t234 and PLATFORM_SCAN.
  - Siblings:
    - Extreme 2360068: weekly series from 2024-08, 13.4%/month, equity DD 22.42%, tiny account.
    - High Risk 2392781: 5.7 months, too young.
  - **Watch only; do not clone.**
- **Soarsup** (Vantage MT4, Myfxbook-verified, "+283% since 2022") ≈2.6–2.8%/month, below the floor. It sits on SignalStart, which is already mined.
- **Dead ends for the box:**
  - Exness social-trading host: no connect from the box (HTTP 000).
  - Bybit: Akamai 403.
  - Bitget: public rank path 404.
  - Reddit: 500 on both reddit.com and old.reddit. Only one mirror snapshot was readable: the StrategyQuant portfolio, 23.6% YTD with a sizing bug. It had no link and is not a candidate.
- Prop-firm leaderboards were skipped (horizons are too short to meet the 18-month age rule).

## D. OwnGold v2 ideas (published; checked quickly where free data allowed)
Free hourly data from data-api.binance.vision: BTCUSDT and PAXGUSDT (a gold proxy), 2020–2026-11. Script: analysis/ideas_oos.py, output in ideas_oos.txt.

**Rejected by our own quick out-of-sample checks:**
1. **Gold Asia session long, 00–08 UTC.** Sources: Wei SSRN 7257240 (2026); Donati & Jung, CBS 2019.
   - PAXG 2020–07/2024: +0.5 bp/trade. 2024-07 to 2026-11: +3.0 bp. 2026: +0.9 bp. A prior-US-session filter does not help.
   - Far below 10 bp. Reject.
2. **BTC 21–23 UTC long.** Source: Quantpedia 2022/2023.
   - 2020–21 in-sample: 12.4 bp. Post-publication 2022–06/2023: 2.0 bp. Out-of-sample 07/2023–11/2026: 6.1 bp. 2026: −1.8 bp.
   - Below the 5×-cost bar. Reject.
3. **Crypto Donchian ensemble.** Source: Zarattini, Pagani & Barbon, SSRN 5209907 (2025).
   - Our BTC approximation: 20%/yr up to 03/2025, then **−0.3%/yr after publication**. It is in the market ~80% of days, so many swap nights. It also belongs to the TSMOM family. Reject.
4. **Gold holiday drift.** Source: Quantpedia / SSRN 5384405 (2025). Only 2.3%/yr. Reject.

**Supporting negative evidence:** Krueger Algorithms (2026) replicated 7 published intraday rules on CFD minute data, 2015–2026, with a 2023–06/2026 holdout. Gross results are 1–3 bp, and none is net-positive after costs. The rules include Baltussen's last half hour, the overnight drift and Breedon-Ranaldo. The NY Fed's "Disappearing Overnight Drift" (2026) agrees. Conclusion: v2 must target moves of ≥30–100 bp per trade, not intraday seasonality.

**Still worth a Claude test on RF ticks (not checked here; needs index/oil data):**
- A. **Overnight-intraday reversal**: Liu, Liu, Wang, Zhou & Zhu, "Overnight-Intraday Reversal Everywhere", SSRN 2730304.
  - Futures CO-OC Sharpe: equity index 5.5, commodities 3.5.
  - Rule: buy at the cash open after a strongly negative overnight move (sell after a positive one), flat at the cash close. Intraday only, no swap. Run it as time-series on US500/USTECH/DE40/JP225/WTI/XAU CFDs.
  - Risks: the edge may be tiny on CFDs, as in Krueger's tests. It is related to the "overnight premium" Claude already tested, but it is a reversal and not the premium itself. Pre-register a floor of ≥10 bp net per trade.
- B. **Crude-oil EIA-Wednesday intraday momentum**: Wen, Indriawan, Lien & Xu, Energy Journal 44(4), 2023.
  - Rule: the sign of the 3rd half-hour after the 10:30 ET release predicts the last half-hour. One trade a week on the WTI CFD, no swap.
  - Risk: small per trade. Test with a ≥10 bp floor.

## Files
- PREREG_t256.md: e0f3a70e84eeccc3a69c7b029edc95f53e11791d13c84bb9c80cd0451665c1ab
- results_t256/analysis: binance_gate.json, mql5_growth.json, ideas_oos.txt, donchian_btc.txt, and the scripts.
