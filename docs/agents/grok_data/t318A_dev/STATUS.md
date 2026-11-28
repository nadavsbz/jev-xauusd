# t318A DEV 2016–2021 — סטטוס ריצה

- **הופעל:** 23.11.2026 21:51:53 שעון ישראל (IST), ב-box בלבד.
- **פקודה:** `cd /workspace/t318A_dev && setsid nohup bash code/run_dev.sh > run.log 2>&1 < /dev/null &`
- **PID:** ‏91723 (הופעל מחדש 21:58 IST אחרי תיקון זיכרון ב-s2_daily.py — רק אופן איסוף השורות, אותם נתונים; הריצה הראשונה, PID 88830, נעצרה ידנית באמצע s2 לפני שנכתב קובץ כלשהו) (‏`bash code/run_dev.sh`); כל שלב רץ כתהליך python בן (`pgrep -af "python -u s"`).
- **לוג:** `/workspace/t318A_dev/run.log`
- **שלבים:** s0_lists → s1_universe → s2_daily → s3_filter → s4_open → s4b_select → s5_full → s6_backtest → s7_coverage → s9_gates. כל שלב מדפיס `=== <שלב> <זמן>`.
- **כללים:** PREREG sha256 ‏5b3ca5a5…ddad + addendum1/2/3 בלבד; addendum4 נדחה (בלי שינוי phantom ובלי שינוי בר כניסה; השמרנית ראשית). asof='-' בכל משיכה. הנתונים עד 31.12.2021 בלבד (assert ב-cfg.py); VAL/HOLDOUT לא נפתחים. פרטי ביצוע: `EXEC_NOTE_DEV.md`; sha של הקוד וההערה לפני הריצה: `SHA256SUMS_pre_run.txt`.
- **מפתחות:** נטענים מ-`~/.secure/alpaca_paper.env` בתוך alp.py בלבד; לא מודפסים ולא נכתבים.

## איך יודעים שהסתיים
- בסוף `run.log` מופיעות השורות `ALL_DONE` ואז `END <תאריך>`.
- קבצי תוצאה: `out/results_t318A_DEV.json`, ‏`out/gates_DEV.json`, ‏`out/dq_summary.json`, ‏`out/coverage_delisted.json`, ‏`out/data_quality_symbol_days.csv`, ‏`out/trades_*_s2.csv.gz`.
- אם `pgrep -f run_dev.sh` ריק ואין `END` בלוג — הריצה נפלה (set -e); השגיאה בסוף run.log. כל השלבים idempotent לגבי משיכות (open5/full לפי יום), כך שהרצה חוזרת של אותה פקודה ממשיכה.
- הערכת זמן (ASSUMED): s2 ‏~15 דק', s4 ‏~45–90 דק', s5 ‏~20 דק', s6 ‏~10–30 דק'.

## אחרי הסיום (לא לפני)
- §8א: אם gross R של A0 (OR5m_a10) ≤0 → FAIL, ו-VAL/HOLDOUT לא רצים. `gates_DEV.json` → `family.kill_8a_A0_gross_le0`.
- G5 UNKNOWN (N חברתי) ⇒ אין PASS בלי N.

## עדכון 24.11.2026 08:26 IST
- ה-box אותחל בסביבות 05:20; s4_open נתקע מ-02:05 (0 CPU, sockets מתים) ב-1008 ימי open5 (עד 2020-01-03).
- הופסק (PID 91723/99413) והופעל המשך מ-s4_open: `code/run_resume.sh` (אותם שלבים וסדר, s0–s3 כבר הושלמו ולא רצו שוב), פלט נוסף ל-run.log. אין שינוי בקוד הניתוח או בכללים.
