# PREREG t371 — PROPOSED (not frozen): next search iteration "t372 forward-holdout watch"
Status: **PROPOSED** for Claude's review. Not frozen. Written 24.11.2026 ~19:30 IST.
Why this and not a trading-rule PREREG: no t371 candidate passed triage (see candidates.md), so there is no trade list to reverse-engineer. Following the standing rule that every FAIL queues the next pre-registered iteration, this PREREG targets the main weakness of all public-track-record hunting: **selection on past performance**. It does so with a forward, untouched holdout.

## Hypothesis
H1: among public MQL5 signals that already pass every numeric gate on history up to 24.11.2026 **or** will first reach 78 weeks before 24.05.2027, at least one non-grid, non-concentrated record keeps >=3%/mo honest return with equity DD <=25% on **forward data it has not yet produced**. Only a forward survivor goes on to trade-list rule extraction (t373+).

## Universe (frozen at freeze time)
- Snapshot: `list_parsed.csv` (3,769 public signals, crawl of 24.11.2026). sha256 ffa34faa16c65943797b28e8ee3b7d5fb2eba0f7e13a8950afa42f38b2d003cf.
- Eligible: weeks >= 52 on 24.11.2026, real account, list DD <= 25%, geometric monthly from growth >= 3%, not in `_prior_ids.txt` closed families (GR/Profalgo/Limitless/Solnce/EdgeTrader, Kenni, Happy*, TP TRADER, VAJJ, BTCBOT, Harmonizer, NoPain/UpEverest, LazyPro, Relevant-Trading blends, etc.), and no grid/martingale/averaging word in the description.
- Instruments: all-in cost <= 2 bp/side and swap <= ~5%/yr. FX majors and XAUUSD allowed; BTC and exotic CFDs excluded.

## Costs used in any later rule test (RoboForex)
- XAUUSD >= 10 bp per round trip per trade. FX 4–5 pips per trade. Real swap from the terminal spec (read-only), never 0.

## Splits
- DEV = everything up to 24.11.2026 (already seen; used only for eligibility, never as evidence).
- VAL = 25.11.2026 – 24.02.2027 forward (monthly re-crawl, read-only).
- HOLDOUT = 25.02.2027 – 24.05.2027 forward. **Untouched**: not looked at for any decision until VAL is closed and the VAL survivor list is frozen and hashed.

## Gates
- G0 (at freeze): eligibility as above; page shows no "80% of growth within N days" with N <= 30, and top-10 weeks < 50% of log growth.
- G1 (VAL): forward geometric monthly >= 3% (honest TWR from the MQL5 growth table); forward equity DD <= 15%; forward top-10 days or weeks < 50% of forward growth; no added grid/martingale evidence (deposit-load spikes > 3x the median, or equity DD > 2x balance DD in the window).
- G2 (HOLDOUT): the same as G1 on the holdout window, and cumulative (VAL + HOLDOUT) honest >= 3.5%/mo (Nadav's broader bar).
- Pass = G0 & G1 & G2. Only then a trade-list rule-extraction PREREG (entries/exits vs features), with its own DEV/VAL/HOLDOUT on price data and RoboForex costs.

## Early kill
- K1: any watched signal whose forward equity DD exceeds 10% within the first 6 weeks of VAL, or whose description or warnings change to grid, martingale or "no SL", is dropped immediately (logged, never re-admitted).
- K-program: if 0 signals survive G1 on 24.02.2027, close the MQL5-public domain and move to the fallback below.

## Fallback direction (queued, +1 trial family)
- Public Darwinex DARWINs whose "Trade distribution" is not hidden (underlying trades visible without log-in), with >= 18 months: extract entries/exits vs features directly from the public trade distribution. Same costs, gates and splits.

## Trial ledger
- t371: K_alpha = 0 (no backtest or rule test was run). Selection universe screened = 3,769 signals (selection-bias note for later DSR).
- Company cumulative N: last box snapshot N_alpha_cumulative = 2,549 (render 03.11.2026, old copy) [OBSERVED]. Current value UNKNOWN to me; Claude to fill from the ledger. t372 adds K = 1 (one watch family); a later rule test adds its own K.
