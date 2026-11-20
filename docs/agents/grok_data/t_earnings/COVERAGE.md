# t_earnings — point-in-time US earnings announcement dates (EDGAR 8-K Item 2.02)

Built 17.11.2026 for Claude's 20:05 request (pre-earnings premium, t281 idea 5).
Public SEC sources only. No sign-up, no paid data, no Alpaca key.

## Output
- `earnings_pit.csv.gz` — one row per 8-K / 8-K/A whose `items` field contains Item 2.02.
- `stats.json` — machine-readable coverage.
- `build_earnings_pit.py` — the builder (index → fetch → build).

## Sources [VERIFIED]
- EDGAR full-index `form.idx`, 2014Q1–2026Q4, used only to list every CIK that filed an 8-K or 8-K/A.
- Per-CIK submissions API: `https://data.sec.gov/submissions/CIK##########.json`, including overflow `files[]` whose `filingTo >= 2014-01-01`.
- Current ticker map: `https://www.sec.gov/files/company_tickers.json` (10,400 tickers on 17.11.2026), then the submissions `tickers[]` array as fallback.
- Fair access: generic User-Agent (`GrokBot-research earnings-pit-builder research-contact@example.org`), ≤ 8 req/s.
- The bulk file `submissions.zip` returned HTTP 403 (“temporarily unavailable / maintenance”) on 17.11.2026, so the per-CIK route was used instead. All 16,000 8-K CIKs were fetched; 0 failures.

Acceptance timestamps: the JSON field `acceptanceDateTime` ends in `Z` and is true UTC (spot-checked against the SGML `<ACCEPTANCE-DATETIME>` header of an AAPL 8-K). Converted to `America/New_York`.

## Timing rule (fixed)
- `before_open` if NY time < 09:30
- `after_close` if NY time ≥ 16:00
- `during_market` otherwise

Among original (non-amendment) filings: after_close 55.57%, before_open 35.09%, during_market 9.34%. Weekend share of acceptance dates: 0.00%.

## Expected-date proxy (no look-ahead)
For each original 2.02 filing of a CIK, look only at earlier original 2.02 filings of the **same CIK**. Take the one whose lag is in [320, 410] days (same fiscal quarter, one year back, ±45 days; if several, the lag closest to 365). `expected_date_proxy` = that prior announcement’s NY date plus one calendar year.

- 84.07% of all original rows have a proxy (2014 is almost empty, as expected; from 2015 onward the yearly share is 86–93%).
- Error vs actual `accept_date_ny`: median signed −1 day, mean signed −0.68, median absolute 2 days, mean absolute 4.12, p90 absolute 9 days.
- Within 1 / 7 / 14 days: 44.91% / 86.83% / 94.47%.

This is a date-of-announcement proxy, not an analyst “confirm date”. Companies that skip a quarter, change fiscal year, or IPO mid-sample will have a missing or off proxy. Mid-quarter 2.02s (flag `likely_dup_or_nonearnings` = 1 when the previous 2.02 of the same CIK is < 30 days earlier) should be treated with care: they are often pre-announcements, updates, or corrections, not the regular quarterly print.

## Coverage by year

| year | filings | originals | amendments | unique CIKs | share with current ticker | share with proxy | before_open | during_market | after_close | likely_dup |
|-----:|--------:|----------:|-----------:|------------:|--------------------------:|-----------------:|------------:|--------------:|------------:|-----------:|
| 2014 | 18,697 | 18,508 | 189 | 4,664 | 0.4746 | 0.0020 | 5,937 | 3,156 | 9,604 | 1,297 |
| 2015 | 18,773 | 18,621 | 152 | 4,683 | 0.4994 | 0.8913 | 6,163 | 2,802 | 9,808 | 1,296 |
| 2016 | 18,172 | 18,007 | 165 | 4,476 | 0.5334 | 0.9132 | 5,988 | 2,469 | 9,715 | 1,273 |
| 2017 | 17,710 | 17,561 | 149 | 4,352 | 0.5708 | 0.9123 | 5,941 | 2,097 | 9,672 | 1,240 |
| 2018 | 17,497 | 17,314 | 183 | 4,305 | 0.6088 | 0.9056 | 5,969 | 1,891 | 9,637 | 1,115 |
| 2019 | 17,095 | 16,941 | 154 | 4,244 | 0.6471 | 0.9111 | 5,891 | 1,620 | 9,584 | 987 |
| 2020 | 17,648 | 17,484 | 164 | 4,239 | 0.6821 | 0.9096 | 6,228 | 1,503 | 9,917 | 1,450 |
| 2021 | 18,396 | 18,227 | 169 | 4,609 | 0.7118 | 0.8593 | 6,494 | 1,401 | 10,501 | 1,191 |
| 2022 | 18,871 | 18,693 | 178 | 4,601 | 0.7467 | 0.8798 | 6,666 | 1,251 | 10,954 | 1,076 |
| 2023 | 18,328 | 18,171 | 157 | 4,484 | 0.7907 | 0.9301 | 6,589 | 1,148 | 10,591 | 1,112 |
| 2024 | 17,569 | 17,421 | 148 | 4,309 | 0.8492 | 0.9253 | 6,542 | 954 | 10,073 | 977 |
| 2025 | 16,952 | 16,824 | 128 | 4,193 | 0.9079 | 0.9263 | 6,417 | 871 | 9,664 | 894 |
| 2026 | 16,054 | 15,959 | 95 | 4,079 | 0.9670 | 0.9178 | 6,191 | 753 | 9,110 | 785 |
| **all** | **231,762** | | | **8,068** | | | | | | |

2014 is kept in the file so that 2015 rows have a prior-year anchor. The requested research window is 2015–2026. 2026 is year-to-date through 17.11.2026.

16,000 CIKs filed some 8-K in 2014–2026; 8,068 of them filed at least one Item 2.02. Unique CIKs per year (~4,200–4,700) line up with the listed US operating-company universe. AAPL (CIK 320193) has four 2.02 filings in every year 2014–2026 except 2015–2019 which have 4–5 (53 total), including overflow filings from before 2015-10.

## Columns
ticker, cik, company_name, exchange, sic, accession, form, is_amendment, items, filingDate, reportDate, acceptance_ts_ny, accept_date_ny, weekday_ny (Mon=0), timing, expected_date_proxy, prior_year_announce_date, prior_year_lag_days, days_since_prev_202, n_202_prev_365d, likely_dup_or_nonearnings, files_10q_10k.

`files_10q_10k` = 1 if that CIK also has at least one 10-Q/10-K in the fetched window (a light “is this an operating registrant?” flag).

## Caveats
1. **Ticker is current, not point-in-time.** Delisted / acquired / renamed names often have a blank ticker, which is why the ticker share rises from 47% in 2014 to 97% in 2026. **CIK is the point-in-time identifier.** For a CRSP/Compustat merge, join on CIK (or a PIT ticker map), not on `ticker`.
2. Foreign private issuers that report earnings on Form 6-K are **not** in this table (6-K has no Item 2.02). 20-F/40-F filers appear only if they also filed a domestic 8-K 2.02.
3. Item 2.02 can be used for non-quarterly updates. Use `likely_dup_or_nonearnings` and `n_202_prev_365d` (regular reporters are typically 3–5 in the prior year) to filter.
4. Amendments (8-K/A) are included and flagged; do not use them as a fresh announcement without looking at the original.
5. This is the **actual** announcement timestamp, which is what you need to score a pre-earnings trade after the fact. The proxy is the no-look-ahead stand-in for the **expected** date. It is not a company-issued calendar confirm date.
