# PREREG t387 - אירועי הגנה משותפים בין חשבונות (תיאורי בלבד)
נכתב 25.11.2026 ~06:40 (Asia/Jerusalem), **לפני כל חישוב**. Grok, ‏box בלבד, read-only. כינויים בלבד (A1..A8; ‏A4 = ‏#4 = BTC_Bot_4 ב-t376). אין מספרי חשבון, logins, IPs.
**K=0** (תיאורי, לא gate, לא נספר בלדג'ר). **אין המלצה לשינוי הגדרות** - שינויים בחשבונות הם של נדב.

## מקורות (קלט קפוא, sha מ-SHA256SUMS של המסירות הקודמות)
- אירועים: `bridge_pending/delivered_t376/t376_events.csv` (59 אירועים), sha `a5026724251d8543f86f556df68eb754ad16d8947e1cbbff10ed4d5f5247c9f9`.
- basket מוביל + lot התחלתי + הפסד הגנה: `bridge_pending/delivered_t379/t379_events_basket.csv`, sha `23721b337661f0cbcf5d087a44ef0f11842e7717ed604b329a198417eb6fc298`. חיבור 1:1 לפי (acc,start).
- set/TF לכל חשבון-תקופה: `bridge_pending/delivered_t377/t377_bd_sets.csv`, sha `207beaa197ff6a2bc76af8f0c0a170b0cfba1e86279e4a2455c91fbb7f2a13ee`.

## הגדרות
- **אירוע** = אשכול סגירות `n_<price>_v` מרשימת t376 (59).
- **שעון משותף:** זמני שרת. A1/A8 (EGlobal) ב-CET/CEST → מוסיפים שעה כדי להמיר לשעון Athens (EET/EEST) של שאר החשבונות (ממצא t379: ‏in-bar 100%). כל התאריכים/שעות להלן בשעון Athens.
- **shared-day** = תאריך שבו ל-≥2 חשבונות שונים יש אירוע. **shared-hour** = אותה שעה עגולה (YYYY-MM-DD HH) ב-≥2 חשבונות. רגישות (משנית): אשכול זמן - אירועים של ≥2 חשבונות בפער ≤60 דק' (single-linkage).
- חשבון עם כמה אירועים באותו יום/שעה נספר פעם אחת בקבוצה (האירוע הראשון שלו מייצג אותו לצורכי config).
- **config לאירוע:** set + TF מ-t377 לפי (חשבון, תאריך האירוע בתוך [from,to], ו-magic של ה-basket המוביל ב-t379 ∈ רשימת ה-magic של השורה). magic 0 → `manual(magic0)`. אין התאמה → `UNKNOWN`. שם set מנורמל למשפחה: Lars / CasperIT_Aggressive / CasperIT_Hybrid / Ramil_1H / stoch_true / stoch_asian / JPB / casper_m1 / BTC_Bot / TrendAI / Hamster / manual / UNKNOWN. TF = הערך הראשון ב-tf_observed (לפי ה-fingerprint).
- **lot/equity** = Lot_Init של ה-basket המוביל / היתרה בתחילת ה-basket (t379 `lead_bal_start`). **"אותו lot ליחידת equity"** = max/min של היחס בקבוצה ≤ 1.20.
- **"same config"** (לקבוצה): כל החשבונות בקבוצה עם אותה משפחת set + אותו TF + יחס lot בטווח ±20% (max/min≤1.2). מדווחים גם מדרג: same set; same set+TF; same set+TF+lot. ‏UNKNOWN לא נחשב "זהה".

## Q1
מספר shared-days ו-shared-hours, מספר האירועים שבתוכם, וכמה מהקבוצות same set / set+TF / set+TF+lot. רגישות: אשכולות ≤60 דק'.

## Q2 - סוגי תקופה
- חלון: 2026-04-13 עד 2026-10-26, ימי Mon–Fri בלבד. (שני אירועי 2025 של A1 מחוץ לחלון.)
- חשבון **פעיל** ביום d אם יש לו שורה ב-t377 עם from≤d≤to, למעט שורות "no trades". כל השורות הפעילות נספרות (כולל לא-BD כמו BTC Bot/Trend AI/Hamster).
- **LARS_ALL**: ≥2 חשבונות פעילים וכל השורות הפעילות הן משפחת Lars (כל TF). **MIXED**: ≥2 פעילים ולפחות שורה פעילה אחת שאינה Lars. ימים עם <2 פעילים - מחוץ לניתוח.
- מדדים: **R1 (ראשי)** = shared-days / ימי חלון במחלקה. R2 = shared-days / ימים עם ≥1 אירוע. R3 = אירועים / חשבון-ימים פעילים (בסיס).
- **bootstrap**: בלוקים = שבוע ISO × מחלקה. בכל resample דוגמים עם החזרה את בלוקי השבוע של כל מחלקה בנפרד (מספר בלוקים כמקור), מחשבים את המדד המצרפי (סכום מונה/סכום מכנה) ואת ההפרש MIXED − LARS_ALL. ‏10,000 resamples, ‏seed=387. מדווחים הפרש נקודתי + CI 95% (percentile). resample עם מכנה 0 → מושמט ומדווח.
- אזהרות שידווחו: n קטן, in-sample, confounding (מספר החשבונות הפעילים, תקופת השוק) - **לא סיבתי**.

## Q3
- **מדד הפסד ראשי:** `prot_loss` מ-t379 = ה-net הממומש של סגירות ההגנה (סנטים; סה"כ צפוי ~1,061,313 = ~$10.6K). משני: `loss_money` מ-t376 = יתרה לפני האירוע − equity בטריגר.
- מחשבים את הסכום והחלק מסה"כ על ימים (Athens) עם ≥3 חשבונות שונים עם אירוע; וגם ל-≥2 ולימים עם חשבון יחיד.
- USD = סנטים/100, רק סכומים ברמת הצי.

## פלטים
`t387_events_shared.csv` (59 שורות, כינויים, config, דגלי shared), `t387_summary.csv`, `RESULTS_t387.md` (עברית, תגיות VERIFIED/OBSERVED/ASSUMED/UNKNOWN), `SHA256SUMS.txt`. כל סטייה מה-PREREG תדווח במפורש.
