# SOURCES for BD_CRASH_SURVEY (accessed 17.11.2026, public, no login)
## Event 17.11.2026
- [V data] Dukascopy public datafeed, XAUUSD ticks 17.11.2026 hours 00–01, 06–20 UTC: https://datafeed.dukascopy.com/datafeed/XAUUSD/2026/10/17/HHh_ticks.bi5 (month 0-indexed). DXY (DOLLARIDXUSD) and USTBONDTRUSD hours were refused (429/503/TLS), so they weren't used.
- [S] Kitco, "Gold price drops to $3,848/oz after … retail sales rise 0.2%, core rises 0.6%": https://www.kitco.com/news/article/2026-11-17/gold-price-drops-3848oz-after-september-retail-sales-rise-02-core-rises-06
- [S] Kitco AM report 17.11: https://www.kitco.com/news/article/2026-11-17/gold-trades-near-one-year-low-us-retail-sales-slow-kitco-am-report
- [S] FXStreet (J. Gibson) 17.11 19:01 GMT, "Gold recovers its retail sales drop…": https://www.fxstreet.com/news/gold-recovers-its-retail-sales-drop-and-holds-above-mondays-low-202611171901
- [S] investinglive (A. Button), "US October advance retail sales +0.2% vs +0.2% expected": https://investinglive.com/news/us-october-advance-retail-sales-0-2-vs-0-2-expected/
- [S] ING THINK snap: https://think.ing.com/snaps/us-retail-sales-and-manufacturing-suggests-strong-momentum/
- [S] Investing.com (consensus +0.1%): https://www.investing.com/news/economic-indicators/retail-sales-edge-up-slightly-exceeding-forecasts-93CH-5032977
- [S] ABA Banking Journal: https://bankingjournal.aba.com/2026/11/aba-databank-retail-sales-rose-in-october/
- [S] FinScans, "Dollar Index slips to 103.40 as industrial production falls 0.4%": https://finscans.com/news/2026/11/17/dollar-index-slips-to-10340-as-industrial-production-falls
- [S] CNBC 17.11: https://www.cnbc.com/2026/11/17/gold-hovers-near-over-one-year-low-as-firm-dollar-fed-hike-bets-weigh.html
- [S] Euronews, US strikes on Qeshm: https://www.euronews.com/2026/11/17/us-strikes-targets-in-qeshm-island-after-iranian-mines-hit-five-ships-in-hormuz
- [S] Euronews, gold/silver lowest in over a year: https://www.euronews.com/2026/11/17/why-gold-and-silver-prices-have-fallen-to-their-lowest-in-over-a-year
- [S] Federal Reserve G.17 (IP release 17.11.2026): https://www.federalreserve.gov/releases/G17/20261117/default.htm
## Historical data
- [V data, third-party mirror] kevingtlin/dukascopy_XAUUSD_1m_Data (Dukascopy M1 bid via dukascopy-node, UTC, to 19.10.2026): https://github.com/kevingtlin/dukascopy_XAUUSD_1m_Data
## Protection mechanisms
- [V] Taranto & Khan (2020), "Gambler's ruin problem and bi-directional grid constrained trading and investment strategies", Investment Management and Financial Innovations: https://businessperspectives.org/images/pdf/applications/publishing/templates/article/assets/13892/IMFI_2020_03_Taranto.pdf
- [S] Taranto & Khan, drawdown/drawup of BGC processes, J. Math. & Stat.: https://research.usq.edu.au/download/47714f47433a88f73275c6c6eec97917d6c2c2765765baf58e44ce1cb06762fd/1986504/jmssp.2020.182.197.pdf
- [S] Rundo et al. (2019), "Grid Trading System Robot (GTSbot)", Applied Sciences 9(9):1796: https://doi.org/10.3390/app9091796
- [V abstract] Smales & Yang (2015), IRFA 41:292-302: https://ideas.repec.org/a/eee/finana/v41y2015icp292-302.html
- [S] Elder, Miao & Ramchander (2012), "Impact of macroeconomic news on metal futures", J. Banking & Finance: https://www.sciencedirect.com/science/article/abs/pii/S0378426611001968
- [V abstract] Harvey et al. (2018), "The Impact of Volatility Targeting", JPM / SSRN 3175538: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3175538
- [V abstract] Cederburg, O'Doherty, Wang & Yan (2020), "On the performance of volatility-managed portfolios", JFE: https://www.sciencedirect.com/science/article/pii/S0304405X2030132X
- [V, cited as standard] Andersen & Bollerslev (1997), "Intraday periodicity and volatility persistence in financial markets", J. Empirical Finance 4:115-158.
- [S] Midas Grid, "How to protect a martingale grid bot on gold: 7 protections" (model on Dukascopy XAUUSD ticks 1/2025–10/2026): https://midasgrid.com/blog/how-to-protect-martingale-grid-bot-gold.html ; methodology: https://midasgrid.com/methodology.html
- [U] axiscoretech, "Can you fix a martingale? 15-year AUD/CAD": https://axiscoretech.com/blog/trading-systems/martingale-absolute-audcad/
- [U] MQL5 article 22677 (RSI divergence grid + risk manager): https://www.mql5.com/en/articles/22677
- [U] MQL5 article 21833 (research-grounded grid EA, Taranto): https://www.mql5.com/en/articles/21833
- [U] MQL5 Code Base 78206, GridPro Panel (min interval between orders, caps): https://www.mql5.com/en/code/78206
- [U] MQL5 Market 178855, EA Phoenix Apex (ATR Risk Stop): https://www.mql5.com/en/market/product/178855
- [U] MQL5 Market 160644, Fintech Grid (Equity Guard): https://www.mql5.com/en/market/product/160644
- [U] FlexHedgePro user guide (hedge lock + recovery grid): https://www.easafetyscore.com/docs/flexhedgepro
- [U] Nordman Algorithms, "Grid EA: average price, exposure and risk": https://www.nordman-algorithms.com/blog/grid-ea/
- [U] Reddit r/Forex anecdote: https://www.reddit.com/r/Forex/comments/1qceoj5/finally_coded_a_logic_that_doesnt_suicide_short/
## Internal (read-only, Benzaquen)
- docs/BD_CLONE.md, docs/BD_EVERYYEAR_PLAN.md (rounds 1–3), docs/SCAN_PLAN.md (rounds 23, 74, 76, 90), docs/HANDOFF.md, frozen/bd_v7_d24ntop_20261026/ (README, .set, DragonClone_v7.mq5 CrashNow(), news_top_rf.txt).
