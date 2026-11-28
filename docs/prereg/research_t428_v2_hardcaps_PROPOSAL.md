# t428 — הצעת רישום מראש ל־v2 עם תקרות קשיחות

## מעמד ההצעה

זהו **מפרט מחקר מוצע לרישום מראש**, לפני שינוי הקוד ולפני הרצת טסטר כלשהי. הוא אינו משנה את ההכרעה להעביר לדמו את v1 כפי שנבדקה: החריגות `0.503` ו־`1.916` מוכרות ומכוסות בספי הניטור הקיימים. ההכרעה עצמה מבהירה שכל תיקון ייחשב גרסה חדשה ויחייב ריצה חדשה מול t420/t424. [docs/research/t427_review_20261127.mdL5-L13](https://github.com/nadavsbz/jev-xauusd/blob/35c079372c346b27e43c4e61e1069306fbad4467/docs/research/t427_review_20261127.md#L5-L13)

**אין כאן אישור שער, החלפה בדמו או מסחר.**

---

# 1. בסיסי ההשוואה הקפואים

## C1d — בסיס t420 A4

ההשוואה תהיה אך ורק מול:

```text
EA: CryptoTrend_C1d.mq5 v1
AssetVol=0.075
TargetVol=0.20
MaxGross=0.50
DriftCap=true
Period=2020-01-01..2026-10-31
InitialDeposit=120,000
Model=Every tick based on real ticks
```

תוצאות הבסיס הקפואות:

| מדד | t420 A4 |
|---|---:|
| יתרה סופית | 339,012.06 |
| נטו | +219,012.06 |
| נטו ביחס לבסיס C1 | 81.5% |
| max gross | 0.503 |
| max L_H6 | 11.45% |
| max L_H24 | 21.12% |
| max L_H48 | 21.49% |
| DD משוחזר H6 | 13.51% |
| שנים חיוביות | 6/7 |

ה־gross המרבי וה־stress מתועדים בתוצאת t420, לרבות 0 חריגות מעל 25% ב־H6 וב־H24. [docs/agents/grok_data/t420/RESULTS_t420_A4.mdL8-L18](https://github.com/nadavsbz/jev-xauusd/blob/35c079372c346b27e43c4e61e1069306fbad4467/docs/agents/grok_data/t420/RESULTS_t420_A4.md#L8-L18) היתרה הסופית וה־DD המשוחזר מתועדים גם בבדיקות השפיות. [docs/agents/grok_data/t420/RESULTS_t420_A4.mdL34-L39](https://github.com/nadavsbz/jev-xauusd/blob/35c079372c346b27e43c4e61e1069306fbad4467/docs/agents/grok_data/t420/RESULTS_t420_A4.md#L34-L39)

## I2 — בסיס t424

```text
EA: IndexNoiseLev.mq5 v1
TargetVol=0.075
MaxLev=1.90
Period=2020–2026
InitialDeposit=120,000 per yearly run
Model=Every tick based on real ticks
```

תוצאות הבסיס הקפואות:

| מדד | t424 |
|---|---:|
| net sum | 87.84% מהפקדה שנתית של 120K |
| שנים חיוביות | 7/7 |
| עסקאות | 1,073 |
| max closed DD | 9.83% |
| max tester equity DD | 10.05% |
| max stress loss | 24.08% |
| max leverage שנמדד | 1.916 |

ה־net, מספר השנים, stress, DD והמינוף המרבי מופיעים בסיכום t424. [docs/agents/grok_data/t424/RESULTS_t424.jsonL95-L110](https://github.com/nadavsbz/jev-xauusd/blob/35c079372c346b27e43c4e61e1069306fbad4467/docs/agents/grok_data/t424/RESULTS_t424.json#L95-L110) כל שבע הריצות בוצעו באיכות 100% real ticks, וה־equity DD המרבי היה 10.05% בשנת 2020. [docs/agents/grok_data/t424_tester/summary.jsonL8-L18](https://github.com/nadavsbz/jev-xauusd/blob/35c079372c346b27e43c4e61e1069306fbad4467/docs/agents/grok_data/t424_tester/summary.json#L8-L18)

---

# 2. C1d v2 — תקרה קשיחה

## 2.1 שינוי C1d-A: עיגול היתרה המותרת

### הכלל הקפוא

`CapDrift()` לא תחשב עוד כמות סגירה מעוגלת:

```text
close_lots = floor((current_lots - desired_lots) / step) × step
```

במקום זאת תחושב **היתרה המרבית החוקית שמותר להשאיר**:

```text
raw_allowed_remaining =
    current_abs_lots × MaxGross / measured_gross

allowed_remaining =
    floor(raw_allowed_remaining / volume_step) × volume_step
```

לאחר מכן:

```text
close_lots = current_abs_lots - allowed_remaining
```

כללים משלימים:

1. העיגול של `allowed_remaining` הוא תמיד כלפי מטה.
2. אם `0 < allowed_remaining < SYMBOL_VOLUME_MIN`, היתרה החוקית היא אפס והכרטיס ייסגר במלואו.
3. לא מעגלים את `close_lots` שוב כלפי מטה.
4. לאחר כל מילוי מחשבים מחדש את הפוזיציות בפועל ואת ה־gross.
5. `CapDrift()` אינה מדווחת הצלחה עד שכל הפוזיציות לאחר reconciliation נמצאות בתוך התקרה.
6. `TRADE_RETCODE_DONE_PARTIAL` מחייב חישוב מחדש והמשך ניסיון על היתרה בפועל.
7. לצורך gross, כל כרטיס נספר בערך מוחלט; BUY ו־SELL אינם מתקזזים.
8. מחיר notional יהיה:
   - `bid` לכרטיס BUY;
   - `ask` לכרטיס SELL;
   - אם אחד מהם חסר או לא חיובי, האכיפה נכשלת סגור ואינה מסמנת את הבר כמטופל.

הקוד הנוכחי מעגל את כמות השינוי ב־`Move()` ומחזיר הצלחה כאשר השינוי המעוגל קטן מהמינימום. [mql5/CryptoTrend_C1d.mq5L142-L162](https://github.com/nadavsbz/jev-xauusd/blob/35c079372c346b27e43c4e61e1069306fbad4467/mql5/CryptoTrend_C1d.mq5#L142-L162) בנוסף, `CapDrift()` הנוכחית משתמשת ב־`abs(NetLots)` ומסמנת את בר H1 לאחר שהקריאות ל־`Move()` הצליחו, גם בלי אימות gross חוזר. [mql5/CryptoTrend_C1d.mq5L165-L180](https://github.com/nadavsbz/jev-xauusd/blob/35c079372c346b27e43c4e61e1069306fbad4467/mql5/CryptoTrend_C1d.mq5#L165-L180)

### השפעה צפויה על הרווח

**כיוון צפוי: אפס עד שלילי.**

- השינוי רק מסיר חשיפה עודפת שנשארה בגלל step.
- בנקודת החריגה ההיסטורית, ההפרש בין `0.503` ל־`0.500` הוא כ־0.6% מן החשיפה המותרת.
- לכן ההשפעה הצפויה משינוי זה לבדו היא בסדר גודל של **נקודות בסיס עד עשיריות אחוז בנטו המצטבר**, לא שיפור מהותי.
- תוצאה חיובית קטנה אפשרית חשבונאית אם החשיפה שנחתכה הייתה מפסידה לאחר מכן, אך אין לפרש אותה כמטרת התיקון או כראיה לשיפור האות.

---

## 2.2 שינוי C1d-B: `CapDrift` שני לאחר ריבלנס H6

### סדר הפעולות הקפוא

בכל בר H6 חדש:

```text
1. CapDrift(PRE_H6)
2. Targets()
3. H6 rebalance
4. reconcile actual positions
5. CapDrift(POST_H6)
6. reconcile again
7. only then mark lastBar
```

כללים:

1. `POST_H6` חייב לרוץ גם אם `PRE_H6` כבר טיפל באותו בר H1.
2. לשתי הקריאות יהיו מזהי אירוע נפרדים; `lastH1` לא יחסום את הקריאה שלאחר הריבלנס.
3. `lastBar` יתעדכן רק אם:
   - כל הוראות הריבלנס הסתיימו;
   - כל הוראות `POST_H6` הסתיימו;
   - reconciliation מצא gross בתוך התקרה.
4. אם הוראת ריבלנס או cap נדחית או חלקית, אותו בר H6 ינוסה שוב בטיק הבא.
5. בזמן פתיחת תוספת בריבלנס מותר מראש רק הנפח שנכנס בתקציב gross שנותר.
6. סדר הפעולות בין סימולים יהיה:
   - תחילה הפחתות וסגירות;
   - לאחר reconciliation, תוספות;
   - בסוף `POST_H6`.
7. `RebalPct` אינו רשאי למנוע הפחתה שנדרשת כדי לעמוד ב־MaxGross.

בקוד v1 `CapDrift()` מופעלת לפני בדיקת בר H6, והריבלנס שאחריה אינו גורר אכיפה שנייה. [mql5/CryptoTrend_C1d.mq5L182-L199](https://github.com/nadavsbz/jev-xauusd/blob/35c079372c346b27e43c4e61e1069306fbad4467/mql5/CryptoTrend_C1d.mq5#L182-L199)

### השפעה צפויה על הרווח

**כיוון צפוי: אפס עד שלילי.**

- השינוי יכול רק למנוע תוספת חשיפה זמנית מעל התקציב.
- ברוב ברי H6 שבהם הריבלנס כבר מסיים מתחת ל־0.5, ההשפעה תהיה אפס.
- בברים שבהם `RebalPct`, עיגול או סדר הסימולים יוצרים חריגה, החשיפה תופחת מוקדם יותר.
- סדר הגודל הצפוי הוא **פחות מאחוז אחד מן הנטו המצטבר של t420**, אלא אם מתברר שהחריגות לאחר H6 נפוצות בהרבה מכפי שמשתקף ב־max gross ההיסטורי. במקרה כזה v2 תיכשל בשער הסטייה שלהלן ולא תיחשב תיקון מכני בלבד.

---

## 2.3 שינוי C1d-C: audit ב־`OnInit`

### audit חוסם וקפוא

לפני `INIT_SUCCEEDED`, ה־EA יסרוק את כל הפוזיציות בחשבון ויבדוק:

1. כל כרטיס עם `Magic=61001`.
2. כל כרטיס כזה נמצא רק ב־`Symbols` הקפואים.
3. אין BUY ו־SELL באותו סימול ובאותו Magic.
4. לכל סימול קיימים ערכים תקינים של:
   - `SYMBOL_TRADE_CONTRACT_SIZE`;
   - `SYMBOL_VOLUME_MIN`;
   - `SYMBOL_VOLUME_STEP`;
   - `SYMBOL_VOLUME_MAX`;
   - bid ו־ask.
5. אין EA אחר או מופע נוסף שידוע כי משתמש באותו Magic.
6. gross התחלתי מחושב כסכום הערך המוחלט של כל כרטיס, לא מן הנטו.
7. ה־equity חיובי.
8. אם gross התחלתי מעל 0.5, נרשמת חריגה מפורשת. ה־audit אינו מציג אותה כמצב תקין.

### מדיניות restart קפואה

לאחר audit תקין:

```text
lastH1  = current H1 bar
lastBar = current H6 bar
```

כלומר, attach או restart באמצע בר אינם יוצרים ריבלנס סינתטי על בר שכבר החל. האיזון האסטרטגי הבא יתקיים רק בגבול H6 הבא. ניטור cap יכול להתחיל מיד בטיק הראשון באמצעות קריאת audit/cap נפרדת, אך ללא חישוב אות מחדש באמצע H6.

### תוצאת audit

- כרטיס מחוץ לרשימת הסימולים, צדדים מנוגדים, מפרט חסר או equity לא תקין: `INIT_FAILED`.
- אין סגירה אוטומטית של פוזיציה לא מזוהה במסגרת `OnInit`.
- כל כשל נכתב ללוג עם ticket, symbol, type, volume ו־Magic.
- מצב נקי: `INIT_AUDIT_PASS`.

### השפעה צפויה על הרווח

- בריצה נקייה מתחילתה: **אפס בדיוק**, למעט הבדל אפשרי ביום הראשון אם v1 הייתה מבצעת ריבלנס מיד באמצע H6.
- ב־restart תקין: צפויה ירידה קטנה במחזור, לא שיפור מכוון ברווח.
- במצב חשבון לא תקין: אין להשוות רווח, משום שהריצה תיחסם ותסווג `OPERATIONAL-FAIL`.

---

## 2.4 שער קפוא ל־C1d v2

### שער תקינות מכני

כל התנאים נדרשים:

1. מיד לאחר כל `PRE_H6`, ‏`POST_H6`, attach-cap ו־H1-cap:

```text
actual_gross <= 0.500000 + 1e-6
```

ה־`1e-6` הוא epsilon חישובי בלבד, לא סבולת כלכלית.

2. אפס אירועים שבהם cap סומן כהצלחה וה־gross נשאר מעל התקרה.
3. אפס BUY/SELL מנוגדים באותו Magic וסימול.
4. אפס כרטיסי Magic מחוץ ל־`Symbols`.
5. אפס rebalances כפולים לאחר restart באמצע H6.
6. אותה סדרת אותות וכיווני יעד כמו v1 לפני יישום cap.
7. אותן תקופות, נתונים, inputs ומודל טסטר כמו t420.

### שער סטייה מול t420

הטווח הבא מוקפא מראש:

| מדד | בסיס t420 | תחום v2 מותר |
|---|---:|---:|
| נטו | 219,012.06 | **216,821.94–219,559.59** |
| שינוי נטו | — | ‎−1.00% עד ‎+0.25% מן הנטו |
| max L_H6 | 11.45% | לא מעל **11.55%** |
| max L_H24 | 21.12% | לא מעל **21.22%** |
| max L_H48 | 21.49% | דיווח; לא מעל **21.59%** |
| DD משוחזר | 13.51% | לא מעל **13.61%** |
| שנים חיוביות | 6/7 | לפחות **6/7** |
| max gross אחרי אכיפה | 0.503 | לא מעל **0.500001** |

**כישלון v2:** כל חריגה מן הטווח, גם אם היא משפרת רווח, מחייבת לסווג את השינוי כיותר מתיקון cap מכני. בפרט, עלייה של יותר מ־0.25% בנטו אינה “הצלחה”; היא מצביעה על שינוי מסלול מהותי או על אי־התאמה בין הריצות ודורשת הסבר ורישום חדש.

---

# 3. I2 v2 — תקרת לוט לפני כל כניסה

## 3.1 החישוב הקפוא

`SizeFor(d)` רשאית להמשיך לחשב את תנודתיות היום ואת לוט היעד האסטרטגי. אולם `dayLots` לא יהיה עוד אישור סופי לפתיחה.

לפני **כל** הוראת כניסה או היפוך:

```text
equity_now = ACCOUNT_EQUITY

cap_price =
    current ask, if opening LONG
    current bid, if opening SHORT

raw_cap_lots =
    MaxLev × equity_now
    / (cap_price × contract_size)

cap_lots =
    floor(raw_cap_lots / volume_step) × volume_step

entry_lots =
    min(dayLots, cap_lots, SYMBOL_VOLUME_MAX)
```

כללים:

1. `SymbolInfoTick()` חייב להצליח באותו tick שבו נשלחת ההוראה.
2. `ask > 0`, ‏`bid > 0`, ‏`equity_now > 0` ו־`contract_size > 0`; אחרת אין כניסה.
3. החישוב חוזר לפני כל retry בעקבות rejection או מילוי חלקי.
4. לאחר סגירת פוזיציה לצורך היפוך, מחשבים שוב equity, quote ו־cap; אין להשתמש בחישוב שבוצע לפני הסגירה.
5. אם `entry_lots < SYMBOL_VOLUME_MIN`, אין כניסה.
6. `MathFloor` מופעל רק בסוף, על `cap_lots` הסופי.
7. לוגיקת האות, `Want()`, אומדן התנודתיות ושעות המסחר אינם משתנים.
8. `dayLots` נשאר יעד אסטרטגי; `entry_lots` הוא הכמות המותרת בפועל.

ב־v1 הלוט מחושב לפי מחיר פתיחת היום `R[io].open` ו־equity בזמן `SizeFor()`, ולאחר מכן נשמר ב־`dayLots` ליתר היום. [mql5/IndexNoiseLev.mq5L107-L124](https://github.com/nadavsbz/jev-xauusd/blob/35c079372c346b27e43c4e61e1069306fbad4467/mql5/IndexNoiseLev.mq5#L107-L124) [mql5/IndexNoiseLev.mq5L213-L223](https://github.com/nadavsbz/jev-xauusd/blob/35c079372c346b27e43c4e61e1069306fbad4467/mql5/IndexNoiseLev.mq5#L213-L223) הפתיחה משתמשת ישירות ב־`dayLots`. [mql5/IndexNoiseLev.mq5L148-L156](https://github.com/nadavsbz/jev-xauusd/blob/35c079372c346b27e43c4e61e1069306fbad4467/mql5/IndexNoiseLev.mq5#L148-L156)

## 3.2 בדיקה לאחר מילוי

לאחר כל fill:

```text
actual_leverage =
    abs(actual_lots × contract_size × fill_price)
    / post_fill_equity
```

הערך נרשם אך אינו משנה את האות.

כדי להפריד בין cap של הקוד לבין תנאי ביצוע:

- **תקרת בקשה קשיחה:** `requested leverage <= 1.900000 + 1e-6`.
- **סבולת מילוי קפואה:** `actual leverage <= 1.9095`, כלומר עד 0.5% מעל 1.90 עקב החלקה ועמלת כניסה.
- כל fill מעל `1.9095` הוא `EXECUTION-CAP-FAIL`.
- בטסטר deterministic, ללא פער בין quote ל־fill שמסביר זאת, הדרישה היא `actual leverage <= 1.900001`.

אין להשתמש שוב בסבולת הישנה `1.989`: היא שייכת ל־t424 v1, שבו הסייזינג נעשה לפי מחיר פתיחת היום. הסבולת הישנה אכן נקבעה ב־PREREG של t424. [docs/agents/grok_data/t424/PREREG_t424.mdL11-L18](https://github.com/nadavsbz/jev-xauusd/blob/35c079372c346b27e43c4e61e1069306fbad4467/docs/agents/grok_data/t424/PREREG_t424.md#L11-L18)

## 3.3 השפעה צפויה על הרווח

**כיוון צפוי: אפס עד שלילי.**

- המינוף ההיסטורי המרבי ירד מ־1.916 לכ־1.90.
- ההפחתה המרבית בנקודה הזאת היא בקירוב:

```text
1 - 1.90 / 1.916 ≈ 0.835%
```

- רק כניסות שבהן `dayLots` גבוה מן התקרה העדכנית יושפעו.
- לכן ההשפעה הצפויה על הנטו המצטבר היא **נקודות בסיס עד פחות מחצי אחוז מן הנטו**, לא שיפור.
- שיפור קטן בפועל יכול להתרחש אם הכמות שנחתכה הייתה מפסידה, אך עלייה מהותית ברווח תיחשב אי־התאמה ולא הצדקה ל־v2.

---

## 3.4 שער קפוא ל־I2 v2

### שער תקינות מכני

1. אפס הוראות כניסה שבהן requested leverage גדול מ־`1.900001`.
2. אפס fills מעל `1.9095`.
3. חישוב cap חדש לכל פתיחה, retry והיפוך.
4. אותה סדרת אותות, כיוונים וזמני כוונה כמו t424.
5. מספר עסקאות יכול לרדת רק אם הכמות החוקית נמוכה מ־minimum lot; כל מקרה כזה חייב להופיע בלוג.
6. אפס פתיחות עם quote או equity ישנים.

### שער סטייה מול t424

| מדד | בסיס t424 | תחום v2 מותר |
|---|---:|---:|
| net sum | 87.84% | **86.96%–88.06%** |
| שינוי נטו | — | ‎−1.00% עד ‎+0.25% מן הנטו |
| שנים חיוביות | 7/7 | **7/7** |
| max closed DD | 9.83% | לא מעל **9.93%** |
| max tester equity DD | 10.05% | לא מעל **10.15%** |
| max stress loss | 24.08% | לא מעל **24.18%** |
| max requested leverage | לא נמדד בנפרד | **1.900001** |
| max realized leverage | 1.916 | **1.9095** |
| median hold | 120 דקות | **120 דקות**, למעט סטיית tick ביצוע |
| max open per side | 1 | **1** |

גם כאן, עלייה בנטו מעל הגבול העליון אינה מעבר: התיקון אינו אמור לשפר את האות או להוסיף חשיפה.

---

# 4. לוג P2 קפוא

## 4.1 פורמט

כל שורה תהיה רשומת CSV או JSONL יחידה, עם סדר שדות קבוע. לכל אירוע יוקצה:

```text
schema_version
ea_version
build_hash
run_id
event_id
server_time_ms
event_type
symbol
magic
ticket
direction
reason
equity_before
equity_after
bid
ask
decision_price
fill_price
contract_size
volume_min
volume_step
volume_max
raw_target_weight
raw_target_lots
allowed_remaining_lots
requested_lots
filled_lots
position_lots_before
position_lots_after
gross_before
gross_after
max_gross
estimated_vol
raw_leverage
capped_leverage
requested_leverage
realized_leverage
max_leverage
retcode
retcode_description
reconciliation_status
```

## 4.2 סוגי אירועי C1d

```text
INIT_AUDIT_START
INIT_AUDIT_POSITION
INIT_AUDIT_PASS
INIT_AUDIT_FAIL
CAP_PRE_H1
CAP_REQUEST
CAP_FILL
CAP_POST_H1
H6_REBALANCE_START
H6_REBALANCE_REQUEST
H6_REBALANCE_FILL
CAP_POST_H6
H6_REBALANCE_COMPLETE
RECONCILIATION_FAIL
```

## 4.3 סוגי אירועי I2

```text
SIZE_DAILY
ENTRY_CAP
ENTRY_REQUEST
ENTRY_FILL
ENTRY_REJECT
ENTRY_PARTIAL
EXIT_REQUEST
EXIT_FILL
POST_FILL_LEVERAGE
RECONCILIATION_FAIL
```

## 4.4 כללי תקינות הלוג

1. כל כוונת ביצוע מקבלת `event_id` יציב שמקשר בין target, request, fill ו־reconciliation.
2. גם הוראה שלא נשלחה בגלל minimum lot נרשמת.
3. גם cap שלא שינה כמות נרשם.
4. אין לעדכן `lastBar` או `lastH1` לפני כתיבת רשומת reconciliation.
5. חסר בלוג באירוע שבו הייתה חשיפה הוא `LOGGING-FAIL`.
6. הלוג אינו משמש לשינוי החלטות בזמן הריצה, למעט כשל כתיבה אם נקבע מראש ש־telemetry היא דרישת בטיחות.

## 4.5 השפעה צפויה על הרווח

**אפס בדיוק.**

הלוג אינו רשאי:

- לשנות signal;
- לשנות sizing;
- לעכב הוראה לצורך I/O סינכרוני;
- לשנות `lastBar` או state;
- לבצע retry נוסף.

אם הפעלת הלוג משנה trade count, timestamps, requested lots או P&L מעבר לדיוק מספרי, v2 נכשלת. השפעה מותרת על נטו: **0.00**, פרט להבדלי floating-point שאינם משנים לוט או הוראה.

---

# 5. סדר הריצות הקפוא

כדי לייחס כל שינוי לסיבה אחת בלבד:

1. **R0 — שחזור v1:** קומפילציה והרצה מחדש של הקוד הקיים. חייב לשחזר את t420/t424 בתוך דיוק הדוחות.
2. **R1 — לוג בלבד:** אותו קוד עם P2 logging. תוצאות המסחר חייבות להיות זהות ל־R0.
3. **R2 — שינוי יחיד:**
   - C1d: עיגול allowed remaining בלבד;
   - I2: cap עדכני לפני כל כניסה בלבד.
4. **R3 — C1d:** הוספת `POST_H6 CapDrift`.
5. **R4 — C1d:** הוספת `OnInit` audit ומדיניות restart.
6. **R5 — v2 מלאה:** כל השינויים יחד.

אין לשנות בין הריצות:

- פרמטרים;
- סדר סימולים;
- `RebalPct`;
- שעות;
- lookbacks;
- נתונים;
- מודל הטסטר;
- הפקדה;
- commission או spread;
- קוד signal.

אם R0 אינה משחזרת את הבסיס, כל השוואת v2 היא `INVALID`.

---

# 6. מבחני יחידה ותפעול שחייבים לעבור

## C1d

1. פוזיציה של `0.01` לוט כאשר `0.01` משקף gross של `0.503`:
   - allowed remainder חייב להיות `0.00`;
   - הפוזיציה נסגרת;
   - gross לאחר reconciliation אינו מעל 0.5.
2. שתי פוזיציות שבהן הפחתה באחת ותוספת בשנייה:
   - הפחתות מבוצעות ראשונות;
   - תוספת אינה יכולה להעלות gross מעל 0.5.
3. BUY ו־SELL באותו Magic וסימול:
   - `OnInit` נכשל;
   - אין קיזוז ל־gross אפס.
4. כרטיס באותו Magic בסימול לא מוכר:
   - `OnInit` נכשל.
5. restart באמצע H6:
   - אין ריבלנס מיידי נוסף;
   - אין הוראה כפולה.
6. מילוי חלקי:
   - reconciliation ממשיך מן הנפח שנותר בפועל.
7. דחייה:
   - `lastBar`/`lastH1` אינם מתקדמים כאילו הפעולה הצליחה.

## I2

1. לונג: cap מחושב מ־ask הנוכחי.
2. שורט: cap מחושב מ־bid הנוכחי.
3. ירידת equity בין sizing יומי לכניסה:
   - lot הכניסה קטן בהתאם.
4. שינוי מחיר של 0.85% מאז פתיחת היום:
   - המינוף המבוקש עדיין אינו עובר 1.90.
5. היפוך:
   - cap מחושב מחדש אחרי הסגירה.
6. retry:
   - quote ו־equity נקראים מחדש.
7. cap מתחת ל־minimum lot:
   - אין כניסה ונכתבת רשומת `ENTRY_CAP`.
8. עמלה או החלקה שיוצרות realized leverage מעל 1.9095:
   - הריצה מסומנת `EXECUTION-CAP-FAIL`.

---

# 7. הכרעה מוגדרת מראש

v2 תסווג:

- **VALID-MECHANICAL** — כל invariants ושערי הסטייה עברו.
- **FAIL-CAP** — תקרת gross/requested leverage הופרה.
- **FAIL-DEVIATION** — תוצאות t420/t424 סטו מעבר לטווח, גם אם הסטייה שיפרה רווח.
- **FAIL-AUDIT** — audit לא זיהה או לא חסם מצב לא חוקי.
- **FAIL-LOGGING** — אין שרשרת מלאה מ־target ועד reconciliation.
- **INVALID-BASELINE** — v1 לא שוחזרה לפני בדיקת v2.
- **EXECUTION-CAP-FAIL** — cap הבקשה תקין אך fill בפועל עבר את סבולת הביצוע.

מעבר טכני של הרישום, אם יתרחש, יהיה לכל היותר ראיה לכך שהשינוי מיישם את התקרות בלי לשנות מהותית את האסטרטגיות. הוא **לא** יהיה אישור שער, דמו או מסחר.

## בדיקות שבוצעו לצורך ההצעה

- ✅ `cat AGENTS.md`
- ✅ `nl -ba docs/research/t427_review_20261127.md`
- ✅ `nl -ba docs/agents/grok_data/t420/PREREG_t420.md`
- ✅ `nl -ba docs/agents/grok_data/t420/RESULTS_t420_A4.md`
- ✅ `python -m json.tool docs/agents/grok_data/t424/RESULTS_t424.json`
- ✅ `nl -ba docs/agents/grok_data/t424_tester/summary.json`
- ✅ `nl -ba mql5/CryptoTrend_C1d.mq5 | sed -n '120,215p'`
- ✅ `nl -ba mql5/IndexNoiseLev.mq5 | sed -n '100,240p'`
- ✅ `git status --short --branch` — עץ העבודה נקי; בהתאם לבקשה, לא שונו קבצים ולא נוצרו commit או PR.

 [View task →](https://chatgpt.com/s/cd_6b091ebe27d48191832ec61622708f2c)
