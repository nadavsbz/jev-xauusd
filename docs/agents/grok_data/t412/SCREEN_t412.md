# t412 — סינון ספרות: כללים ל-BTCUSD/ETHUSD שאינם במשפחות הסגורות (K=0, בלי PREREG, בלי ריצה)

**כותב:** Grok (המאסטרו). **נכתב:** 26.11.2026 (שעון ישראל, UTC+2). **בקשה:** claude_outbox.md, רשומה "26.11.2026 03:40".
**סטטוס:** סינון ספרות בלבד. לא חושבה שום תשואה על הנתונים שלנו בסבב הזה, לא נפתח holdout, K=0.
**תגיות:** VERIFIED = נבדק במקור/בקובץ; OBSERVED = נטען במקור שצוטט, לא שוחזר אצלנו; ASSUMED = הסקה/גזירה שלי; UNKNOWN = לא ידוע.

## 0. מה סגור (נקרא read-only מ-docs/prereg ו-SCAN_PLAN.md, VERIFIED)
| מזהה | המשפחה | תוצאה |
|---|---|---|
| t326 | עונתיות שעה-ביממה BTC/ETH (בחירה מתגלגלת) | סגור |
| t327 | I2 noise-area על BTC/ETH | סגור |
| t334 | ETH יום/לילה, היפוך מותנה סשן (JRFM 2026) | סגור |
| t342 | אינדיקטורי TradingView (SuperTrend, UT Bot וכו') | סגור |
| t343 | SMC מכני על BTC M5 | סגור |
| t365 | היפוך אחרי מפולת סגירות כפויות (מחיר+OI+נפח), 24h | 139 עסקאות, ‎−0.68%/עסקה, t=−2.14 — המשכיות, לא היפוך |
| r71 | היפוך BTC אחרי funding קיצוני + ADX<20 | n=2, KILL |
| r80 | היפוך BTC/ETH אחרי זעזוע נפח שעתי | gross ‎−5.9bp, t=−3.78 — המשכיות |
| r89 | BTC בסוף שבוע כמנבא למדדים ביום שני | נכשל ב-dev |
| r98 | היפוך BTC אחרי פקיעה חודשית ב-Deribit | נכשל |
וגם נבדקו בעבר (VERIFIED בקבצים): סוף-שבוע לונג BTC/ETH (t187u/t209, ‏BACKLOG t211 #28 — DROP), ‏BTC_MAX10 / פייד MIN10 (t199u, נכשל, corr C1 0.47), ‏MR/מומנטום יומי ו"יום חריג" (t187u Family 1, ≤0.89bp), ‏ETH/BTC ratio (STABLE), ‏Coinbase premium (G2-B, ‏n=565, t=1.38, KILL), ‏stablecoin supply כמסנן ל-C1 (r94/r94b), ‏TGA (r100), ‏halving (r2), ‏שעה 22 UTC (Padyšák-Vojtko = משפחת t326).

## 1. עלויות (VERIFIED מ-/workspace/research_new_component/COST_PRESCREEN_20261111_2000_third_sleeve.md ו-_t211.md)
- הבריף: 2×2bp = **4bp RT**. בפועל בקבצי העלות: ‏**BTC ECN ‏2.84bp RT**, ‏**ETH ECN ‏6.74bp RT** (עמלה 3bp/צד). לכן כלל חדש כדאי שיהיה **BTC בלבד**.
- **swap קריפטו ב-RF: 4.75%/שנה בשני הצדדים** (לא UNKNOWN — נמצא בקבצי העלות), ≈**1.30bp ללילה**, שישי ×3 (≈3.90bp). אין funding carry סחיר ב-RF.
- נתונים על ה-box (VERIFIED): ‏`data/binance/BTCUSDT_1h.csv`, ‏`ETHUSDT_1h.csv` עד 09.11.2026 23:00; ‏`data/binance_funding/BTCUSDT_funding_2019_2026.csv` (BTC בלבד; קבצי ה-zip החודשיים הם שגיאות NoSuchKey); ‏`data/fomc/scheduled_statement_dates.csv`. **אין** לוח מועדי פרסום CPI (יש רק רמות CPI מ-FRED) — UNKNOWN עד הורדה מ-BLS.

## 2. טבלת המועמדים ששרדו את הסינון (3, לא 5 — ביושר)
| # | כלל (BTC) | מאמר + קישור | gross לעסקה מהמקור | מול 4bp (+swap) | תקופת מדגם | OOS / אחרי פרסום | נתונים: יש לנו? | מתאם צפוי ל-C1 | סיכוי |
|---|---|---|---|---|---|---|---|---|---|
| **A** | **היפוך אחרי הכרזת FOMC (ואופציונלית CPI):** נר H1 של ההכרזה (14:00 ET ל-FOMC) קובע כיוון; נכנסים הפוך בפתיחת הנר הבא, יוצאים אחרי 4 שעות. החזקה 4h, פוזיציה אחת. | Johansson & Vilhelmsson, "Bitcoin's Price Alchemy…", SSRN 4478184 (working paper, לא פורסם בכתב-עת — VERIFIED באתר המחבר) https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4478184 ; גודל התנועה: Yang & Wang, FRL 101 (2026) https://ideas.repec.org/a/eee/finlet/v101y2026ics1544612326006021.html | המאמר: "התגובה הראשונית ל-FOMC נוטה להתהפך ב-4 השעות הבאות" (OBSERVED, תקציר; **מספר bp לא בתקציר — UNKNOWN**, ה-PDF לא נגיש מה-box). Yang-Wang: ממוצע |תשואה| בשעה הראשונה 1.25% מול 0.66% רגיל (OBSERVED). אם 30–50% מהתנועה מתהפך → **≈35–60bp** (ASSUMED). | 4bp (2.84 בפועל) + לילה אחד 1.30bp אם היציאה אחרי rollover (FOMC: יציאה ≈22–00 UTC) → יחס ≈0.07–0.15 (ASSUMED) | J&V: אפקט שהחל ב-2021 (OBSERVED); Y&W: 41 הכרזות 01.2021–01.2026 | **אין OOS מפורסם להיפוך** (UNKNOWN). Pyo & Lee FRL 2020 (https://doi.org/10.1016/j.frl.2019.101386): FOMC כמעט לא השפיע לפני 2020 (OBSERVED). אין שכפול אחרי פרסום. | מחירים: כן (BTC 1h). FOMC: כן. CPI: צריך לוח BLS (ציבורי, בלי הרשמה, ASSUMED). | נמוך: ~8–20 אירועים/שנה × 4h, בלי קשר למגמה (ASSUMED) | **נמוך-בינוני.** n קטן (~47 FOMC עד 11.2026, ~+70 CPI); אירועי מאקרו על זהב/מדדים כבר נכשלו אצלנו; ה-H1 גס מול נתוני דקה במאמר. יתרון: מנגנון ברור (overshoot בנזילות דקה), עלות זניחה. |
| **B** | **זרימות ETF ספוט → BTC ל-24h:** אחרי פרסום זרימת היום (≈14:00 UTC למחרת) — לונג 24h אם הזרימה ברבעון העליון (אופציה: שורט בתחתון). | Lim, "The Price Impact of Spot Bitcoin ETF Flows", SSRN 6592830 (2026) https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6592830 ; נגד: Fabus et al., SSRN 7545019 (2026) https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7545019 | Lim: זרימות "מנבאות תשואה של היום הבא" (Newey-West t=3.12), אבל בלי יישור זמן פרסום (OBSERVED). Fabus et al.: אחרי יישור לחלון שמתחיל אחרי שהזרימה פומבית — **אין קשר חיובי** (OBSERVED). בדיקה לא-אקדמית (whycoinmoves): +10.7bp ל-1σ, t=1.03 (OBSERVED). gross סחיר: **≈0–11bp** (ASSUMED). | 4bp + 1.30bp לילה ≈5.3bp → יחס ≈0.5–∞ | 01.2024–04.2025 (Lim); 01.2024–07.2025 (Fabus) | חלש/שלילי אחרי יישור זמן (OBSERVED). קצר מאוד (~2.9 שנים). | לא על ה-box. Farside — טבלה ציבורית (ASSUMED שאפשר בלי הרשמה). | בינוני: הזרימות עוקבות אחרי המחיר (corr 0.54 עם 5 ימים קודמים, DWF Labs, OBSERVED) → קרוב למומנטום/C1 (ASSUMED 0.2–0.4) | **נמוך.** הראיה הטובה תלויה בטעות תזמון; העלות אוכלת חלק גדול. |
| **C** | **הנפקת stablecoin (mint ≥$1M) → לונג BTC ל-24h** מהשעה המלאה הראשונה אחרי ההנפקה. | Ante, Fiedler & Strehle, FRL 41 (2021) https://doi.org/10.1016/j.frl.2020.101867 (WP: https://www.blockchainresearchlab.org/wp-content/uploads/2020/05/The_Influence_of_Stablecoin_Issuances_on_Cryptocurrency_Markets_BRL_Working_Paper_No_11.pdf); רקע: Griffin & Shams, JF 75(4) 2020 https://doi.org/10.1111/jofi.12903 | CAAR(0,24h) **0.47–0.69%** *חריג* (VERIFIED ב-PDF). אבל הבסיס בחלון האומדן ‎−0.018%/שעה (VERIFIED) → תשואה גולמית ≈**4–26bp** (ASSUMED, גזירה). אפקט USDT עצמו הוא **לפני** ההנפקה (לא סחיר); אחרי ההנפקה מובהק בעיקר ל-HUSD/BUSD שכבר לא פעילים. G&S: ‏3.85–8.13bp ל-3h על 100 BTC זרימה (2017–18, OBSERVED). | 4bp + 1.30bp → יחס ≈0.2–1.3 | 04.2019–03.2020 (12 חודשים, 565 אירועים) | אין OOS ידוע (UNKNOWN). המנגנון של G&S היה תלוי שחקן יחיד ב-2017–18. היום הנפקות מפורסמות מיידית בבוטים (Whale Alert) — crowding סביר (ASSUMED). | לא. דרושות חותמות זמן ברמת שעה של mint on-chain; Etherscan דורש API key (=הרשמה, אסור בלי אישור). חלופה בלי הרשמה UNKNOWN. | נמוך (אירועי, 24h) (ASSUMED) | **נמוך.** מדגם שנה אחת, האפקט הסחיר דק, משפחה סמוכה (r94) נסגרה, ונתונים לא זמינים בקלות. |

## 3. נפסלו בסינון (לא נכנסים לטבלה)
| רעיון | מקור | למה נפסל |
|---|---|---|
| סוף-שבוע / יום שני ב-BTC | Mueller, FRL 64 (2024) https://www.sciencedirect.com/science/article/pii/S1544612324004598 ; Caporale & Plastun FRL 2019 | ספרות: לא נמשך אחרי 2015 (OBSERVED). אצלנו: DROP ב-t187u/t209/t211 #28; המסה בשבת, 2022 ‎−41% (VERIFIED בקובץ). |
| היפוך אחרי זעזוע מחיר שעתי שלילי | "Intraday Bitcoin price shocks: when bad news is good news", J. Applied Economics 2022 https://www.tandfonline.com/doi/full/10.1080/15140326.2022.2151253 | המאמר: +3.13% אחרי 24h ל-‏−5% (2016–06.2021, OBSERVED). **אצלנו t365 ו-r80 מצאו המשכיות** אחרי 2021 → אותה משפחה, סגורה. |
| מומנטום/קונטרה אחרי יום חריג | Caporale & Plastun, FMPM 2020 https://link.springer.com/article/10.1007/s11408-020-00357-1 | נבדק ב-t187u Family 1: ≤0.89bp; גרסת תוך-יומית קרובה ל-I2 (t327). |
| funding / basis ("Crypto carry") | Schmeling-Schrimpf-Todorov (BIS) | r71 סגור; אין funding carry ב-RF (swap 4.75% בשני הצדדים). |
| פרמיות בין בורסות (Coinbase/Kimchi) | Huang et al. 2023 וכו' | G2-B ‏KILL. |
| ספרים עגולים (psychological barriers) | Choi, RIBAF 90 (2026) https://ideas.repec.org/a/eee/riibaf/v90y2026ics0275531926002217.html | "clustering חזק, מחסומים חלשים"; פריצה של מספר עגול = המשכיות (מגמה → C1). |
| taker flow / long-short ratio | — | אין מאמר אקדמי עם ניבוי ברמת שעה; בדיקות פומביות: corr ≈0 (OBSERVED, לא אקדמי). |
| VRP / DVOL / VoV | Atanasova et al., SSRN 6771170 (2026); arXiv 2410.15195 | לא נמצאה ראיה כיוונית סחירה ב-שעות–ימים; VoV דורש משטח אופציות מלא (UNKNOWN זמינות חינמית). |
| קשב/Google Trends | Liu & Tsyvinski, RFS 2021 | אופק שבועות, ביטוי של מומנטום → מתאם גבוה ל-C1 (ASSUMED). |

## 4. דעיכה / crowding (כללי)
- כל השלושה מבוססים על מדגם קצר ועל תקופה שבה המבנה של שוק הקריפטו השתנה (ETF מ-2024, CME 24/7 מ-05.2026 לפי RESULTS_t209 — VERIFIED שם). דעיכה סבירה (ASSUMED).
- A פחות חשוף ל-crowding כי ההיפוך הוא תוצאה של נזילות דקה סביב אירוע, לא של אות שכולם רואים (ASSUMED); B ו-C מבוססים על נתונים פומביים שמופצים מיד (ASSUMED crowding גבוה).

## 5. המלצה מדורגת ל-t413 (לאישור Claude)
1. **A — היפוך אחרי FOMC(+CPI) על BTC בלבד.** K=1: כלל אחד מוקפא, FOMC+CPI ממוזגים (FOMC לבד רק תיאורי). חלוקה מוצעת: **dev ‏01.01.2021–31.12.2023** (התקופה שהמאמר מזהה), **holdout ‏01.01.2024–09.11.2026** (סוף הנתונים), לא נוגעים ב-holdout עד שה-dev עובר. שערים מוצעים: dev נטו>0 עם t≥1.5 (n≈60), holdout נטו>0 באותו סימן, DSR לפי ספירת הניסויים המצטברת. דרוש: לוח שעות CPI מ-BLS. ה-KILL: dev gross ≤0. ה-iteration הבא אם נכשל: B.
2. **B — זרימות ETF** כ-t414 רק אם A נכשל (K=1, dev 01.2024–12.2025, holdout 01.2026–11.2026 — קצר מאוד, ולכן סיכוי נמוך מראש).
3. **C — לא להירשם עכשיו:** בלי מקור נתונים שעתי בלי הרשמה.
