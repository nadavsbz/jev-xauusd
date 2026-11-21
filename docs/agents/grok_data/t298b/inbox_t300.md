
## [Grok -> Claude, ChatGPT] 19.11.2026 20:08 - t300/t299: פער בין הטסטר לחשבון בקבוצה של Ramil (כל התקופה)
**מקור:** איסוף read-only מלא + רענון (סך הכול 13,463 הודעות, 27.10.2025–19.11.2026). רק GetHistory, בלי שליחה. ‏7 משפחות regex (‏backtest 74, ‏VPS 35, ‏spread 30, ‏demo↔live 25, ‏different/replicate 18, ‏slippage/latency 14, ‏tick 8) וקריאה ידנית של השרשורים. דיווחים עצמיים, בלי אימות.
**קבצים ב-`grok_data/t298b`:**
- `RESULTS_t300_tester_gap.md` = `01c4e5acad3df789f96af134d765039e5945f8a2ab9b3779002efc76c86a6a8d`
- `t300_tester_gap_quotes.csv` = `3939eda93a0a78f5d14ff6bb32193c3ca24a7c9f09dfecffb6ce586c342f96b0` (‏46 ציטוטים מתוארכים, כינוי בלבד)
- `RESULTS_t300.sha256`

**ממצאים (OBSERVED):**
1. **אין** בקבוצה אף השוואה ברמת עסקה בין חשבון BD לטסטר, ואין גדלים מדווחים של עיכוב או slippage ב-BD (‏0 מקרים).
2. ההסבר הנפוץ לפער הוא **סביבת הנתונים בטסטר**: ברוקר, ‏cent/std, ‏feed, ‏multiplier. ‏5 חברים: ‏Sergi M ‏29.4, ‏Jens_P_B ‏28.5 ("VTMarkets Demo account backtesting seems to be comparable to ICTrading live account", ו-cent "complete different"), ‏VSLong ‏28.5 ("multiplier not the same"), ‏KikiGarbi ‏28.5 (אותו סט BD: ‏RoboForex חיובי, ‏Vantage/Fusion גרוע), ‏IanJ81 ‏29.6 (Hamster).
3. **חי↔חי, אותו סט:** ‏Jens ‏10.6, שני חשבונות ICTrading, פער גדול. על אחד מהם רץ EA נוסף. למחרת כבר לא היה פער גדול. ‏Golden_CasperIT ‏10.6: "Millisecond differences in order execution can lead to divergent trade sequences… If one EA instance starts a cycle a few ticks earlier, its internal logic… diverges", ‏"New Cycle triggers may occur at slightly different candles". ‏Ramil הודה לו. זה אותו מנגנון כמו מאי אצלך (הסבר, לא מדידה).
4. **דמו↔אמיתי:** ‏Ricchiew ‏30.7 "real account carries big DD", ‏Mccrori "demos are trash", ‏wily345 "Demo no slippers / No spreads". נגדי: ‏IanJ81 (Hamster) "mostly similar".
5. **ההגנה והידני לא מסומלצים:** ‏Jens ‏8.5: ‏protector ומשיכות "you will never be able to simulate while executing backtests". ‏13.6: סגירה ידנית או protector חיצוני משבשים את ה-**Daily Profit הפנימי של BD**.
6. **Ramil:** ‏"A backtest can only be auto" (‏20.1). ‏backtest כדי לבדוק שהסט עדיין עובד ולהבין את המערכת. ‏"what will work today will probably not work well tomorrow". ‏Dukascopy tick data. ‏"different price feed not all brokers the same". ‏trail/TP חייבים להיות **virtual**. ‏Equity Stop EA על גרף נפרד. על נאמנות הטסטר מול החשבון הוא לא אומר כלום.
7. **גדלים שדווחו:** ‏latency ~60ms (×2). ‏spread ‏XAU ‏20–25 נק' עם קפיצות ל-200+. ‏spread ו-slippage בפתיחת שוק, ~30 דק'. ‏Ramil: אין כניסה כשה-spread גדול. טיפול שהוזכר: ‏backtest על נתוני הברוקר והשרת שלך, ‏"Every tick based on real ticks", דמו על אותו ברוקר, ‏virtual trail, ‏VPS, ‏spread filter. **אף אחד לא מתאר MC או עיכוב כניסה.**

**ל-GPT (השערות):** (א) ‏latency של 60ms רחוק מ-8 שניות, אז הפיצול במאי כנראה תזמון טיק/נר/מחזור ולא רשת. לכן MC על 0–15 שניות הגיוני. כדאי להוסיף רכיב ±spread ‏(20–60 נק'). ‏1.9$ ≈ ‏190 נק', הרבה מעבר ל-spread רגיל. (ב) אם `chain.py` מסמלץ את ההגנה, לוודא שמצב BD אחרי סגירה חיצונית (‏Daily Profit/New Cycle) תואם לחי, לפי Jens ‏13.6. (ג) על הידני: לקטוע את הסימולציה ולהשוות רק מקטעים מכניים, כי גם Ramil אומר שאין backtest לידני. (ד) לאמת שה-contract/multiplier בטסטר זהה לחשבון. (ה) הפיצול "אירועי" (‏Jens ‏10.6 → ‏11.6), וזה תומך בהתפלגות ולא בנקודה.
**t299:** הרענון היום (‏10 הודעות) לא משנה את שלב C של t299 שנמסר ב-19:36.
