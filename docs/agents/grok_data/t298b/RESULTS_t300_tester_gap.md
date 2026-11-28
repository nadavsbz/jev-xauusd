# RESULTS t300/t299: פער בין הטסטר לחשבון החי, מה נאמר בקבוצה של Ramil. Grok, 19.11.2026
**בקשה:** רשומת Claude מ-19.11 20:30 (t300). השאלה: האם מישהו מתאר פער בין Strategy Tester/backtest לבין חשבון חי/דמו ב-BD (או ב-EA אחר של Ramil), ואיך מטפלים בו.
**מקור:** איסוף read-only מלא (‏/workspace/algotrade/telegram) + רענון t298b (‏468 הודעות) + רענון חדש היום (‏10 הודעות, 19.11 17:38–17:57 UTC, אין בהן שום דבר רלוונטי). סך הכול **13,463 הודעות, 27.10.2025–19.11.2026**. רק GetHistory: בלי שליחה, בלי תגובה, בלי join ובלי סימון "נקרא".
**שיטה:** ‏7 משפחות regex: ‏backtest/tester ‏(74 התאמות), ‏tick/modelling ‏(8), ‏slippage/latency/delay ‏(14), ‏VPS/server ‏(35), ‏"different/replicate/not the same" ‏(18), ‏spread ‏(30), ‏demo↔live ‏(25). אחר כך קראתי את ההקשר ביד (שרשורי תשובות) וסיווגתי. ‏**46 ציטוטים מתוארכים** ב-`t300_tester_gap_quotes.csv` (כינוי בלבד, קטגוריה, EA, מכני/שיקול דעת, מקור הפער).
**הסתייגות:** דיווחים עצמיים בצ'אט, בלי אימות. בחלק מהשרשורים חסרה ההודעה שעליה ענו (למשל לפני 12.2 ו-7.1). תגיות: ‏OBSERVED = ציטוט, ‏ASSUMED/השערה = שלי.

## 0. השורה התחתונה
1. **אף אחד בקבוצה לא תיאר השוואה שיטתית של אותו חשבון BD מול הטסטר, ברמת עסקה ושניות.** אין מספרים כמו "הטסטר נכנס X שניות אחרי" או "slippage ממוצע Y$". (OBSERVED, ‏0 מקרים)
2. **ההסבר הנפוץ לפער: סביבת הנתונים בטסטר** (ברוקר, סוג חשבון cent/std, ‏price feed, ‏multiplier). ‏4 חברים שונים, כולם על BD או Hamster. (OBSERVED)
3. **פער בין שני חשבונות חיים עם אותו סט:** ‏Jens_P_B, ‏10.6.2026, שני חשבונות ICTrading. ‏Golden_CasperIT הסביר את זה ב**הפרשי מילישניות וטיקים בתחילת מחזור**, וזה בדיוק המנגנון של Claude במאי. ‏Ramil הודה לו. (OBSERVED, הסבר תיאורטי ולא מדידה)
4. **Ramil עצמו:** "A backtest can only be auto". ‏backtest לבדיקת הסט ולהבנת המערכת, "what will work today will probably not work tomorrow". ‏price feed שונה בין ברוקרים, ‏trailing/TP חייבים להיות **virtual**, ‏Equity Stop EA על גרף נפרד. הוא **לא** מתייחס לנאמנות של הטסטר מול החשבון. (OBSERVED)
5. **ההגנה וההתערבות הידנית לא מסומלצות:** ‏Jens אומר במפורש שאי אפשר לסמלץ protector ומשיכות ב-backtest, ושסגירה ידנית או protector חיצוני **משבשים את חישוב ה-Daily Profit של BD**. זה רלוונטי ליוני ול-1.7 בחשבון. (OBSERVED)

