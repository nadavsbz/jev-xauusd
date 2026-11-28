# RESULTS t377: איזה set של BD רץ בכל חשבון ובאיזו תקופה
נכתב 24.11.2026 בסביבות 22:35 IST (Asia/Jerusalem). Grok, על ה-box בלבד. לא נגעתי ב-Benzaquen.
**read-only:** לא נשלח דבר ל-Telegram, לא בוצע log-in, ולא נפתח accounts.json. החשבונות מופיעים רק בכינוי (BD1..BD8; ‏BD4 = קובץ ההיסטוריה `BTC_Bot_4`, כמו ב-t376).
תגיות: VERIFIED = נקרא ישירות במקור. OBSERVED = חישוב שלי על ה-deals המקומיים. ASSUMED = הסקה. UNKNOWN = לא נמצא.
התאריכים הם בשעון השרת, לפי הכניסה הראשונה והאחרונה ב-deals. ההיסטוריה המקומית מסתיימת ב-26.10.2026.

## תשובה קצרה
- **26 תקופות BD ב-8 חשבונות.** ל-23 מהן יש שם set ידוע. 3 הן UNKNOWN. [OBSERVED]
  - **17 מתוך ה-23 מגובות בציטוט ישיר** מיומן ה-Excel של נדב, ואצל רובן גם magic ו-comment שזהים ל-set file. [VERIFIED]
  - **6 מבוססות על fingerprint בלבד:** ‏BD1 casper 10–11.2025, ‏BD2 Lars מ-24.08, שלוש תקופות TF של BD3, ו-BD5 באוקטובר. [OBSERVED]
  - **לשני sets יש שם ידוע אבל אין קובץ על ה-box:** ‏`1H_Rramil` (‏BD2) ו-`ea_black_dragon_mt5_stochastic_asian_xauusd_2digits_m5` (‏BD3). הפרמטרים שלהם UNKNOWN.
