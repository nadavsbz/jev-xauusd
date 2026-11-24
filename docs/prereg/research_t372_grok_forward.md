# PREREG t372 — forward-holdout watch על MQL5 Signals ציבוריים
**STATUS: FROZEN — 24.11.2026 (Asia/Jerusalem, IST)**
- מקור: `PREREG_t371_PROPOSED.md` (sha256 `1cf528a4e0ad0b09062cdf0285ebb2346bb53658872cf5691835b287e8d440f6`), עם כל התיקונים של Claude מה-outbox מ-24.11.2026 20:50 (commit a507f55): ‏P1-1, ‏P1-2, ‏P1-3, ‏P2-1, ‏P2-2 ו-ledger.
- מרגע ההקפאה: אין שינוי ב-universe, ב-gates, ב-splits או בספים. כל שינוי = PREREG חדש עם מספר חדש ו-+1 ל-N.
- תגיות: VERIFIED = נבדק על הקובץ/המקור. OBSERVED = חישוב שלי על נתונים מאומתים. ASSUMED = הנחה. UNKNOWN = לא ידוע.

## 0. למה ה-PREREG הזה
- ב-t371 אף מועמד לא עבר triage (ראו `candidates.md`, sha256 `a7072a91de41652dcf2c4c536d479da36a019d629e2c6621026145374cc609ea`), ולכן אין trade list לעשות לו reverse-engineering. [VERIFIED]
- לפי הכלל הקבוע (כל FAIL מגיע עם האיטרציה הבאה כבר רשומה מראש), ה-PREREG הזה תוקף את החולשה המרכזית של ציד track records ציבוריים: **selection on past performance**. הכלי: forward holdout שעוד לא נוצר.

## 1. השערה
- H1: בין ה-public MQL5 signals שעוברים את G0 ב-24.11.2026, לפחות אחד שאינו grid ואינו מרוכז ישמור על honest return של ‎≥3%‎ לחודש ועל equity DD של ‎≤15%‎ **על נתוני forward שעוד לא נוצרו** (VAL ואחר כך HOLDOUT).
- רק שורד forward מתקדם ל-trade-list rule extraction (‏PREREG נפרד בסגנון t373, עם DEV/VAL/HOLDOUT משלו על price data ועלויות RoboForex).
- **ההחלטה היחידה שמותרת בסוף VAL+HOLDOUT היא "worth t373-style deep test".** אסור לכתוב "works", "מוכח" או "edge מאומת" על סמך t372 (ראו §5, ‏P1-2).

## 2. Universe (קפוא)
- Snapshot: `list_parsed.csv` (3,769 public signals, crawl מ-24.11.2026), sha256 `ffa34faa16c65943797b28e8ee3b7d5fb2eba0f7e13a8950afa42f38b2d003cf`. [VERIFIED: sha חושב מחדש ב-24.11.2026 21:05]
- רשימת המשפחות הסגורות: `_prior_ids.txt`, sha256 `ec17e9685e5ba6254cd3da1d09e08c776791676da27986c0fcb7e784e27a263e`. [VERIFIED]
- Eligibility (‏G0, §4): ‏weeks ‏≥52 ב-24.11.2026, ‏real account, ‏list DD ‏≤25%, geometric monthly מה-growth ‏≥3%, לא ב-`_prior_ids.txt`, ואין במילות התיאור grid/martingale/averaging.
  - [OBSERVED] על העמודות המספריות בלבד, ‏58 signals עוברים (weeks‏≥52, ‏real, ‏DD‏≤25, ‏gm‏≥3%, ‏prior=False). סינון התיאור ותנאי P1-3 עוד לא הוחלו, ולכן הרשימה הסופית קטנה או שווה ל-58.
  - הרשימה הסופית (אחרי G0 המלא) תיכתב ל-`t372_watchlist_frozen.csv`, ה-sha שלה יחושב, והיא תיקבע **לפני** ה-re-crawl הראשון של VAL.
- Instruments: ‏all-in cost ‏≤2 bp/side ו-swap ‏≤~5% לשנה. מותר: FX majors ו-XAUUSD. מוחרג: BTC ו-CFDs אקזוטיים.

## 3. עלויות לכל rule test עתידי (RoboForex)
- XAUUSD: לפחות 10 bp ל-round trip לכל עסקה.
- FX: ‏4–5 pips לעסקה.
- Swap אמיתי מה-terminal spec (read-only). אף פעם לא 0.

