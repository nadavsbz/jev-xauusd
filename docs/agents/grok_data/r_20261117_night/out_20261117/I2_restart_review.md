# Review: I2 restart guard (commits 7cabd8d + 523d9ef), mql5/IndexNoise.mq5. Grok, 17.11.2026 00:08 IST

**Source:** I ran `git fetch` (read-only) from origin into the box clone `/workspace/algotrade/jev-xauusd`. This review is of
`origin/feat/portfolio:mql5/IndexNoise.mq5` at 523d9ef, which is the commit after 7cabd8d. C1 (`mql5/CryptoTrend_C1.mq5`) has not
changed since 12.11. I did not compile or run anything in MT5. Benzaquen is offline, and the review doesn't touch any terminal or account.
**Tags:** VERIFIED = read in the code, or in the MQL5 docs (https://www.mql5.com/en/docs/runtime/running). HUNCH = inference that
still needs checking in the terminal or journal.

## What the code does now (VERIFIED, read)
```mql5
int OnInit() { ...  datetime b = iTime(_Symbol, PERIOD_H1, 0);
   if(b > 0 && TimeCurrent() - b >= 60) restartBar = b;  return INIT_SUCCEEDED; }
// OnTick, inside the check window, after the gap and session-left branches:
   int q = Want(d, j);
   if(b == restartBar) done = (Pos() == 0 || Pos() == q) || Flat();   // close if needed, never open
   else done = Go(q);
```
The per-tick time guard, exit bar, new day, gap and session-left branches all run before this branch and are not affected by it. That's correct.
The restart-bar branch does what it should: it holds when the position matches the signal, and flattens when the signal is 0 or the opposite side. It never opens or reverses. If the Flat fails, the bar is retried on the next tick. Q1 is answered correctly.

## P0

**P0-1. The decision is made in OnInit, which can run on stale or unsynced data at terminal cold start. In that case the guard is silently off in the 9.11 scenario.** (Mechanism VERIFIED from docs; whether it hit 9.11 is a HUNCH, check the journal.)
- **What the docs say (VERIFIED):**
  - The terminal gives an EA **at most 5 s** to synchronize, then starts it "with available data". With no connection to the server, it starts it anyway.
  - EAs are also **re-loaded on "connection to an account, even if the account number is the same"** when they were attached before authorization. So a cold start can produce two OnInit calls, both possibly before the first quote arrives.
- **What that means at a cold start (HUNCH):**
  - `TimeCurrent()` = time of the last quote the terminal knows, possibly from before the crash.
  - `iTime(H1,0)` = last bar in the local cache, possibly from before the crash.
- **Failure:** the crash happens at T0 in hour X, and the restart is in a later hour Y (9.11: restart 21:39). Then `restartBar` gets bar X, or nothing if `TimeCurrent()-b<60` or `b==0`. The first real tick builds bar Y, `b != restartBar`, and **the EA opens mid-bar, exactly as on 9.11**. The guard works only when the crash and the restart are in the same H1 bar, and the crash came ≥60 s after its open.
- **`b > 0` fails open:** if history isn't loaded (`iTime`=0), there's no guard at all.
- **The tester A/B can't see this.** In the tester OnInit always gets synced data. "Identical to the cent" proves no regression. It doesn't prove the guard protects.
- **To verify in the 9.11 journal:** the time of the last log line before the crash, the time of OnInit, and the time of the first tick or order.

**Fix (recommended): decide on ticks, not in OnInit. Use a stateless "first-seen lateness" per bar.** This covers restarts, reconnects and freezes in one rule.
It needs no OnInit logic, and the tester stays identical, because in the tester the first tick of each H1 bar comes at the bar open.
```mql5
input int LateSec = 60;                 // a bar first seen more than LateSec after its open is close-only
datetime seenBar = 0, lateBar = 0;      // globals; NOT relying on reset in OnInit (see P2-1)

// in OnTick, right after: datetime b = iTime(_Symbol, PERIOD_H1, 0); if(b == lastBar) return;
   if(b <= 0) return;                                                 // no bar yet: fail closed, retry next tick
   if(!MQLInfoInteger(MQL_TESTER) &&
      (!TerminalInfoInteger(TERMINAL_CONNECTED) || !SeriesInfoInteger(_Symbol, PERIOD_H1, SERIES_SYNCHRONIZED)))
      return;                                                         // history not synced yet: wait (the time guard above still closes)
   MqlTick tk; if(!SymbolInfoTick(_Symbol, tk) || tk.time < b) return; // the tick must belong to bar b (server time on both sides)
   if(b != seenBar) { seenBar = b; lateBar = (tk.time - b >= LateSec) ? b : 0;
                      if(lateBar == b) PrintFormat("I2 late bar %s first seen %s: close-only", TimeToString(b), TimeToString(tk.time)); }
// ... and in the check branch:
   if(b == lateBar) done = (Pos() == 0 || Pos() == q) || Flat();      // as now, with lateBar instead of restartBar
   else done = Go(q);
```
- `seenBar` is set on the first tick of the bar, so retries of failed orders on a bar first seen at its open are **not** blocked.
- Use the symbol's tick time (`SymbolInfoTick`), not `TimeCurrent()`. `TimeCurrent()` is the last quote of any Market Watch symbol (VERIFIED docs semantics). It's usually the same here, but the tick time is the exact one.
- The OnInit block can then be removed. Keep only `tr.SetExpertMagicNumber(Magic)`.
- **A/B must be re-run** in the tester (2025 and 1–17.11). It's expected to be identical, but that's a HUNCH until run.

## P1

**P1-1. A disconnect or freeze without a reload gives the same mid-bar entry, and the current fix doesn't cover it.** (VERIFIED from the code logic.)
- Example: internet drop or VPS freeze from 21:00 to 21:39, no restart.
- `restartBar` isn't touched, `b != lastBar` on the first tick at 21:39, and `Go(q)` opens mid-bar.
- The stateless rule in P0-1 covers this case. That's the main reason to prefer it over an OnInit flag.

**P1-2. The position is unmanaged while the PC or terminal is down.** (VERIFIED: the code has no SL or TP on the server. Positions survive a crash on the server.)
- If the PC is down at ExitHour (22, NY 16:00), the I2 position stays open overnight and over the weekend with no stop.
- The tick time guard closes it only once the terminal is back.
- **Options:**
  - A wide catastrophic SL sent with the order (e.g. 3–4× the day's noise band). It's almost never hit, so the tester impact is close to 0, but that must be A/B'd.
  - An external watchdog that alerts if the terminal is down during 16–22.
- **This changes live protection, so it's Nadav's decision.** I'm raising it, not proposing to implement it now.

## P2

**P2-1. Q2: reload paths and globals.**
- **Chart symbol/TF change:** VERIFIED from docs. The EA is not unloaded. OnDeinit and OnInit are called, **and global and static variables are NOT reset**.
  - `lastBar`, `sizedDay`, `dayLots` and `restartBar` survive. OnInit overwrites `restartBar` with the current bar if ≥60 s into it.
  - Usually harmless, because `lastBar == b` already and OnTick returns.
  - It changes behaviour only if the current bar was still being retried after a failed order. Then the open becomes blocked: a small divergence, toward safety.
  - The code uses hard-coded `PERIOD_H1` everywhere (VERIFIED), so the chart timeframe doesn't affect the signals.
  - A **symbol** change would trade another symbol with the same Magic. That's an operator error, not this fix's.
- **Input change (REASON_PARAMETERS):** the docs don't list it as unload or reload for EAs. HUNCH: globals also survive. Verify with `Print(lastBar, sizedDay)` in OnInit after changing an input.
  - Consequence: after changing `Lots` or `TargetVol` mid-day, `dayLots` is **not recomputed until the next day** (`sizedDay == d`). That's pre-existing, not from this fix.
  - Fix: in OnInit set `sizedDay = 0;` (sizing is recomputed from bars, so this is safe).
- **Template or profile change, recompile, terminal start, account connection:** VERIFIED that these are real unload/load. Globals are re-initialized, and the guard logic applies, subject to P0-1.
- **Suggestion:** add `void OnDeinit(const int reason){ PrintFormat("I2 deinit reason %d", reason); }` and a Print in OnInit of `TimeCurrent()`, `iTime(H1,0)` and `SERIES_SYNCHRONIZED`. Then the next incident can be diagnosed from the journal.

**P2-2. Q3: the 60 s threshold.**
- 60 s is fine for US500 at 16:00–22:00 server time (liquid; HUNCH for RF ticks). Anything from 60 to 300 s gives the same protection against a 39-minute-late entry.
- With the tick-based rule the threshold matters less, because only the first tick of a bar is measured. Make it an input (`LateSec`), default 60.
- Weekend or market closed: with the OnInit version, a Saturday load sets `restartBar` to Friday's last bar. That's harmless, because Monday's bars differ. The tick-based rule has no weekend case, since no ticks come in.
- Server time vs bar time: both are server time (VERIFIED: `iTime` and the tick time). Never use `TimeLocal()` or `TimeGMT()` here.

**P2-3. Restart-bar close uses `Want` of the bar that closed at its open.** That's the state the tester wanted for this bar, so it's correct.
- Sizing on a restart day is recomputed with equity at restart, which includes floating P/L, not at 16:00. That's a minor deviation.

## Q4: C1 (mql5/CryptoTrend_C1.mq5), recommendation: do NOT add the skip (VERIFIED code + reasoning)
- C1 recomputes a **target** from closed H6 bars at every new bar (path-independent, "restart-safe" by design). Positions persist on the server.
- A mid-bar restart either does nothing (the |Δ| is inside `RebalPct` or below a lot step), or moves late toward the target the tester already holds.
- Skipping would leave a **stale** exposure for up to 6 h, which is further from the tester than a late rebalance. For a slow trend ensemble (lookbacks 10–250 H6 bars), being late costs drift for minutes. Being wrong costs a 6 h stale position.
- C1 already waits for `SERIES_SYNCHRONIZED` live, and fails closed on `b==0` (VERIFIED). So the P0-1 stale-cache problem mostly doesn't bite there.
- **Residual:** `Targets()` checks sync for each symbol. But `iTime(sy[0], PERIOD_H6, 0)` could still be a cached old bar before the first tick. Then it would rebalance once on the old bar time, then again at the real bar. That's harmless: the same target, recomputed. (HUNCH.)
- **Optional P2:** the same OnInit/OnDeinit reason logging.

## Summary
| # | Severity | Finding | Tag |
|---|---|---|---|
| P0-1 | P0 | OnInit decision on stale or unsynced data at a cold start. The guard misses when the crash and the restart are in different H1 bars (the 9.11 pattern), and it fails open on iTime=0. The fix is first-seen-tick lateness in OnTick. | mechanism VERIFIED (docs); 9.11 applicability HUNCH, check the journal |
| P1-1 | P1 | A disconnect or freeze without a restart still enters mid-bar. Fixed by the same rule. | VERIFIED (logic) |
| P1-2 | P1 | No server-side protection while the PC is down; the 22:00 exit depends on the terminal. Nadav's decision. | VERIFIED (code) |
| P2-1 | P2 | Chart change keeps globals (docs). Input change probably too, so `dayLots` stays stale until the next day; reset `sizedDay` in OnInit. Add deinit/init logging. | VERIFIED / HUNCH |
| P2-2 | P2 | 60 s is fine; make it an input. | HUNCH (RF tick timing) |
| Q4 | — | C1 doesn't need the skip; a late rebalance is closer to the tester. | VERIFIED code + reasoning |
