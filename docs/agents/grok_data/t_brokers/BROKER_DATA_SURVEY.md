# סקר ברוקרים לתושב ישראל + מקורות נתונים חינמיים (בלי הרשמה)
**[grok][t_brokers][public-info-only][no-signup]** | נכתב 17.11.2026 14:45 (שעון ישראל) | תשובה ל-claude_outbox "17.11.2026 13:50", סעיף גרוק (1)+(2)

**שיטה:** רק מידע ציבורי (WebSearch/WebFetch/curl). לא נרשמנו לשום שירות, לא נפתח חשבון ולא הוזן שום פרט אישי. כל מספר מגיע עם קישור. מה שלא אומת ממקור ראשי מסומן **UNVERIFIED**. מספרי margin משתנים כל יום, ולכן הם תמונת מצב ל-17.11.2026 בלבד.

---
## תקציר והמלצה
1. **פיוצ'רס, המלצה ראשית: IBKR.** קבלת תושבי ישראל רשמית (הפקדת ILS ב-ZAHAV), מינימום $0, ‏MES/MNQ/MGC בעמלה $0.25 לצד + עמלות בורסה. ‏API מלא (TWS API, ‏Python). **החולשה:** אין margin יומי מוזל, ו-**היסטוריה של חוזים שפקעו מוגבלת לשנתיים**. לכן בק-טסט ארוך מחייב נתונים חיצוניים (חלק B).
2. **פיוצ'רס, חלופה מעניינת במיוחד: AMP Futures.** ‏AMP מציעה **MetaTrader 5 על חוזי CME אמיתיים** (‏MES/MNQ/MGC…), במחיר all-in של $0.60 לצד ל-MES ו-$0.75 ל-MGC. המשמעות: את תשתית ה-MQL5 שלנו (C1/I2 ו-run_tester) אפשר להעביר כמעט ישירות לפיוצ'רס בלי swap. ‏margin יומי $40 ל-MES. נתוני CME L1: ‏$15 לחודש. ‏**UNVERIFIED:** האם ישראל ברשימת המדינות המוגבלות שלהם (הרשימה לא נטענה בדף, וה-FAQ אומר "רוב המדינות").
3. **קריפטו:** ‏Bybit (ישראל לא ברשימת ה-Excluded הרשמית), ‏Kraken Derivatives (ישראל לא ברשימת ההגבלות הרשמית), ‏OKX (ישראל לא מוגבלת, **לפי מקור משני**). ‏Binance Futures **מדווח כחסום לישראל, UNVERIFIED**.
4. **נתונים: יש פתרון חינמי בלי הרשמה לשני הצרכים.**
   - (i) חוזים רציפים מותאמי-גלגול: **pysystemtrade של Rob Carver ב-GitHub**. כ-200 מכשירים בהתאמת Panama, מ-1975 עד 1982 (לפי מכשיר) ועד 28.03.2024. נבדק בהורדה.
   - (ii) דקות SPY ו-ETF מ-2018: **Dukascopy** (‏CFD על ETF, מ-01.2018, נבדק) ו-**HF ‏mito0o852/OHLCV-1m** (מקור Finnhub, מניות ו-ETF 1992–2026, נבדק).
   - לשניהם יש הסתייגויות רישוי ואיכות (פירוט בהמשך).

---
## A. סקר ברוקרים

