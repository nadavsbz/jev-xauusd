# PREREG t380 - חיתוך basket מותנה-מהירות (L_N fast) - שלב 0 (counterfactual live)
STATUS: FROZEN for stage 0
נכתב 25.11.2026 (Asia/Jerusalem) לפני כל חישוב של t380. Grok, box בלבד, read-only. כינויים בלבד. לא נוגעים ב-Benzaquen ולא פותחים accounts.json.
המשך ישיר של t379 (PREREG sha256 `30f02b3d36e372841b04275c9411efc2f0534c572683a02b4f4f7cc794bc0c13`). משלב את ביקורת Claude (00:40): P0, P1-1, P1-2, P1-3, P2.

## השערה
חיתוך basket של BD ב-level N עוזר רק כשה-level הושג מהר (חתימת crash מ-t379: ~2.5 ATR תוך ~2–3 שעות), ולא כשה-basket העמיק לאט (שם רוב ה-baskets מתאוששים ברווח).

## גריד (K = 8, נספר בספירה המצטברת / DSR)
N ∈ {6,8} × T ∈ {2,4} שעות × k ∈ {2,3}. שם combo: `N{N}_T{T}_k{k}`.
ה-N/T/k נגזרו מאירועי 4–11/2026, כלומר in-sample (P1-1). שלב 0 הוא סינון בלבד, לא הוכחה.

## מקורות (זהים ל-t379)
- deals: `/workspace/algotrade/history/<alias>_deals.csv`. ‏net = profit+commission+swap+fee. מיון לפי time_msc+ticket. ‏type 3 (credit) לא נספר ביתרה.
- חשבונות: BD1, BD2, BD3, BD5, BD6, BD7, BD8, BTC_Bot_4 (8). ל-BD4 אין export.
- מחירים: Dukascopy XAUUSD H1 BID (UTC), `claude_bridge/out_20261117/g2_crossmarket/data/XAUUSD_1h.csv` (עד 31.10.2026). baskets שנפתחו אחרי סוף הנתונים לא נבדקים (אין חיתוך).
- אזור זמן שרת (מתוך הסטיות של t379, מאומת in-bar): ‏BD1, BD8 (EGlobal) = Europe/Berlin (CET/CEST). כל השאר (RoboForex) = Europe/Athens (EET/EEST).
- basis לכל חשבון = חציון (מחיר deal − (H+L)/2 של הבר שלו), כמו ב-t379. מחירי H1 של הבר = Dukascopy + basis.
- יחידות: cent, ‏k=100. כל סכום בסנטים, ‏USD = סנטים/100. ‏mult מכויל כמו ב-t376/t379 (יצא 100 בכל החשבונות).

## הגדרת basket (מ-t379, ללא שינוי)
- לכל account × symbol × magic × side: ‏basket נפתח ב-deal כניסה (entry=0) כשה-volume הפתוח של (symbol, magic, side) הוא 0, ונסגר כשהוא חוזר ל-0.
- יציאות (entry 1/3, כולל magic 0 של ההגנה) משויכות לפי position_id.
- level = מספר deals הכניסה שבוצעו ב-basket עד אותו רגע. ‏t0 = זמן הכניסה הראשונה. ‏p1 = מחיר הכניסה הראשונה.
- P&L בפועל של basket = סכום net של כל ה-deals של הפוזיציות שלו.
- basket "crash" = basket שלפחות פוזיציה אחת שלו נסגרה ב-deal `n_*_v` של אחד מ-59 אירועי ההגנה.
- **scope ראשי (להחלטה):** ‏magic 5555 על XAU, כמו ה-main של t379. ל-BD7 אין 5555, ולכן ב-scope הראשי יש רק 7 חשבונות עם baskets של BD. כלל ≥5/8 נשאר כפי שנכתב (כלומר ≥5 חשבונות חיוביים מתוך 8, כשאחד מהם בהכרח 0).
- **sensitivity (לא להחלטה):** ‏scope BD_all (כל magic עם comment של Black Dragon), ו-spread=0.

## קירוב floating / המחיר בבר (מ-t379)
- מחיר הבר בצד השרת = Dukascopy BID + basis של החשבון. floating של פוזיציה = s·(P − p_i)·v_i·mult, כש-s=+1 לקנייה ו-−1 למכירה.
- כמות פתוחה ברגע c = net exposure לפי ה-deals עם זמן UTC ≤ c (כניסות פחות יציאות לכל position_id).

