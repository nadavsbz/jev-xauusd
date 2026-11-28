# PREREG t379 - מיפוי 59 אירועי ההגנה של BD והפחתת נזק (counterfactual)
נכתב 25.11.2026 (Asia/Jerusalem) לפני כל חישוב. Grok, box בלבד, read-only. כינויים בלבד. תרגיל מיפוי, לא gate.

## מקורות
- אירועים: `delivered_t376/t376_events.csv` (59 אירועים, clustering של סגירות `n_*_v` בפער 30 דק' כמו ב-t376).
- deals: `/workspace/algotrade/history/<alias>_deals.csv`, ‏loader של t376/t378: ‏net=profit+commission+swap+fee, מיון time_msc+ticket, ‏type 3 (credit) לא ביתרה.
- חשבונות: אלה שמופיעים ב-events (BD1,2,3,5,6,7,8 ו-BTC_Bot_4). ל-BD4 אין export.
- מחירים: Dukascopy XAUUSD H1 BID (UTC) מ-`claude_bridge/out_20261117/g2_crossmarket/data/XAUUSD_1h.csv` (עד 31.10.2026).
- יחידות: כל החשבונות cent, ‏k=100. כל סכום בסנטים, ‏USD = סנטים/100. mult (רווח לכל 1 lot × ‏1$) מכויל מה-deals כמו ב-t376.

## (4) הגדרת basket
- per account × magic × side (buy/sell). ‏basket נפתח ב-deal כניסה (entry=0) כשה-volume הפתוח של (magic,side) הוא 0, ונסגר כשהוא חוזר ל-0.
- יציאות (entry 1/3, כל magic, כולל magic 0 של ההגנה) משויכות לפי position_id לפוזיציה ול-basket שלה.
- level = מספר deals הכניסה שבוצעו ב-basket עד אותו רגע. ‏Lot_Init = volume של הכניסה הראשונה. ‏max/first = volume מקסימלי של כניסה / הראשונה. בדיקת lot ratio 1.5 מול ה-deals.
- P&L של basket = סכום net של כל ה-deals של הפוזיציות שלו.
- basket "crash" = basket שלפחות פוזיציה אחת שלו נסגרה ב-deal `n_*_v` של אחד מ-59 האירועים.
- כללי ה-level חלים רק על magic 5555 (EA Black Dragon). כלל ה-equity היומי חל על החשבון (כל ה-magics).

## (1) Basket בטריגר, לכל אירוע
- לכל צד: levels פתוחים, max lot / first lot, ‏Lot_Init, מחיר כניסה ראשונה מול מחיר הטריגר (מה-comment `n_<price>_v` של ה-deal הראשון) ב-$ וב-ATR(14) של H1.
- ATR(14) = ממוצע פשוט של True Range של 14 ברי H1 שנסגרו לפני בר הטריגר.

## (2) Timing
- שעות מהכניסה הראשונה של ה-basket המוביל (הכי הרבה volume פתוח בטריגר) עד הטריגר.
- הקירוב ל-floating: לכל בר H1, ‏floating = Σ s·(P_adverse − p_i)·v_i·mult על הפוזיציות הפתוחות של ה-basket, כש-P_adverse = low לקנייה / high למכירה של הבר, ועוד basis = חציון (מחיר deal − (H+L)/2 של הבר שלו) לכל חשבון. כולל realized של פוזיציות ה-basket שכבר נסגרו. כמות פתוחה = net exposure לפי ה-deals עד סוף הבר (שמרני).
- המרת זמן שרת→UTC: EET/EEST (‏UTC+2 בחורף, +3 בקיץ לפי DST האירופי). אימות: אחוז ה-deals שמחירם (פחות basis) בתוך [low−1$, high+1$] של הבר; אם <90% מדווחים כ-UNKNOWN חלקי.
- סף −5% / −10%: floating של ה-basket ≤ ‏−5%/−10% מהיתרה בתחילת ה-basket (קירוב ל-equity; ASSUMED). מדווחים את ה-level שהיה פתוח בבר הראשון שחצה.

## (3) כללי counterfactual
- **L4/L5/L6:** סוגרים את ה-basket מיד אחרי שה-deal של level N מתבצע, במחיר אותו deal. תוצאה = realized עד אז + Σ s·(p_N − p_i)·v_i·mult + עמלת יציאה (= עמלות הכניסה שוב) − עלות spread של 0.30$ ×volume פתוח ×mult (ASSUMED; רגישות 0). swap עתידי מתאפס. מחושב מה-deals בלבד, בלי H1.
- **D5/D8:** stop יומי (יום שרת). ‏ref = יתרה ב-00:00 + floating בבר הראשון של היום (קירוב). כשה-equity המקורב (יתרה + floating לפי P_adverse) ≤ ref·(1−X%): סוגרים את כל הפוזיציות במחיר שמוביל בדיוק ל-equity של הסף (אופטימי) וגם ב-P_adverse של הבר (פסימי); מדווחים את שניהם, הראשי = פסימי. כל basket שנפתח באותו חשבון אחרי ה-stop ועד סוף אותו יום שרת מוסר (ה-net שלו נספר כ-forgone/saved).
- **השוואה:** ‏Δ = תוצאה תחת הכלל − תוצאה בפועל, לכל basket מושפע. ‏crash saved = Σ Δ על baskets ‏crash. ‏non-crash: מספר baskets שנחתכו, מתוכם רווחיים בפועל, ו-profit forgone = Σ Δ (שלילי = ויתור). ‏**net = Σ Δ על כל ההיסטוריה** של כל החשבונות.
- הנחת יסוד (ASSUMED): שאר רצף העסקאות לא משתנה (אין path-dependence: ‏lot, רצפת ההגנה ו-baskets הבאים נשארים כפי שהיו). זו מגבלה מרכזית.

## כללי פרשנות
- אין gate. כלל "שווה prereg לטסטר" אם net > 0 בסנטים בסך הכל וגם ב-≥ חצי מהחשבונות עם crash. אחרת "לא".
- in-sample, נתוני live, ‏~13 חודשים. רק השערה ל-prereg טסטר על 2016–2026.