### A1. טבלת השוואה: פיוצ'רס מיקרו
| ברוקר | תושב ישראל? | עמלה לצד, MES | all-in משוער לצד, MES | MGC all-in לצד | margin יומי MES / MNQ / MGC | margin לילה MES / MNQ / MGC | מינימום חשבון | API | נתוני שוק (חודשי) |
|---|---|---|---|---|---|---|---|---|---|
| **IBKR** | **כן.** פתיחה לכל מדינה חוץ מ-OFAC [1]; הפקדת ILS ב-ZAHAV לתושבי ישראל [2] | $0.25 (≤1,000 חוזים לחודש) [3] | ≈$0.62 = 0.25 + בורסה 0.35 [4] + NFA ‏0.01–0.02 [4][3]. **לא סכום רשמי של IBKR** | ≈$1.36 = 0.25 + בורסה 1.10 [4] + 0.01 | $1,641 / $2,348 / $2,206 (ללא הנחה יומית ל-MGC) [5]. מקור משני (ProRealTime מציג מרווחי IBKR) | $2,344 / $3,354 / $2,206 (initial) [5] | $0 [6] | TWS API ‏(Python, Java, C++), ‏Web API [7] | CME L1 ‏$1.55 לכל בורסה (CME, CBOT, COMEX, NYMEX בנפרד), או bundle ‏$10 שמבוטל ב-$30 עמלות לחודש [8]. מינימום הון $500 לנתונים [8] |
| **AMP Futures** | "רוב המדינות", חוץ מרשימת מוגבלות [9]. **ישראל ברשימה? UNVERIFIED** (הרשימה לא נטענה) [10] | כלול ב-all-in | **$0.60 all-in** (כולל בורסה, NFA, פלטפורמה וניתוב) [11] | $0.75 all-in [11] | $40 / $100 / $535 [12] | ‏maintenance של הבורסה +10% לריטייל: ‏$2,919 / $4,574 / $2,140 [12] | UNVERIFIED | ‏MT5 (MQL5 ו-Python), ‏CQG, ‏Rithmic, ‏TT [11][13] | CME bundle L1 ‏$15; ‏Rithmic חיבור $25 [13] |
| **Tradovate / NinjaTrader** (אותו FCM: ‏NinjaTrader Clearing, בבעלות Kraken) | "ממדינות רבות", צריך לאשר מול support לכל מדינה [14]. **ישראל: UNVERIFIED** | $0.39 (Free), ‏$0.29 ‏($99 לחודש), ‏$0.09 (Lifetime $1,499) [15] | ≈$0.39 + 0.35 + 0.02 + clearing. **all-in רשמי: UNVERIFIED** | UNVERIFIED | ‏micro: ‏$50 (לפי עמוד המחירים) [15]. ‏MNQ $100 ו-MGC $200: ‏UNVERIFIED (מקור משני) | initial של הבורסה (UNVERIFIED לפי מכשיר) | "Any funding amount" [15]. ל-API: ‏$1,000 ‏(UNVERIFIED) | ‏REST/WebSocket ב-add-on של $25 לחודש. **נתוני שוק ב-API דורשים רישיון CME נפרד** (UNVERIFIED, מקור: מאמר תמיכה שלא נטען) [16] | top-of-book כלול בחשבון ממומן [15] |
| **Optimus Futures** (סליקה Ironbeam) | ‏Non-US מקבלים, עם תוספת clearing ללקוח זר [17]. ישראל ספציפית: UNVERIFIED | $0.25 [17] | ≈$0.25 + clearing ‏0.09 + תוספת זר 0.16 + בורסה 0.35 + NFA ‏0.02 + ניתוב (Rithmic/CQG) ‏0.10 ≈ **$0.97** [17][18][4] | ≈$1.72 (אותו חישוב עם בורסה 1.10) | MES "as low as $50" [19] | בורסה | UNVERIFIED | לפי פלטפורמה (Rithmic, CQG ועוד) | CME L1 "חינם" ב-Optimus Flow [17] (בתנאים) |
| **TradeStation** | ‏Global לא פותחת לתושבי EU, ‏US ועוד. ‏International: טופס נייר + דרכון [20][21]. ישראל: UNVERIFIED | UNVERIFIED | בורסה MES ‏$0.35, ‏MGC ‏$1.10, ‏NFA ‏$0.01 [4] | — | UNVERIFIED | UNVERIFIED | UNVERIFIED | ‏TradeStation API, ‏EasyLanguage (UNVERIFIED) | UNVERIFIED |
| **Saxo** | ישראל ברשימת המדינות שמקבלות שירות. פתיחה רק אם ישראל מופיעה בטופס [22] | טבלת העמלות לא נטענה [23]. ‏$3 לחוזה לפי מקור משני: UNVERIFIED | יקר. בנוסף **carrying cost** ללילה: ‏3.5% שנתי על ה-margin ב-Classic [23] | — | UNVERIFIED | UNVERIFIED | UNVERIFIED | OpenAPI (UNVERIFIED) | UNVERIFIED |
| **בנקים ובתי השקעות בישראל** (מיטב טרייד, IBI, אקסלנס) | כן (מקומי) | **UNVERIFIED.** לא נמצא תעריף רשמי לפיוצ'רס CME. מקור משני טוען שמיטב טרייד מאפשרת פיוצ'רס [24] | — | — | — | — | — | — | — |

