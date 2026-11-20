# shortlist_t205 — grids allowed, equity DD, 24+ months, Abs 4–5% target

See `RESULTS_t205.md` for mechanics, swap, 2020/2022 episodes, and the
`AUDCAD_ENV_GRID_T205` backtest. This file is the candidate list only.
Ages as of 12 Nov 2026 (Asia/Jerusalem, UTC+2).

## In-scope named books

| Rank | Name | Abs %/mo | Months | Equity / stated DD | Gain≈Abs | Non-gold? | Decodable? | Call |
|---|---|---|---|---|---|---|---|---|
| 1 | **Carla Mt4** 11509126 | **4.65%** | 45.5 | 26.59% (history private) | yes (760 vs 662) | yes (AUDCAD/NZDCAD/USDCAD) | **no** (private history) | Best live number. Missed 2020/2022. Cannot build. |
| 2 | **NoPain MT5** 11204017 | **~2.32%** (site 5.27% is Gain) | ~70 (analytics 2021–26) | **48.22%** Myfxbook; MQL5 20.63% incomplete | **no** (2236 vs 403) | yes (AUDCAD only) | family yes, exact `.set` no | Longest honest track. Below 4–5%. DD 48%. Used as the decoded family. |
| 3 | **HWRLFSL** 11390837 | **1.88%** (site 2.66% is Gain) | ~25 | 16.79% | Gain not printed; Abs 59.6% on $2,880 dep | **no** (gold is Best Symbol; also EURNZD/AUDJPY/USDCHF) | **no** (irregular steps, parallel lots, 52-trade sample) | Below target, gold in the book. |
| 4 | **AGM Accumulation** 1081311 | ~4.2–4.4% on MQL5 Growth, Abs UNKNOWN | 64+ (from Jul 2021) | **equity 65.55%** | UNKNOWN | mostly AUD crosses | accumulation grid | **FAIL equity tail.** |
| 5 | **News Catcher Pro** 1845908 | ~2.4% | ~45 | **equity 52.58%** | — | EUR majors (news), not a ranging-cross diversifier | news baskets | **FAIL return and tail.** |
| — | UpEverest / UpFuji | 4–6% claims | <24 mo or 2× NoPain | 14% (short) / 2× NoPain | — | AUDCAD | same family | FAIL age or duplicate. |

## Backtest of the only decodable family (proxy, not a clone)

`AUDCAD_ENV_GRID_T205`: Envelopes(20, 0.10%) + 20-pip step + 1.3× + 12-pip
TP + max 10 + RF Prime costs including swap, M15 2018–2026, $10k / 0.08 lot.

- Compound monthly **1.97%** (train 2.00%, holdout 1.93%).
- Max **equity DD −244%**, trough **−$19,350** on **19 Mar 2020, 03:45 IST**,
  after **−2,021 pips** of AUDCAD from 16 Mar 2018. Recovered 2 Jun 2020.
- 2022: **−60%** equity, 25 Feb 2021 → 28 Jan 2022, recovered 9 Dec 2022,
  **−1,064 pips**.
- RF 30% diagnostic would have **stopped out on 6 Apr 2018, 00:45 IST**
  at **$6,664**. The $81k ending equity is a zombie path.
- Closed-trade WR **100%** (6,174 baskets); losses are floating.
- At a 25% 2020-DD size: ~**0.2%/month**. FAIL 5%/25%.
- Gold monthly corr **−0.06**; 2020 trough **shares the COVID week** with
  a gold-trend crash. "Non-gold" ≠ automatic crash-day hedge vs BD.
- No MQL5. No second search.

## Not re-opened

t204 non-grid fails (ares, Calicut, R Factor, Ferrari, Gold Trade Pro,
fn-capital, Darwinex) and earlier failed families (gold S/R, goldfade,
London FX breakout, carry, BTC MR, NR7/ID, JLC news 1-min at 5%/25%
size) are unchanged. pr42 BD-on-AUDCAD is prior OBSERVED research on a
*different* EA and was not this PREREG.