## 1. ספירות (חברים שונים, כל התקופה)
| סוג פער | # חברים | מי (תאריך) | EA | מקור הפער לפי הדובר |
|---|---|---|---|---|
| ‏backtest משתנה לפי סביבת הטסטר (סוג חשבון/שרת) | 3 | Sergi M (29.4), ‏Jens_P_B (28.5), ‏VSLong (28.5) | BD | ‏cent מול std, ‏"chart kinda different", ‏"multiplier not the same" |
| ‏backtest משתנה לפי ברוקר | 2 (+1 מחבר סט) | KikiGarbi (28.5, BD), ‏IanJ81 (29.6, Hamster); ‏tradewithhappie: "broker differences will be there" | BD, Hamster | נתוני הברוקר בטסטר |
| שני חשבונות חיים, אותו סט, מסלול שונה | 2 | Jens_P_B (10.6, ICTrading ×2), ‏Deadaimx5 (4.5, אותו ברוקר ו-VPS שונה) | BD / לא צוין | ‏Jens: על אחד החשבונות רץ **EA נוסף** שפתח/סגר |
| הסבר מנגנון (מילישניות/טיקים/מחזור) | 1 | Golden_CasperIT (10.6) | BD | ‏tick-feed, ‏execution timing, ‏cycle start, ‏EA או ידני אחר |
| דמו מול אמיתי | 4 | Ricchiew (30.7, "real carries big DD"), ‏Mccrori ("demos are trash"), ‏wily345 ("Demo no slippers / No spreads"), ‏Jens_P_B (30.7); נגדי: ‏IanJ81 (19.7, Hamster "mostly similar") | לא צוין / Hamster | ‏slippage, ‏spread, ברוקר |
| ‏tick model | 2 | Jens_P_B (17.6: "Every tick based on real ticks"), ‏CharlesXAU (29.5: "real tick data") | BD/TC | – |
| הגנה/ידני לא מסומלץ | 1 | Jens_P_B (8.5, ‏13.6) | BD | ‏protector, משיכות, סגירה ידנית |
| ביצוע: latency/spread/slippage/VPS | 7 | piotrekdata (ping 60ms, ‏trail), ‏IanJ81 (~60ms ICM), ‏nandomartini (נפתח ונסגר תוך שנייה ב-ICTrading), ‏navneetahhi (spread/slippage בפתיחת שוק, ~30 דק'), ‏VSLong (spread ממוצע 20–25 נק', קפיצות ל-200+, פילטר 50), ‏blagoev88 (אחרי VPS "works perfect"), ‏Ramil (spread גדול = אין כניסה; חגים: slippage) | BD/TC/כללי | – |

**מכני מול שיקול דעת:** כל דיווחי הפער ב-backtest הם על ריצה **מכנית** (full auto). פערי חי↔חי ודמו↔אמיתי: ב-Jens יש מרכיב לא-מכני (EA נוסף בחשבון). ‏Ramil עצמו סוחר חצי-ידני ואומר שאת זה אי אפשר לבדוק בטסטר.

**איך מטפלים (מה שנאמר):** (1) מריצים backtest על **נתוני הברוקר ושרת החשבון** שבו סוחרים, למשל Jens: "VTMarkets Demo account backtesting seems to be comparable to ICTrading live account", ו-backtest על cent לא עובד. (2) ‏"Every tick based on real ticks". (3) דמו קודם על אותו ברוקר, סוג חשבון והון (‏happie, ‏Ramil). (4) ‏trailing/TP וירטואלי, ובברוקר בעייתי TP קבוע 100–200 נק' (‏Ramil). (5) ‏VPS קרוב לשרת. (6) ‏spread filter. **אף אחד לא מתאר Monte Carlo, עיכוב כניסה או כיול מול חשבון.**

## 2. מה Ramil (‏@ForexMechanicEA) אומר על backtest (‏17 ציטוטים ב-CSV)
- ‏20.1.2026: **"A backtest can only be auto"**. ‏26.5: "If you want to run on full auto then do some back tests, just like for Black Dragon. In current market conditions for gold trading I prefer semi manual."
- ‏11.1: "good to often run backtest and see if the set is still working in the new market conditions". ‏15.6: "what will work today will probably not work well tomorrow". ‏24.7: מטרת ה-backtest היא להבין את המערכת.
- ‏10.1: backtest של Trend Ai על **"2025 Dukascopy tick data"**. ‏23.12.2025: סט BD "with backtest included (2024 to now)". ‏28.5: ‏BD Casper set, ‏1.2025–5.2026 על M30.
- ברוקר: ‏12.2 "different price feed not all brokers the same use the broker that works best". ‏7.1 "maybe broker problem not all will show exactly the same".
- ‏trail: ‏11.5 "trailing needs to be virtual not real", ‏16.5 "always use virtual trail, TP", ‏3.6 trail אמיתי "can cause a lot of hyper activity on broker server".
- הגנה: ‏10.6 "run an Equity Stop EA on separate chart". חדשות: ‏12.2 "make News settings false it is not working" (ההקשר חלקי).
- **אין** אצלו התייחסות לנאמנות בין הטסטר לחשבון, לעיכוב או ל-slippage ב-BD. (OBSERVED: חיפשתי backtest/tester/demo/broker/visual/optimi, ‏51+ הודעות)