## כלל החיתוך t380 (קבוע מראש)
לכל basket ב-scope עם levels ≥ N:
1. tN = זמן ה-deal של level N. תנאי מהירות: **tN − t0 < T שעות**.
2. ATR(14,H1) = ממוצע פשוט של True Range של 14 ברי H1 סגורים לפני הבר הנבדק (בדיוק כמו `px.atr` ב-t379, Dukascopy).
3. בדיקה רק בסגירות של ברי H1 (UTC). הבר הראשון שנבדק הוא הבר שמכיל את tN. נבדקים ברים שזמן הסגירה שלהם c מקיים c − t0 < T + 1h (כלומר עד בר אחד אחרי חלון T, כי הרזולוציה היא H1), וגם c < זמן סגירת ה-basket בפועל.
4. תנאי מרחק בסגירה: s·(p1 − C) ≥ k·ATR, כש-C = close של הבר + basis.
5. **ביצוע:** ה-basket נסגר כולו ב-C, בסגירת **הבר הראשון** שבו כל התנאים מתקיימים. **אין נתוני M1/tick ל-2025–2026 על ה-box** (קובץ ה-ticks היחיד הוא מ-2023), ולכן ביצוע ב-H1 close הוא סופי ולא "או טוב יותר".
6. תוצאה = realized של פוזיציות ה-basket עד c + Σ s·(C − p_i)·v_open·mult + עמלת יציאה (exc·vol, החציון בפועל) − spread 0.30$·vol·mult (ASSUMED). ‏swap עתידי מתאפס. כל ה-deals של ה-basket אחרי c מבוטלים.
7. Δ = תוצאה − P&L בפועל. ‏basket שלא נחתך: Δ = 0.
8. הנחת יסוד (ASSUMED, כמו ב-t379): אין path-dependence. שאר רצף העסקאות (lot, רצפת הגנה, baskets הבאים) לא משתנה.

## טבלה (P1-3), לכל combo × חשבון
crash saved = Σ Δ על baskets ‏crash שנחתכו. cut_profitable = מספר baskets ‏non-crash שנחתכו והיו רווחיים בפועל. forgone = Σ Δ על baskets ‏non-crash שנחתכו. net = saved + forgone. הכול בסנטים וב-USD, ומפוצל גם ל-"data" ו-"other" (ראה P1-2).

## P1-2: חלון נתוני ארה"ב (הגדרה מדויקת, קבועה מראש)
- זמני הפרסום מוגדרים ב-**America/New_York**: ‏08:30 ו-10:00 ET, בימי חול (ב'–ו' לפי ET).
- מיפוי לזמן שרת: ‏CET/CEST (‏BD1, BD8) = ‏14:30/16:00 ברוב השנה. EET/EEST (שאר החשבונות) = ‏15:30/17:00. בשבועות שבהם ה-DST של ארה"ב ושל אירופה לא מסונכרנים, ההפרש זז בשעה. ההגדרה לפי ET מטפלת בזה. זו פרשנות מדויקת של "14:30/16:00 server": המספרים האלה מתאימים רק לשרתי CET.
- חיתוך מסווג כ-**data** אם זמן הטריגר c (סגירת הבר, UTC) נופל ב-[release, release + 90 דקות] של אחד משני הפרסומים, באותו יום. אחרת **other**.
- הערה: בגלל רזולוציית H1, ‏c נופל תמיד על שעה עגולה ב-UTC. לכן אחרי 08:30 ET נכנסות הסגירות של +30 ו-+90 דקות, ואחרי 10:00 ET נכנסות +0 ו-+60.
- sensitivity (לא להחלטה): פירוש מילולי, ‏14:30/16:00 בזמן השרת של כל חשבון.

## כלל GO לטסטר (קבוע מראש)
combo עובר אם **כל** אלה מתקיימים:
(a) net > 0 ב-≥5 מתוך 8 חשבונות (scope ראשי).
(b) net כולל > 0.
(c) net > 0 כשמוציאים את חיתוכי ה-data, כלומר net_other > 0 (סה"כ).
- אם כמה combos עוברים: **מנצח יחיד** לפי net כולל מקסימלי. tie-break: ‏N קטן יותר, אחר כך T גדול יותר, אחר כך k גדול יותר.
- אם אף אחד לא עובר: **NO-GO**, אין הרצת טסטר, ומוצעת משפחה הבאה ב-pre-registration.
- K = 8 מתווסף ל-N המצטבר (ה-ledger המדויק אצל Claude ב-LEDGER.md).

## אם GO: שלב הטסטר (מוגדר כאן, לא מורץ על ידי Grok)
- P0: ‏real ticks של RF קיימים רק מ-1/2022. כל שלב טסטר מוגבל ל-1/2022–10/2026.
- P1-1: ‏DEV = ‏1/2022–12/2023 + ‏4–10/2026. ‏HOLDOUT = ‏1/2024–3/2026. רק המנצח היחיד מ-DEV רץ על HOLDOUT, ו-HOLDOUT לא משמש לבחירת פרמטרים.
- P2: בטסטר, ATR(14,H1) מחושב מנתוני הברוקר (RF) ולא מ-Dukascopy. ב-live (שלב 0) הוא מ-Dukascopy H1. ההבדל מדווח.
- רק Claude מריץ טרמינלים. הרצה על Benzaquen דורשת אישור של נדב (זיכרון נמוך).