## 4. Splits ו-Gates
**Splits:**
- DEV = כל מה שעד 24.11.2026. כבר נראה, ומשמש רק ל-eligibility. אף פעם לא כראיה.
- VAL = ‏25.11.2026–24.02.2027, forward, ‏re-crawl חודשי read-only (ראו §6).
- HOLDOUT = ‏25.02.2027–24.05.2027, forward, **untouched**: לא נקרא לשום החלטה עד ש-VAL נסגר ורשימת שורדי VAL נקבעה ונחתמה ב-hash.

**G0 (ב-freeze):**
- (a) eligibility כמו ב-§2.
- (b) בעמוד אין "80% of growth within N days" עם N ‏≤30, ו-top-10 weeks מתחת ל-50% מה-log growth.
- **(c) [P1-3, חדש]** ל-signal חייבים להיות **לפחות 8 שבועות של equity monitoring לפני 25.11.2026**, כלומר תאריך ה-"Started"/registration ב-MQL5 הוא לכל המאוחר 30.09.2026.
  - הסיבה: MQL5 עוקב אחרי equity רק מרגע הרישום. ההיסטוריה שלפני כן מיובאת, ואין בה equity/floating DD (בדיוק המקרה של ICM30 ‏2400112: ‏208 שבועות של history, אבל monitoring של 6 ימים בלבד). [VERIFIED ב-`candidates.md` C1]
  - signal שתאריך הרישום שלו לא מוצג או לא ניתן לקריאה מסומן **[UNKNOWN] ומוחרג**. אין הנחה לטובתו.

**G1 (על VAL):**
- forward geometric monthly ‏≥3% (‏honest TWR מטבלת ה-growth של MQL5).
- **forward equity DD ‏≤15%.**
- forward top-10 days או weeks מתחת ל-50% מה-forward growth.
- אין ראיה חדשה ל-grid/martingale: deposit-load spikes מעל פי 3 מהחציון, או equity DD מעל פי 2 מה-balance DD בחלון.

**[P1-1] למה 15% ב-G1 ו-25% ב-eligibility:**
- תקרת ה-15% equity DD ב-G1 חלה **רק על חלון ה-forward** (VAL, ובהתאמה HOLDOUT ב-G2).
- רשימת ה-eligibility ב-G0 מאפשרת עד 25% list DD היסטורי, כדי לא לחתוך מראש מועמדים שה-DD ההיסטורי שלהם כולל תקופה ישנה או balance DD.
- הסיבה ל-15% ב-forward: ה-15% equity protection stop של נדב הוא **תנאי הישרדות**, לא פרמטר אופציונלי. אם בחלון ה-forward ה-equity DD עבר 15%, אז בחשבון של נדב ההגנה הייתה עוצרת את החשבון. האסטרטגיה בפועל לא הייתה שורדת אצלנו, גם אם ה-signal עצמו התאושש אחר כך.

**G2 (על HOLDOUT):**
- אותם תנאים כמו G1, על חלון ה-HOLDOUT.
- בנוסף, honest מצטבר (VAL+HOLDOUT) ‏≥3.5% לחודש (הרף הרחב של נדב).

**Pass** = G0 ‏& G1 ‏& G2. גם Pass מוביל רק ל-PREREG חדש של trade-list rule extraction (entries/exits מול features), עם DEV/VAL/HOLDOUT משלו על price data ועם עלויות RoboForex.

## 5. [P1-2] מגבלת power: ‏G1/G2 הם screen זול, לא ראיה
- 3 חודשי VAL, עם ממוצע 3% לחודש ו-vol של כ-5% לחודש: ‏t ≈ 3 / (5/√3) ≈ **1.04**. [OBSERVED: חישוב]
- t של כ-1 לא מבדיל בין edge לבין מזל. גם VAL+HOLDOUT יחד (6 חודשים) נותנים t ≈ 1.47 בלבד. [OBSERVED]
- לכן G1 ו-G2 הם **cheap screen** שמטרתו להוריד מהרשימה את מה שקורס forward (DD מעל 15%, ריכוז, grid). הם לא ראיה לכך שהאסטרטגיה עובדת.
- **ההחלטה היחידה המותרת אחרי VAL+HOLDOUT: "worth t373-style deep test".** אסור "works". ההכרעה האמיתית נעשית רק ב-deep test עם trade list, עלויות אמיתיות, holdout נפרד ו-DSR.

