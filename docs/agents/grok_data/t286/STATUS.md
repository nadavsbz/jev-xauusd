# t286 - Bull Scalper 4.7 on Grok box - STATUS: BLOCKED (no demo file on box)
Checked: 18.11.2026 11:26-11:30 (Asia/Jerusalem). Executor: Grok.

## Result
- No `EA Bull Scalper*.ex5` exists under any `MQL5/Experts/Market/` on the box.
  - Searched: every Wine prefix on the box (`~/.mt5`, `/workspace/research_new_component/data/private/wine_t236`), every terminal folder
    (ENG_COMPILE*, MT5_EXP1, MT5_EXP34, MT5_JEV_GROK, MT5_PUPRIME, MT5_T236, MT5_DATAOPS), the AppData/Roaming/MetaQuotes data folders,
    every Downloads folder, and a full-filesystem search for any *.ex5 / *bull* / *116071* file modified after 08:45.
  - The only `Experts/Market` folder is `C:\MT5_JEV_GROK\MQL5\Experts\Market` (empty, mtime 18.11 08:41:45).
  - The only Bull Scalper binary on the box is our t285 read-only copy of the Benzaquen file:
    `/workspace/t285/ea/EA Bull Scalper.ex5`, 161,062 bytes, mtime 18.11 07:05:43, SHA256 fdfac122...4f05.
- MT5_JEV_GROK journal: no terminal has run since 08:44:40, and there are no Market download/install lines.
  The 08:30-08:44 relaunches were OUR t285 attempt to drive the Market WebView (cdp.py at 08:40; Market images cached 08:40:35-55).
  That attempt did not download anything.
- Important finding (tester log, 08:41:10):
  `"Market\EA Bull Scalper.ex5" X64 demo version` + `EA Bull Scalper invalid license (538), please reinstall from MQL5 Market`
  + `loading of C:\MT5_JEV_GROK\MQL5\Experts\Market\EA Bull Scalper.ex5 failed`.
  => The Benzaquen copy is ITSELF the Market demo build, and it is still hardware-bound (538) on another machine.
  [OBSERVED] So a demo downloaded on another machine will very likely not load here. The only way is a demo downloaded by a terminal
  ON the box, and the Market WebView does not render under Wine (t285).
- Version / 97 inputs: could not be checked. The tester never loads the EA (the input list comes only after a load), and the ex5 is encrypted
  (no version strings).

## Runs (prereg / 2% threshold / results format as in t285, unchanged)
| run | status |
|---|---|
| testbull4_w1 (match check) | NOT RUN - no loadable EA |
| new_profit_w1..w3 | NOT RUN - Claude must KEEP them in its queue |
| bull100_w1..w3 | NOT RUN - Claude must KEEP them in its queue |
No RESULTS file, so no SHA. Run definitions: D:\Claude\jev\research\bull\opt47\win\bull47opt_*_w{1,2,3}.json (unchanged).

## Credentials
- `secrets/grok_tester_investor.json` was NOT opened or used (no run was possible, so no login was needed). accounts.json was not opened.
- Box terminal MT5_JEV_GROK: no accounts.dat, and no Login/Server/Password lines in any ini (verified). There are no temp credential files.

## Processes
- No terminal64/metatester is running on the box. An idle wineserver + 2 winedevice (started 09:51, after t285 closed at 08:51)
  are not from t285, so I left them alone.

## Options (decision needed - nothing paid)
1. Nadav downloads the Free Demo on the box itself, from a terminal ON the box (the Market window under Wine does not render. A browser
   "Free Demo" link opens mql5buy:// which needs the terminal). Not currently possible without a working WebView.
2. Windows VM on the box: needs a Windows image/licence. Even an evaluation ISO needs a Microsoft download plus a KVM check. Not done (prohibited without approval).
3. Claude keeps all 9 runs on Benzaquen (current state).