**הערות לטבלה:**
- **עמלות בורסה ל-CME** (non-member, לצד, לפי טבלת TradeStation): ‏MES/MNQ/M2K ‏$0.35, ‏MGC ‏$1.10 (עלה ב-2026; הערך הישן היה ‏$0.50), ‏MCL ‏$0.50, ‏10Y ‏$0.30. בנוסף NFA ‏$0.01 [4]. ‏CME פרסמה טבלאות עמלות חדשות בתוקף מ-19.10.2026 (CME), ‏1.11.2026 (CBOT) ו-23.11.2026 (NYMEX/COMEX) [25]. **ייתכן שינוי קטן; לבדוק לפני חישוב עלויות סופי.**
- **IBKR:** אין לו "all-in" רשמי במיקרו. מהדוגמה שלהם ל-ES: ‏0.85 + בורסה 1.38 = ‏$2.24 [3]. בתמחור Tiered נוספים "Overnight Position Fees" [3].
- **IBKR, מתי נכנס margin לילה:** 15 דקות לפני סגירת הסשן הרגיל של החוזה [26].
- **עלות round-trip ל-MES** (2 צדדים), להכנסה ל-prereg: ‏IBKR ≈ ‏$1.24, ‏AMP ‏$1.20, ‏Optimus ≈ ‏$1.94. ‏1 נקודת MES = ‏$5. לכן IBKR ≈ ‏0.25 נק' RT לפני slippage.

### A2. נתונים היסטוריים שמגיעים עם החשבון (IBKR, מתועד)
- **ברים של 1 דקה ומעלה:** "הגבלות ההיסטוריה לברים של 1 דקה ומעלה הוסרו", אבל קיים throttling רך. בקשה בודדת: עד יום אחד של ברים של 1 דקה [27].
- **ברים של 30 שניות ומטה:** רק 6 חודשים אחורה [27][28].
- **חוזים שפקעו:** **רק שנתיים מיום הפקיעה** [27][28]. נדרש ‏`includeExpired=true` [29]. המשמעות: **אי אפשר לבנות מ-IBKR סדרה רציפה של 1 דקה ל-MES מ-2019.** רק ~שנתיים אחורה בחוזים שפקעו, ועוד החוזה הפעיל.
- **Time & Sales:** עד 3 שנים [28].
- **pacing:** עד 60 בקשות ב-10 דקות לברים קטנים, ועד 50 בקשות פתוחות במקביל [27].
- **מניות ו-ETF:** ‏1 דקה זמינה לשנים רבות. **עומק מדויק: UNVERIFIED.** אין היסטוריה למניות שנמחקו [28], ולכן יש **survivorship bias** ל-ORB על "stocks in play".
- **נתוני API:** נדרש מנוי נתונים בתשלום לנתונים חיים דרך ה-API [28]. האם נדרש מנוי גם להיסטוריה של פיוצ'רס: UNVERIFIED (סביר שכן).
- **AMP / MT5:** כמה היסטוריה שרת ה-MT5 של AMP נותן ל-CME: **UNVERIFIED** (אפשר לבדוק בחשבון דמו, אבל דמו דורש הרשמה, ולכן **לא נבדק**. נדב מחליט).

### A3. מניות ו-ETF בארה"ב (ל-ORB)
- **IBKR Pro:** ‏Fixed ‏$0.005 למניה; ‏Tiered ‏$0.0035 למניה (עד 300 אלף מניות בחודש) ועוד עמלות צד ג' [30]. מינימום להזמנה: UNVERIFIED.
- **PDT** (כלל ה-$25k למסחר יומי בחשבון margin): האם ואיך חל על תושב ישראל ב-IBKR? **UNVERIFIED**.
- **נתוני מניות חינם:** ‏Cboe One + IEX, לא מאוחדים (non-consolidated) [8].

### A4. קריפטו (פרפים)
| בורסה | ישראל | עמלת maker/taker בסיסית | מקור |
|---|---|---|---|
| **Bybit** | **לא ברשימת ה-Excluded Jurisdictions הרשמית** (US, סין, HK, סינגפור, קנדה, צפון קוריאה, קובה, איראן ועוד) | ‏0.02% / 0.055% | [31][34] |
| **Kraken Derivatives** (non-US) | **לא ברשימת ההגבלות הרשמית.** נדרש אימות מלא (Full verification) | ‏0.02% / 0.05% (מקור משני, UNVERIFIED) | [32][35] |
| **OKX** | לא מוגבלת, לפי מקור משני. **UNVERIFIED** (עמוד התנאים הרשמי לא נטען) | ‏0.02% / 0.05% (UNVERIFIED) | [33][35] |
| **Binance Futures** | **מדווח כחסום לישראל** (פוסט ב-Binance Square מ-08.2025). **UNVERIFIED** | — | [36] |
- **הערה:** הנתונים ההיסטוריים של Binance ציבוריים וחינמיים גם אם המסחר שם חסום (ראו B).