## 6. [P2-1] כללי ה-re-crawl החודשי
- read-only בלבד: GET ציבורי של עמודי signal, בלי log-in, sign-up, subscribe, copy או follow.
- low-rate: ריצה אחת בחודש (בסביבות 25 לכל חודש), עם השהיה של כמה שניות בין בקשות ו-User-Agent רגיל.
- **אין anti-bot circumvention:** אין עקיפת CAPTCHA/Cloudflare, אין proxies או rotation, אין headless stealth ואין cookies מחשבון.
- אם הגישה נחסמת: מתעדים (תאריך, signal, קוד תגובה) ב-`t372_crawl_log.md`, **לא עוקפים**, והחודש הזה מסומן UNKNOWN לאותו signal. signal שחסר לו חודש VAL אחד או יותר לא יכול לעבור את G1 (ייחשב FAIL-by-missing-data, לא PASS).

## 7. Early kill
- K1: signal שה-forward equity DD שלו עובר 10% ב-6 השבועות הראשונים של VAL, או שהתיאור/האזהרות שלו משתנים ל-grid, ‏martingale או "no SL", יורד מיד. נרשם ב-log ולא חוזר לעולם.
- K-program: אם ב-24.02.2027 אף signal לא שרד את G1, נסגר תחום MQL5-public, ועוברים ל-fallback (§8).

## 8. [P2-2] Fallback: ‏DARWINs (משפחה נפרדת)
- Public Darwinex DARWINs שה-"Trade distribution" שלהם לא מוסתר (עסקאות הבסיס גלויות בלי log-in), עם ‏≥18 חודשים. מחלצים entries/exits מול features ישירות מה-trade distribution הציבורי. אותן עלויות, gates ו-splits (עם תאריכים חדשים שייקבעו בהפעלה).
- **זו משפחת ניסויים נפרדת.** היא מוסיפה **+1 ל-N רק כשהיא מופעלת בפועל** (כלומר אחרי K-program, או בהחלטה מפורשת), ולא ב-freeze של t372.
- הפעלה = PREREG קצר משלה עם תאריכי splits, ‏hash של ה-universe ומספר trial.

## 9. Trial ledger ו-DSR
- t371: ‏K_alpha = 0 (לא הורץ backtest או rule test). universe שנסרק: 3,769 signals (הערת selection-bias ל-DSR). [VERIFIED מ-STATUS.md/candidates.md]
- **N מצטבר: ‏N ≥ 2,549 + 30 = 2,579** לפני t372.
  - 2,549 = ה-snapshot האחרון שיש על ה-box (render מ-03.11.2026). [OBSERVED]
  - ‏+30 = לפי ה-outbox של Claude (a507f55). [ASSUMED: נמסר לי, ולא אימתתי מול ledger]
  - Claude יבנה `LEDGER.md` עם הערך המדויק.
- t372 מוסיף K = 1 (משפחת watch אחת), ולכן **N ≥ 2,580** אחרי ה-freeze. אם ה-fallback של DARWIN יופעל: ‏N ≥ 2,581. כל rule test מאוחר יותר מוסיף K משלו.
- **ההשלכה ל-DSR:** עם N ≈ 2,580, ה-expected max Sharpe תחת H0 הוא בערך 3.52 סטיות תקן של ה-Sharpe estimator (נוסחת Bailey–López de Prado עם γ של Euler). [OBSERVED: חישוב]
  - עם 3 חודשי VAL, ה-SE של Sharpe חודשי הוא בערך 0.58. לכן הסף ל-DSR מובהק הוא בערך Sharpe חודשי של 2 (כ-7 שנתי). זה בלתי סביר. [OBSERVED]
  - כלומר: **אין דרך ש-t372 לבדו יעבור DSR.** זו סיבה נוספת לכך ש-G1/G2 הם screen בלבד (§5).
  - בנוסף, בתוך המשפחה יש selection: הבחירה מתוך עד 58 eligible signals (מתוך 3,769). ב-deep test, ה-DSR יחושב עם N המצטבר מה-LEDGER, ובנוסף עם מספר ה-signals שנצפו ב-t372.

## 10. Artefacts שיופקו
- `t372_watchlist_frozen.csv` + sha (לפני ה-crawl הראשון של VAL)
- `t372_crawl_log.md` (כל ריצה, כל חסימה)
- `t372_VAL_survivors.csv` + sha (נקבע ב-24.02.2027, לפני שנוגעים ב-HOLDOUT)
- `RESULTS_t372.md` בסוף HOLDOUT, עם ההחלטה המותרת היחידה (§5).

STATUS: FROZEN — 24.11.2026
