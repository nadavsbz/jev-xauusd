# PREREG t302 - second return engine (not BD, not Bull)

Written and hashed 2026-11-19 ~22:10 Asia/Jerusalem (UTC+2), BEFORE any t302 data pull.
Requester: Claude, claude_outbox.md entry 19.11.2026 21:35 ("t302, ברקע").
Scope: public pages / unauthenticated JSON only (WebSearch, WebFetch, curl). No login, no follow/copy/subscribe/rent/buy/invest, no accounts, no costs.

## Sources (in this order)
1. MQL5 Signals public listing pages (MT5 and MT4), logged out; individual public signal pages for stats.
2. RoboForex CopyFX public rating API (same logged-out `api/copy/*` surface as t253); refresh of t253 aged universe and its passer / near-misses.
3. Well-known public investor/verified accounts (Myfxbook, FXBlue, Darwinex) where public pages load without login.

## De-dup (applied before scoring)
- Any MQL5 id already present in /workspace/research_new_component, /workspace/claude_bridge, /workspace/grok_bridge, /workspace/t2xx (1,698 ids at pre-registration) is EXCLUDED unless it was a passer/near-miss that was never rejected (then it may be re-listed and marked "known").
- Closed families stay closed: Gold Reaper / Profalgo and derivatives, Solnce/Kuropatkin (incl. QuantumStar), SARUJA, EdgeTrader, Happy-author family, CAZADOR, S1, Kenni, Harmonizer grid, Black Dragon, Bull/Ofer.

## Hard bars (frozen)
H1 Age: track >= 18.0 months (MQL5: weeks >= 78; CopyFX: earlier of registration and curve start).
H2 Honest monthly: r_m = (1+G)^(1/months) - 1 >= 3.0%, G = platform cash-flow-neutral growth (MQL5 "Growth", CopyFX official TWR). Headline/simple averages are not used.
H3 DD: max(equity DD, balance DD, curve DD) <= 25%.
H4 No martingale / uncapped grid: FAIL if description or stats show lot escalation after losses or open-ended averaging; MQL5 "Max deposit load" > 60% is a FLAG; author-declared grid with no cap is FAIL.
H5 Sibling collapse: FAIL if a visible sibling signal/book of the same author has DD > 40% (or is dead/blown).
H6 Concentration: where daily data exists, top-10 days < 50% of log-growth; where only monthly data exists, best single month < 35% of total log-growth (proxy, marked as such).

## Soft screens (scored, reported; failing = red flag, not auto-reject unless stated)
S1 Cost: intraday cost <= 0.02% per side is a property of the instrument at RF (gold/indices/majors pass); exotic/crosses flagged.
S2 Replicability after RF costs: avg net per trade >= 10 bp on gold, >= 4-5 pips on FX. Only computable from a ticket export or a published pips figure; else UNKNOWN -> MQL5 export request.
S3 Swap <= ~5%/yr of equity: estimate from average hold (< 1 day => pass), else from swap total if published.
S4 Median hold >= 15 min: MQL5 average holding time used as proxy (mean, not median; marked).
S5 Hard SL: only from tickets; UNKNOWN unless export or explicit vendor statement.
S6 Negative months: count and worst month from the platform's monthly table.

## Ranking
Among H1-H6 passers: rank by residual robustness (concentration, then DD, then honest monthly). If fewer than 3 pass, fill the 3-5 list with the closest near-misses, clearly labelled with their failing bar.

## Capital for $300/day
C = (300 USD x 21 trading days) / r_m = 6,300 / r_m  (r_m = honest monthly as a fraction).
Also reported with a haircut r_m' = r_m x 0.5 (copy slippage / regime decay): C' = 6,300 / r_m'.
No trading recommendation; the decision is Nadav's.
