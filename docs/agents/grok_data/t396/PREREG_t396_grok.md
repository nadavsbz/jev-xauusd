# PREREG_t396_grok — measurement plan for t396 (Grok)
Written 25.11.2026 ~16:45 Asia/Jerusalem, BEFORE any per-run computation by Grok.
Disclosure: Claude's outbox 25.11 16:30 already listed raw tester net per run and summary.json (net, tester eq-DD, quality) was read to locate inputs. No equity reconstruction, floor events, cut metric, crash-day table or gate evaluation had been computed when this plan was written.

## Frozen inputs
- docs/prereg/research_t396.md (Claude, frozen 15:15; addendum per Grok critique 15:35, commit a82f613).
- docs/agents/grok_data/t396_tester/{2022..2026}_b{20,50}.csv.gz + summary.json (commit c2900b5).

## Frozen gate (restated, all on the 5 periods together)
1. Floor events: b20 <= 0.7 x b50. If b50 total < 5 -> condition 1 = INCONCLUSIVE (not PASS).
2. Total net: b20 >= 0.9 x b50.
3. Worst max equity DD: b20 <= b50.
4. Years: in >= 3 of 5 periods, net b20 >= net b50 - 2pp (pp of deposit).
Addendum: b20 = perfect FIRST-ENTRY gate only (adds not blocked). Any year with real-tick quality < 90% is excluded from cond. 4 and totals. Secondary (NOT gate): net-with-cut. 2026 crash-day table (21.4, 23.4, 30.4, 1.5, 5.6). P2 spread when b20 blocked.
PASS = all 4 pass. FAIL = any condition fails. INCONCLUSIVE = no condition fails but cond. 1 is inconclusive.
If FAIL: per research_t396 the family "entry spread limit" closes.

## Measurement definitions (Grok)
- Units: % of deposit (120,000 = 100). Equity E = 100 + realized + floating + swap + commission.
- Equity reconstruction (t389/t390 machinery): deals are normalized (vol_per_100k, K=0.1 %/(lot-per-100k * $1)). Positions valued per M1 bar: longs at Dukascopy BID, shorts at Dukascopy ASK (M1 ask file; if ask missing, bid + median spread of that day / overall). Price basis RF-Duk estimated per year from the run's own entry fills (median of sell-in price - Duk bid close and buy-in price - Duk ask close in the fill minute, pooled). Server time = Europe/Athens -> UTC. Deals take effect from the next M1 bar. Bar low-equity = min(equity at bar low, equity at bar high) (worst case of the bar).
- Period: from the period's start (1 Jan 00:00 server; 2026: 1 Jan) to the last deal of the run (2022/2026: year end; stop-out runs: stop-out deal).
- Stop-out moment: timestamp of the tester deals with comment "so ..." (OBSERVED from file). Floor events, DD, worst days counted only up to and including the stop-out moment. After stop-out = no trading (no data).
- Floor events (PROT-ABS-85 virtual): resets every 7 days anchored at period start; floor = 0.85 x E_close at the reset bar (equity at bar close prices). Event = first bar in that week with low-equity <= floor. At most one per week. No cut in the primary count (position continues).
- Net (1): sum(profit+swap+commission) of deals, % of deposit = tester net (primary, raw, may be < -100% because tester allows negative balance). Sensitivity (not gate): capped at -100% (negative-balance protection).
- Max equity DD (3): max over bars of (running peak of E_close - E_low)/running peak, %. Primary = M1 reconstruction; tester-report DD% (summary.json) shown as cross-check. If the two disagree on cond. 3 direction, report both and mark cond. 3 by primary with a flag.
- Worst 5 days (4): daily change of E_close (server calendar day, last bar of day vs previous day's last bar), pp of deposit.
- First entries / adds (5): per side, an episode starts with an 'in' deal when that side's open volume is 0 (first entry); other 'in' deals of the episode = adds.
- Tick quality (6): from summary.json.
- Net-with-cut (secondary, NOT gate): PROT-ABS-85 with 7-day reset anchored at period start; floor = 0.85 x equity at reset; first event per week. At the event the loss is realized AT THE FLOOR (E := floor), all positions closed, rest of the week skipped; resume at the next reset with the reduced equity; fixed lot unchanged (deals are not rescaled). After resume only episodes whose first entry is >= resume time are counted (ASSUMED: the bot restarts flat and its subsequent baskets match the tester's new baskets; path dependence ignored). Floor at each subsequent reset = 0.85 x cut-path equity. For stop-out runs, the cut path is only observable up to the tester's stop-out moment (no tester deals after it) -> cut net reported "to horizon" and marked truncated; nothing after the horizon is extrapolated.
- 2026 crash-day table: for each date (server day) 21.4, 23.4, 30.4, 1.5, 5.6: number of first entries by b20 and b50 that day, did b20 enter (yes/no), day PnL (E_close change) each arm.
- P2 (if cheap): b50 first entries with no b20 first entry within +-5 min = "blocked by b20" (ASSUMED proxy); report Duk spread (ask-bid close) at that minute and hour-of-day distribution, vs spread at b20 entries. Duk spread != RF spread (caveat).
- Tags: VERIFIED (recomputed and cross-checked), OBSERVED (read from data), ASSUMED, UNKNOWN.