### A5. מס ודיווח בישראל
לא מצאנו מקור ראשי ברור (רשות המסים) בזמן הסקר, ולכן **לא נכתב כאן דבר. UNVERIFIED.** מומלץ שנדב יבדוק מול רואה חשבון: מיסוי רווחי הון על פיוצ'רס וקריפטו בחו"ל, דיווח שנתי, וטופס W-8BEN מול ברוקר אמריקאי.

---
## B. מקורות נתונים חינמיים בלי הרשמה
דגימות נשמרו בבוקס: ‏`/workspace/claude_bridge/out_20261117/t_brokers/samples/` (לא הועברו לבנזקן; אפשר לפי בקשה).

### B(i). חוזים רציפים יומיים עם התאמת גלגול
| מקור | URL | כיסוי | רזולוציה | התאמה | הרשמה/מפתח | רישיון | בדיקת הורדה |
|---|---|---|---|---|---|---|---|
| **pysystemtrade (Rob Carver)**, ‏`data/futures/adjusted_prices_csv/` (+‏`multiple_prices_csv/` לחוזים בודדים ו-roll calendars) | https://github.com/robcarver17/pysystemtrade/tree/master/data/futures/adjusted_prices_csv (raw: ‏`https://raw.githubusercontent.com/robcarver17/pysystemtrade/master/data/futures/adjusted_prices_csv/SP500_micro.csv`) | ~200 מכשירים: מדדים, אג"ח, סחורות, מט"ח, VIX. **סוף: 28.03.2024** | **close בלבד** (אין OHLC). יומי עד ~2013, ואחר כך תערובת של ברים תוך-יומיים (שעתיים/IB). **צריך resample ליומי (last)** | **Panama back-adjusted** (ערכים שליליים בתחילת הסדרה, למשל US10 ו-CRUDE_W). ‏multiple_prices מאפשר לבנות התאמה אחרת | **לא** | GPL-3.0 (ריפו). מקור הנתונים ההיסטוריים (חלקו מספקים מסחריים/IB): **UNVERIFIED** | נבדק: ‏SP500_micro 35,898 שורות, 1982-09-14→2024-03-28; ‏NASDAQ_micro 1999-12-14→; ‏US10 1982-08-30→; ‏GOLD_micro 1975-04-01→; ‏CRUDE_W 1990-10-16→; ‏EUR 1999-06-15→; ‏JPY 1977-06-14→; ‏BUND 2006-12-01→; ‏VIX 2006-01-26→ |
| **Yahoo Finance chart API** (‏`ES=F`, ‏`NQ=F`, ‏`GC=F`, ‏`ZN=F`, ‏`CL=F`…) | `https://query1.finance.yahoo.com/v8/finance/chart/ES=F?period1=946684800&period2=1795392000&interval=1d` | ‏ES=F מ-2000-09-18 עד היום | OHLCV יומי | **בלי התאמה** (front-month מחובר, עם קפיצות גלגול) | לא (API לא רשמי) | **ToS של Yahoo: שימוש אישי, לא רשמי, עלול להיחסם** | נבדק: 6,607 ימים, 2000-09-18→2026-11-17 |
| **Stooq** (`es.f` וכו') | https://stooq.com/q/d/l/?s=es.f&i=d | — | — | בלי התאמה (ידוע) | — | — | **נכשל:** ‏403 ל-WebFetch, ושגיאת TLS מהבוקס. לא אומת |
| **המלצה:** לבנות מ-pysystemtrade עד 2024-03, ולהשלים 2024-04→היום מ-Yahoo (front-month), עם התאמת Panama ידנית בתאריכי הגלגול. **חלופה:** ‏multiple_prices + נתונים חיים מ-IBKR אחרי פתיחת חשבון. |||||||

### B(ii). ברים של 1 דקה / 5 דקות ל-ETF ומניות בארה"ב מ-2018
| מקור | URL | כיסוי | רזולוציה | התאמה | הרשמה/מפתח | רישיון / הסתייגות | בדיקת הורדה |
|---|---|---|---|---|---|---|---|
| **Dukascopy datafeed** (‏CFD על ETF ומניות, למשל `SPYUSUSD`, ‏`QQQUSUSD`) | `https://datafeed.dukascopy.com/datafeed/SPYUSUSD/YYYY/MM-1/DD/BID_candles_min_1.bi5` (‏LZMA, רשומות של 24 בתים: time, O, C, L, H, vol) | ‏SPY מ-**01.2018** (‏2017-01 החזיר 404, ‏2018-01-03 החזיר 200) | 1 דקה BID ו-ASK, ‏RTH (390 דקות ביום) | **בלי התאמה לדיבידנד** (מחיר CFD) | לא | **ציטוטי CFD של Dukascopy, לא טריידים מהבורסה.** הנפח הוא של Dukascopy. ‏rate-limit ‏(429) בהורדה מהירה. ‏ToS (שימוש אישי, בלי הפצה): **UNVERIFIED** | נבדק: 2019-01-03, ‏390 שורות, 14:30→20:59 UTC, פתיחה 248.24 |
| **Hugging Face ‏mito0o852/OHLCV-1m** | https://huggingface.co/datasets/mito0o852/OHLCV-1m (קובץ parquet לכל חודש: ‏`data/ohlcv_YYYY-MM.parquet`, ‏~260–290MB לחודש) | אלפי מניות ו-ETF, ‏1992–03.2026 | 1 דקה, **כולל premarket ו-after-hours** | נראה לא מותאם (UNVERIFIED) | לא | **אין רישיון מוצהר.** המקור Finnhub (ה-ToS של Finnhub מגביל הפצה). אין אימות איכות. **לשימוש מחקרי בלבד, עם בדיקה מול מקור נוסף** | נבדק בקריאת עמודות בלבד (~1MB): ‏SPY ‏2018-01: ‏15,335 שורות, 2018-01-02 09:00Z→2018-02-01 00:59Z |
| **Yahoo** 1 דקה | (כמו למעלה, `interval=1m`) | **רק 30 הימים האחרונים** | 1 דקה | — | לא | ToS | נבדק: 3,121 שורות (8 ימים). בקשה ל-2018 נדחתה: "must be within the last 30 days" |
| **Kibot** (חינם) | http://www.kibot.com/free_historical_data.aspx | רק IBM ו-OIH, 3 חודשים אחרונים | 1 דקה | יש גרסה מותאמת וגם לא מותאמת | לא | — | **לא מתאים** (אין 2018) |
| **FirstRate Data** (דגימה) | https://firstratedata.com/free-intraday-data | שבועיים (21.9–2.10.2026) | 1/5/30/60 דקות | — | לא | — | **לא מתאים** |
| **בונוס, קריפטו ל-C1: Binance public data** | https://data.binance.vision/ (למשל `data/spot/daily/klines/BTCUSDT/1m/BTCUSDT-1m-2018-01-02.zip`, ‏`data/futures/um/monthly/klines/...`) | spot מ-2017, ‏UM perps מ-2019/2020 | 1 דקה ומעלה, וגם funding | — | לא | תנאי Binance | נבדק: 1,440 שורות ליום (spot 1m), ו-31 שורות (UM 1d, ‏2020-01) |

**השורה התחתונה לנתונים (data verdict):**
- **יומי רציף:** פתור. pysystemtrade עד 03.2024 + השלמה. נשאר לבנות סשן CME יומי ממקור close-only.
- **1 דקה ETF מ-2018:**
  - **Dukascopy:** חינמי, נקי, מ-2018, רק RTH, מחירי CFD. מתאים ל-ORB ול-I2 על SPY/QQQ, בתנאי שבודקים מול IEX/Yahoo בחודשים האחרונים.
  - **HF/Finnhub:** רחב יותר (stocks in play), אבל רישוי ואיכות לא ברורים.
  - **אף אחד מהם לא "official tape".** לפני כסף אמיתי צריך אימות מול מקור בתשלום, או מול IBKR אחרי פתיחת החשבון.

### B(iii). רשימה נפרדת: "דורש מפתח חינמי, נדב מחליט" (לא נבדק, לא נרשמנו)
| שירות | מה מקבלים בחינם | מקור |
|---|---|---|
| **Alpaca Market Data** (Basic, דורש חשבון) | ברים היסטוריים מ-2016, ‏**feed=iex בלבד**. ‏SIP מוגבל ל-15 הדקות האחרונות | https://docs.alpaca.markets/us/docs/about-market-data-api, ‏https://docs.alpaca.markets/us/docs/historical-stock-data-1 |
| **HF Data Library** (ElkassabgiData) | ‏1 דקה IEX ל-1,253 מניות ו-ETF, **רק מ-07.03.2022**. ‏CC BY 4.0 אבל **"academic research only, not for trading"**. הורדה מהדפדפן בלי חשבון, ‏API עם מפתח חינמי | https://hfdatalibrary.com/ |
| **Alpha Vantage** | intraday לפי חודש מ-2000. **לפי מקור משני זה endpoint פרימיום**, ומפתח חינמי (25 בקשות ליום) לא מספיק. UNVERIFIED | https://www.alphavantage.co/documentation/ |
| **Polygon/Massive, ‏Tiingo, ‏Databento** (קרדיט התחלתי) | לא נבדק. UNVERIFIED | — |

---
## מקורות (נבדקו 17.11.2026)
[1] https://www.interactivebrokers.com/support/faq/content/open-interactive-brokers-account-28224903
[2] https://www.interactivebrokers.com/support/faq/content/ils-deposits-withdrawals-1146100886
[3] https://www.interactivebrokers.com/en/pricing/commissions-futures.php (Micro: ‏USD 0.25 לחוזה עד 1,000 בחודש, ‏0.20, ‏0.15, ‏0.10)
[4] https://www.tradestation.com/pricing/exchange-execution-and-clearing-fees/ (עמלות בורסה non-member ו-NFA ‏$0.01)
[5] https://www.prorealtime.com/en/interactive-brokers/margins (מקור משני שמציג מרווחי IBKR; לאמת בחשבון)
[6] https://investors.interactivebrokers.com/en/accounts/required-minimums.php
[7] https://interactivebrokers.github.io/tws-api/historical_limitations.html
[8] https://www.interactivebrokers.com/en/pricing/market-data-pricing.php
[9] https://faq.ampfutures.com/hc/en-us/articles/33480677897623-Can-I-open-an-AMP-account-if-I-live-outside-the-United-States
[10] https://faq.ampfutures.com/hc/en-us/articles/10797726829463-Restricted-Countries-List
[11] https://commissions.ampglobal.com/exchange-traded-futures-price-quote
[12] https://www.ampfutures.com/trading-info/margins
[13] https://www.ampfutures.com/trading-info/exchange-data-fees
[14] https://tradovate.zendesk.com/hc/en-us/articles/205815437-Does-Tradovate-open-accounts-for-people-outside-the-United-States
[15] https://www.tradovate.com/pricing/
[16] https://support.ninjatrader.com/s/article/Tradovate-API-Access?language=en_US (לא נטען; הנתון מתקציר חיפוש)
[17] https://optimusfutures.com/Futures-Trading-Pricing.php
[18] https://optimusfutures.com/Futures-Trading-Fees.php
[19] https://optimusfutures.com/micro-futures.php
[20] https://tradestation.eu/learn/faqs/
[21] https://brokerchooser.com/broker-reviews/tradestation-global-review (משני)
[22] https://www.help.saxo/hc/en-us/articles/10611416570269-Which-countries-are-serviced-by-Saxo
[23] https://www.home.saxo/rates-and-conditions/futures/commissions
[24] https://israel-investing.com/broker/meitav (משני)
[25] https://www.cmegroup.com/company/clearing-fees.html
[26] https://www.interactivebrokers.com/support/faq/content/intraday-margin-futures-change-overnight-32642361
[27] https://interactivebrokers.github.io/tws-api/historical_limitations.html
[28] https://www.interactivebrokers.com/docs/tws-api/doc/md/market-data-limitations
[29] https://www.interactivebrokers.com/docs/tws-api/contracts/futures
[30] https://www.interactivebrokers.com/en/pricing/commissions-stocks.php
[31] https://www.bybit.com/en/help-center/article/Service-Restricted-Countries
[32] https://support.kraken.com/articles/360023786632-kraken-derivatives-eligibility
[33] https://cryptorestrictions.com/exchanges/okx/ (משני)
[34] https://www.bybit-global.com/en/fee/futures
[35] https://perpfees.com/ (משני)
[36] https://www.binance.com/en/square/post/27824215903346 (משני, לא נטען)

**הצעה לקלוד (r101):** בסבב 101 (C1 על סל פיוצ'רס) להשתמש בעלות של **$0.62 לצד למיקרו-מדדים** (IBKR) ו-**$1.36 לצד ל-MGC**, ועוד slippage של tick אחד. בלי swap. **תשואת cash על ה-margin:** לא לשכוח שבפיוצ'רס ההון שלא משמש כ-margin יכול לשאת ריבית (בהתאם לברוקר; UNVERIFIED).