- **magic 5555 ‏("EA Black Dragon-Lars") הוא ה-set של Lars במימוש של נדב, ‏`algotrade/sets/bd.set`.** [VERIFIED + OBSERVED]
  - **ה-fingerprint תואם ל-bd.set ולא ל-Lars v2 המקורי:**
    - יחס לוטים 1.50 (ב-bd.set ‏Martin 1.5, ב-Lars v2 ‏1.35).
    - פער שני ≈ ‎$3.3–3.7 ‏(Fix 300 נק' עם overshoot של נר).
    - פער ברמה 6 ≈ ‎$2.0–2.3 ‏(Dyn 200 נק', לעומת 300 אצל Lars).
    - יציאה של סל ברמה אחת ב-~‎$0.7 ‏(trail ‏60/10).
    - TF ‏M15. שעות כניסה 2–20.
  - **הסט הזה רץ ב-7 חשבונות.** ב-BD7 הוא נרשם ב-Excel אבל לא סחר.
- **ה-sets האחרים שרצו:**
  - CasperIT Aggressive M1 (‏123654): ‏BD2, ‏BD6 ו-BD7, באפריל–מאי.
  - CasperIT Hybrid M1 (‏223344): ‏BD2, ‏07–15.04.
  - JPB 9-13 SL (‏1878943): ‏BD6, ‏09–24.06.
  - stoch_true (‏1111): ‏BD2, ‏06–08.2026.
  - stochastic_asian (‏1111): ‏BD3, ‏30.04–15.05.
  - 1H_Ramil (‏1111): ‏BD2, ‏01–17.06.
  - casper m1 5kstandard (‏1111, לפי fingerprint): ‏BD1, ‏30.10–10.11.2025.
- **התנגשויות בין ה-Excel לבין ה-deals (ה-deals גוברים לצורך הטסטר):**
  - **BD3 ‏09.06–30.07:** ה-Excel רושם 5M, אבל 100% מהכניסות שמיושרות לנר נופלות על minute%15 בערך מ-2,000 סלים. כלומר M15.
  - **BD2 מ-24.06:** ה-Excel רושם 1M, אבל הכניסות מיושרות ל-M5.
  - **BD2 ‏18–30.06 (‏magic 11111):** ה-Excel רושם stoch_true, אבל הגריד הוא ‎$3 ולא ‎$8. ‏[UNKNOWN]
  - **BD6 ‏7.5–29.5:** ב-Excel העמודות "רובוט" ו-"הגדרות" מוחלפות. ב-deals רץ 123654, כלומר CasperIT Aggressive.

## מקורות
- **יומן ה-Excel של נדב:** `algotrade/docs/manual_tracking.xlsx`.
  - בתוכן הוא זהה ל-`/workspace/track.xlsx` ול-`algotrade/bots/manual_report.xlsx` (‏mtime ‏23.11.2026).
  - זה המקור של `reports/adv2_reset_floors_from_excel.csv` ש-t376 השתמש בו.
  - הוא מכסה את 12.11.2025–16.07.2026, עם העמודות "רובוט / הגדרות / זמן נר / הערות".
  - חילצתי ל-`t377_excel_log_extract.csv` רק את העמודות האלה. בלי עמודות מספר חשבון או סיסמה, ומספרים של 6 ספרות ומעלה הוסתרו. [VERIFIED]
- **Telegram:** ה-handle של נדב הוא `nadavsbz`. מצאתי 44 הודעות שלו: 24 בקבוצה של Ramil ו-20 ב-export של Lars.
  - ‏**16.09.2025 #68777:** "Cents account today, thanks for @The_B33keeper for the set file and to Ramil for BDEA". [VERIFIED]
  - ‏**07.09.2025 #67374:** תגובה להמלצה של Lars: "I would increase the distance from 150 to 300, for dynamic distance as well 300. The Overlab I would change from 9 to 7". [VERIFIED]
  - בשאר ההודעות של נדב אין שם של set שהוא הריץ. [OBSERVED]
- **set files:** ‏118 sets נותחו ל-`known_sets_params.csv`: ‏117 מהקבוצה ועוד `sets/bd.set`. ‏[VERIFIED]
  - בכל ה-box אין קובץ בשם 1H_Ramil או stochastic_asian. [OBSERVED]
- **deals:** ‏`algotrade/history/*_deals.csv`, ‏read-only. משם שוחזרו 68,616 סלים (`t377_baskets.csv.gz`, בלי tickets או מזהים). [OBSERVED]

## שיטת ה-fingerprint ‏(OBSERVED)
- **בניית סל:** רצף כניסות באותו magic ובאותו צד, עד שכל הפוזיציות נסגרות.
- **מה נמדד בכל סל:**
  - לוט פתיחה, ולוט פתיחה חלקי (יתרה בסוף היום הקודם / 600k)
  - פערי מחיר בין הוספות (‎$): gap1, ‏gap2, ‏gap5, ‏gap6, ‏gap7
  - יחס לוטים חציוני, מחושב רק על לוטים של 0.05 ומעלה
  - מרחק יציאה בסל ברמה אחת
  - שעת כניסה
  - יישור לנר: אחוז הכניסות שנפתחות בשניות 0–2, ומתוכן אחוז הכניסות שנופלות על minute%15, ‏%5 או ‎==0
  - יציאות SL ויציאות הגנה (‏`n_*_v`)
- **אגרגציה:** חשבון × magic|comment × חודש, ב-`t377_fingerprints.csv`. מעברי TF זוהו ברמת שבוע ויום.
- **מגבלות:**
  - ה-gaps כוללים overshoot של נר. ב-M1 עם Fix של 18–25 נק' רואים ‎~$0.9–1.1.
  - ה-overlap מאפשר יותר הוספות לסל מ-MaxOrders.
  - עיגול לוטים קטנים (0.07 → 0.11) מנפח את יחס הלוטים ל-~1.56. [ASSUMED]

## הטבלה (קובץ מלא: `t377_bd_sets.csv`)
| חשבון | מ- | עד | magic | set | ראיה | ביטחון | תגית |
|---|---|---|---|---|---|---|---|
| BD1 | 17.09.25 | 11.11.25 | שונים | BTC Bot (לא BD) | comment | גבוה | VERIFIED |
| BD1 | 30.10.25 | 10.11.25 | 1111 | casperit black dragon set m1 5kstandard (‏#74605) | fingerprint + comment "(casper)" | בינוני-גבוה | OBSERVED+ASSUMED |
| BD1 | 11.11.25 | 26.10.26 | 5555 | Lars = bd.set, ‏M15 | ציטוט (Excel) + magic/comment | גבוה | VERIFIED |
| BD2 | 07.04.26 | 15.04.26 | 223344 | CasperIT_BlackDragon_Hybrid_M1_50k_2digits | ציטוט + magic/comment | גבוה | VERIFIED |
| BD2 | 15.04.26 | 29.05.26 | 123654 | CasperIT_BlackDragon_Agressive_M1_50k_2digits | ציטוט + magic/comment | גבוה | VERIFIED |
| BD2 | 01.06.26 | 17.06.26 | 1111 | 1H_Rramil (אין קובץ) | ציטוט + comment | שם גבוה, פרמטרים UNKNOWN | VERIFIED/UNKNOWN |
| BD2 | 18.06.26 | 30.06.26 | 11111 | **UNKNOWN** | התנגשות Excel/fingerprint | נמוך | UNKNOWN |
| BD2 | 22.06.26 | 06.08.26 | 1111 | EA_Black_Dragon_mt5_xauusd_m5_2_digits_stoch_true.set (‏#75940), ‏M5 | ציטוט + fingerprint חלקי | בינוני | VERIFIED/OBSERVED |
| BD2 | 05.08.26 | 20.08.26 | 16102020/190726 | Hamster/Ultima (לא BD) | comment | גבוה | VERIFIED |
| BD2 | 24.08.26 | 26.10.26 | 5555 | Lars = bd.set, ‏M15 | fingerprint + magic/comment | גבוה | OBSERVED |
| BD3 | 27.02.26 | 30.04.26 | 5555 | Lars, ‏M15 | ציטוט + fingerprint | גבוה | VERIFIED |
| BD3 | 30.04.26 | 15.05.26 | 1111 | ea_black_dragon_mt5_stochastic_asian_xauusd_2digits_m5 (אין קובץ) | ציטוט + comment | שם גבוה, פרמטרים UNKNOWN | VERIFIED/UNKNOWN |
| BD3 | 18.05.26 | 02.06.26 | 5555 | Lars, ‏M5 | ציטוט + fingerprint | גבוה | VERIFIED |
| BD3 | 09.06.26 | 30.07.26 | 5555 | Lars, ‏M15 (ב-Excel 5M) | fingerprint | בינוני | OBSERVED |
| BD3 | 03.08.26 | 06.08.26 | 5555 | Lars, ‏M5 | fingerprint | בינוני | OBSERVED |
| BD3 | 12.08.26 | 26.10.26 | 5555 | Lars, ‏M15, שעות 5–19 | fingerprint | בינוני | OBSERVED |
| BD4 | 13.04.26 | 30.04.26 | 5555 | Lars = bd.set, ‏M15 | ציטוט + fingerprint | גבוה | VERIFIED |
| BD4 | 30.04.26 | 12.05.26 | 90125 | BTC Bot (לא BD) | ציטוט + comment | גבוה | VERIFIED |
| BD4 | 18.05.26 | 02.09.26 | 5555 | Lars = bd.set, ‏M15 | ציטוט + fingerprint | גבוה | VERIFIED |
| BD5 | 15.04.26 | 16.09.26 | 5555 | Lars = bd.set, ‏M15 | ציטוט + fingerprint | גבוה | VERIFIED |
| BD5 | 05.10.26 | 23.10.26 | 5555 | Lars = bd.set, ‏M15 | fingerprint | גבוה | OBSERVED |
| BD6 | 15.04.26 | 01.05.26 | 5555 | Lars = bd.set, ‏M15 | ציטוט + fingerprint | גבוה | VERIFIED |
| BD6 | 01.05.26 | 29.05.26 | 123654 | CasperIT_BlackDragon_Agressive_M1_50k_2digits | ציטוט + magic/comment | גבוה | VERIFIED |
| BD6 | 09.06.26 | 24.06.26 | 1878943 | 1878943_eabd_jpb_xauusd_2d_mt5_v1.00 (Jens, ‏SL 8000) | ציטוט + magic/comment | גבוה | VERIFIED |
| BD6 | 25.06.26 | 23.10.26 | 5555 | Lars = bd.set, ‏M15 | ציטוט + fingerprint | גבוה | VERIFIED |
| BD7 | 20.04.26 | 23.04.26 | 110725 | Trend AI "Andre" (לא BD) | ציטוט + comment | גבוה | VERIFIED |
| BD7 | 24.04.26 | 13.05.26 | 123654 | CasperIT_BlackDragon_Agressive_M1_50k_2digits | ציטוט + magic/comment | גבוה | VERIFIED |
| BD7 | 21.04.26 | 10.06.26 | 1111 | **UNKNOWN** (ASSUMED: ידני דרך הפאנל של BD) | — | נמוך | ASSUMED |
| BD7 | 24.06.26 | — | — | Lars 1M לפי ה-Excel, אבל אין עסקאות (יתרה ~‎$1.7) | ציטוט + אין deals | גבוה | VERIFIED |
| BD8 | 29.09.25 | 09.10.25 | 5000 | **UNKNOWN** (הכי קרוב: משפחת casper m1 5kstandard) | fingerprint חלקי | נמוך-בינוני | ASSUMED |
| BD8 | 21.10.25 | 21.10.25 | 211025 | BTC Bot (לא BD) | comment | גבוה | VERIFIED |
| BD8 | 29.05.26 | 26.10.26 | 5555 | Lars = bd.set, ‏M15 | ציטוט + fingerprint | גבוה | VERIFIED |

## הערות לכל חשבון
- **BD1:**
  - 30.10–10.11.2025 התאמה מלאה לפרמטרים של `casperit black dragon set m1 5kstandard`: ‏M1, שעות 6–19, ‏Fix 3000 ו-Dyn 2000 מרמה 6 (3 ספרות), ‏Martin 1.5, ‏TP 1000. [OBSERVED]
  - **רץ במקביל ל-BTC Bot ‏291025.** [OBSERVED]
  - הקובץ (‏#74605) פורסם ב-31.10, אבל ה-deals מתחילים ב-30.10. ‏[ASSUMED] נדב קיבל אותו קודם, או שפורסם בהודעה מוקדמת יותר.
- **BD2:**
  - **11111:** ‏M1, ‏Fix ‎~$3, ‏Dyn ‎~$2.4, ‏×1.56, ‏TP ‎~$1.1, שעות 9–15. אף set file ידוע לא תואם.
  - ‏**stoch_true (Fix 800 = ‎$8):** הפערים תואמים לקובץ. יחס הלוטים (~1.5) לא תואם ל-Martin 1.4 שבקובץ. ‏[ASSUMED] ה-Martin שונה ידנית.
- **BD3:** שעות הכניסה זזו מ-3–21 ל-5–19 ב-12.08.2026. [OBSERVED]
- **BD5:** אין כניסות בין 17.09 ל-04.10.2026. זה מתיישב עם יציאות ההגנה ב-14.09 וב-16.09 (‏t376).
- **BD6 ו-BD5 ב-01.05.2026:** יש כמה סלים של 1111 בלוט 2.0. ‏[ASSUMED] ידני או טעות. הוצאו מהטבלה.
- **BD8:** בין 12 ל-21.08.2026 היו 18 כניסות ב-XAGUSDc עם 5555. ‏[ASSUMED] ה-set הוצמד בטעות לגרף של כסף.
- **לוט מול equity:** מ-05.2026 החציון של ‎lot0 / (equity/600k)‎ הוא 0.8–1.0, כלומר הכלל נשמר. באפריל 2026 הוא ~1.42, כלומר בערך equity/420k. [OBSERVED]
  - לוח ה-resets והלוטים המלא נמצא ב-`t377_excel_log_extract.csv` (עד 16.07).
  - אחרי 16.07 הלוט ידוע רק מה-fingerprint החודשי.

## פערים / UNKNOWN
1. **אין קובץ על ה-box** ל-1H_Rramil ול-stochastic_asian. רק נדב או ה-VPS יכולים לספק אותם.
2. **BD2 ‏11111 ‏(18–30.06):** איזה set זה?
3. **BD8 ‏5000 (09–10.2025):** מקור ה-set לא ידוע. התקופה קודמת לכיסוי של ה-Telegram.
4. **ה-set החי של RoboForex ב-2 ספרות (Lars) לא נמצא על ה-box.** יש רק bd.set ב-3 ספרות.
   - ה-fingerprint מתיישב עם ‎/10: ‏Fix 300, ‏Dyn 200, ‏TP 200, ‏trail 60/10.
   - **MaxSpred (20 או 50) ‏UNKNOWN**, כמו ב-FIDELITY_GAPS G3.
5. **אחרי 16.07.2026 אין רישומי Excel.** החל משם הכול fingerprint.

## קבצים (`grok_data/t377/`)
- `RESULTS_t377_bd_sets.md`: הקובץ הזה.
- `t377_bd_sets.csv`: הטבלה.
- `t377_fingerprints.csv`: חשבון × magic|comment × חודש.
- `t377_excel_log_extract.csv`: שורות היומן, בלי מזהים.
- `known_sets_params.csv`: פרמטרים של 118 sets.
- `t377_baskets.csv.gz`: הסלים.
- `parse_sets.py`, ‏`fingerprint.py`, ‏`agg.py`, ‏`regimes.py`: שחזור.