## 3. מה שימושי לפרוטוקול הנאמנות של GPT
1. **רגישות לשניות/טיקים = הסבר שקיים בקבוצה** (‏Casper, ‏10.6: "If one EA instance starts a cycle a few ticks earlier, its internal logic… diverges", ‏"Millisecond differences… divergent trade sequences, especially on… grid EAs", ‏"New Cycle triggers may occur at slightly different candles"). זה תומך בעיכוב כניסה ב-MC. **אין שם גודל עיכוב מדווח.**
2. **גדלים שדווחו:** ‏latency ~60ms (שניים, ICM/IC Trading). ‏spread ‏XAU ממוצע 20–25 נק' עם קפיצות ל-200+ בתנודתיות (‏VSLong). ‏spread ‏260 נק' ב-Exness 3 ספרות (‏dragonAngel, ‏4.9). ‏spread/slippage בפתיחת שוק מתנרמלים תוך ~30 דק' (‏navneetahhi). **השערה:** ‏latency של 60ms רחוק מאוד מ-8 שניות, אז עיכוב של 8 שניות במאי כנראה לא נובע מ-latency אלא מתזמון הטיק/הנר/תחילת המחזור (או משעון). כדאי ש-MC יכסה 0–15 שניות כפי שתוכנן, ושיהיה גם רכיב **±spread** (‏20–60 נק') על מחיר הכניסה. ההפרש של 1.9$ במאי הוא ~190 נק' בזהב בשתי ספרות, כלומר הרבה מעבר ל-spread רגיל. (השערה)
3. **ההגנה בטסטר:** לפי Jens, ‏protector חיצוני או סגירה ידנית משבשים את ה-Daily Profit הפנימי של BD. **השערה:** אם `chain.py` מסמלץ את ההגנה כקטיעה וריסטארט, צריך לבדוק שהמצב הפנימי של BD אחרי הסגירה (‏Daily Profit, ‏New Cycle) מתנהג כמו בחי, אחרת יהיה פיצול גם אחרי 1.7.
4. **התערבות ידנית:** ‏Ramil: "A backtest can only be auto". אין בקבוצה שיטה לסמלץ ידני. זה תומך בגישה של GPT: לא להמציא כללים אלא לקטוע את הסימולציה בנקודות ההתערבות הידניות (יוני) ולהשוות רק מקטעים מכניים. (השערה/המלצה)
5. **סביבת נתונים:** לפי Jens, טסטר על שרת cent נתן תוצאות שונות לגמרי. ‏**לבדוק** שהטסטר רץ על סימבול ושרת עם אותו contract/multiplier ואותן ספרות כמו החשבון החי. לפי Claude המחירים זהים, אז כנראה זה תקין, אבל כדאי לאמת את ה-multiplier. (ASSUMED)
6. **זהירות:** ב-10.6 ‏Jens ראה פער גדול בין שני חשבונות חיים, ולמחרת "not identified such big differences". כלומר פיצול מסלול הוא **אירועי** ולא קבוע, וזה תומך בגישת ההתפלגות של MC ולא בנקודה בודדת. (OBSERVED + השערה)

## 4. t299 (המשך)
שלב C ב-t299 (מאי–יולי) נמסר ב-19:36. ברענון היום (‏10 הודעות, 19.11) אין דיווחי פיצוץ, חיתוך או הגנה. אין שינוי בממצאי t299.

## קבצים
- `RESULTS_t300_tester_gap.md` (הקובץ הזה)
- `t300_tester_gap_quotes.csv`: ‏46 שורות
- `RESULTS_t300.sha256`
