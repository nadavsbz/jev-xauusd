# RESULTS t373 — פענוח ה-magic numbers בחשבונות BD
נכתב 24.11.2026 בסביבות 21:07 IST (Asia/Jerusalem). Grok, על ה-box בלבד (Benzaquen offline, לא נגעתי בו).
**read-only:** לא נשלח שום דבר ל-Telegram, לא בוצע log-in ולא נפתח accounts.json. לא מופיעים כאן מספרי חשבון, logins או IPs. חשבונות מסומנים רק בכינוי (BD1..BD8, BTC_Bot_4, BTC_bot_account).
תגיות: VERIFIED = נקרא ישירות במקור. OBSERVED = ספירה/חישוב שלי על נתונים מקומיים. ASSUMED = הסקה. UNKNOWN = לא נמצא.

## מקורות וכיסוי
| מקור | תוכן | טווח תאריכים (UTC) |
|---|---|---|
| `/workspace/algotrade/telegram/messages.jsonl` | הקבוצה של Ramil ("Top Target", @ForexMechanicEA), ‏12,985 הודעות | 27.10.2025 – 26.10.2026 |
| `/workspace/t298b/tg/refresh_messages.jsonl` + `refresh2_messages.jsonl` | רענון read-only של אותה קבוצה, ‏468+10 הודעות | 27.10.2026 – 19.11.2026 |
| `/workspace/algotrade/telegram/files/` + `files_manifest.json` | 216 קבצים, מתוכם 117 ‏set files שהועלו לקבוצה | 31.10.2025 – ספטמבר 2026 |
| `/workspace/algotrade/telegram/lars/messages.jsonl` | ‏Lars (@The_B33keeper), ‏417 הודעות | 12.07.2025 – 15.10.2026 |
| `research_intel/telegram_digest`, ‏`claude_bridge/out_20261117/g1_rf_telegram`, ‏`results_t251/telegram`, ‏`results_t227`, ‏`t311b/raw` | ערוצים ציבוריים אחרים ותקצירים | — |

- [VERIFIED] **הכיסוי המאוחד של הקבוצה של Ramil הוא 27.10.2025–19.11.2026.** כל מה שקרה לפני 27.10.2025 לא נמצא בנתוני הקבוצה. זה רלוונטי ל-magic 5000, ראו בהמשך.
- [OBSERVED] חיפוש ב-grep על כל המקורות: חמשת המספרים, וגם magic/hedge/recovery/protect/"magic number". במקורות שאינם הקבוצה של Ramil או של Lars אין שום אזכור רלוונטי.
- לצורך הצלבה, קראתי read-only גם את ה-deals המקומיים: `/workspace/algotrade/history/*_deals.csv` (ה-refresh השבועי שאושר). ההצלבה מוצגת בספירות מצרפיות בלבד.

## ממצאים לפי magic
### magic 0: ידני, או סגירה מבחוץ (הגנה)
- **[VERIFIED, מקור ציבורי]** עסקאות ידניות ב-MT5 נושאות magic 0 (מקורות: drawguard.io ‏"A magic of 0 means the trade was placed by hand", ‏fxdreema, ‏MQL5 forum 468985).
- **[VERIFIED, Telegram] ‏Ramil, 25.06.2026 ‏#104196:** "Yes in your settings allow manual orders to be managed by EA then you can place trades on your phone".
  - ל-BD יש פרמטר `flag_Hand_Ord`, שמאפשר ל-BD לנהל עסקאות ידניות.
  - בכל ה-sets של CasperIT ‏(123654/223344) הוא `true`. ב-sets הרשמיים של Ramil ‏(1111) וב-JPB ‏(1878943) הוא `false`. [VERIFIED מה-set files]
- **[VERIFIED, Telegram] ‏Ramil ממליץ על protection EA חיצוני "on separate chart":**
  - 10.06.2026 ‏#102547: "The best is to run an Equity Stop EA on separate chart..."
  - 11.05.2026 ‏#99479: "We don't use SL you can use an Equity Protector"
  - הפוסט "ACCOUNT PROTECTORS FOR FREE" (EarnForex Account Protector, ‏meetalgo Equity Guard) פורסם 4 פעמים: ‏23.02, ‏13.03, ‏06.05 ו-04.08.2026.
- **[OBSERVED, deals מקומיים]** ב-magic 0 יש 5,278 deals ב-9 חשבונות, בין 19.09.2025 ל-20.10.2026:
  - **480 יציאות עם reason=3 ‏(EXPERT) ועם comment בתבנית `n_<מחיר>_v`.** זו סגירה של ההגנה שנדב הגדיר. כך מתועד כבר ב-`docs/BD1_CRASH_CAUSE.md` (נדב אישר ב-17.10.2026). הסגירות האלה מופיעות בכל 8 החשבונות, והימים העמוסים ביותר הם 30.07, ‏30.04, ‏04.05, ‏10.08 ו-29.05.2026.
  - 231 כניסות ידניות: 198 מהנייד (reason=1) ו-33 משולחן העבודה (reason=0). הרוב ב-BD2 ‏(142) וב-BD1 ‏(48), בין 14.05 ל-21.08.2026.
  - כ-4,234 יציאות עם comment "BTC Bot[tp]" עם magic 0 ב-BD1. [ASSUMED] יציאת TP בצד השרת של BTC Bot, שנרשמת בלי magic.
  - 30 ‏[sl], ‏15 ‏stop-out.
  - ב-BTC_bot_account יש 62 deals עם comment בסגנון copy-trade (‏`C …E@…#…`, הושמט כאן כי יש בו מזהה). [ASSUMED] copier.
- **פירוש:** magic 0 בחשבונות BD הוא תערובת של שלושה דברים:
  - (a) סגירות של ההגנה החיצונית (`n_*_v`, ‏reason=3)
  - (b) מסחר ידני/semi-manual מהנייד
  - (c) יציאות TP של BTC Bot
  - **הוא אינו bot נפרד שפותח עסקאות.** [OBSERVED + VERIFIED]

### magic 1111: ‏BD, ה-default של Ramil
- **[VERIFIED, Telegram] ‏Ramil, 14.01.2026 ‏#83621–83624:** פרסם את `ea_black_dragon_mt5_xauusd_m5_2digit.set` ‏(+mt4/3digit), עם `Magic=1111`, ‏`Flag_Use_hedge=true` ו-`flag_Hand_Ord=false`. ב-#83625 כתב: "Above are sets for Black Dragon Stochastic = True and trailing on 50k cents (Buy only)".
- [OBSERVED] ‏1111 מופיע ב-24 ‏set files (כולל 4 של Ramil), החל מ-31.10.2025 ‏(#74628, CasperIT). רוב החברים פשוט משאירים את ה-default.
- [OBSERVED, מקור ציבורי, תקציר חיפוש בלבד] גם עותקי BD ברשת (eafxstore, ‏scribd "Beginners Guide... Ramil") מציגים Magic=1111. לא פתחתי את העמודים במלואם.
- [OBSERVED, deals] 6,312 deals ב-7 חשבונות, בין 30.10.2025 ל-06.08.2026. ה-comments: ‏"EA Black Dragon (casper)" ‏1,676, ‏"EA Black Dragon" ‏1,107, ‏"1H_Ramil_EA Black Dragon" ‏289, ‏"ea_black_dragon_mt5_stochastic" ‏113. כל הכניסות הן reason=3.
- **פירוש:** ‏1111 = BD עצמו, עם כמה sets שונים (casper, ‏1H_Ramil, ‏stochastic) שכולם שומרים את ה-default. **אין שום אזכור של protection, hedge נפרד או recovery EA על magic 1111.**
  - הערה: ה-hedge (`Flag_Use_hedge`) הוא פיצ'ר פנימי של BD. ב-set files לא מופיע magic נפרד ל-hedge. [ASSUMED] ‏ה-hedge נפתח באותו magic. [UNKNOWN] אין לנו את קוד המקור.
- הערה צדדית: ‏@ThorVig, ‏31.03.2026 ‏#95292 (BD M5_Thor_0.01.set, ‏Magic=1111): "i use in combination with my own riskmanager". ה-riskmanager לא מזוהה ואין לו magic. [VERIFIED quote]

### magic 123654: ‏set של CasperIT ל-BD (Aggressive/Safe M1)
- **[VERIFIED, Telegram]** הופעה ראשונה: ‏@Golden_CasperIT, ‏15.01.2026 ‏#83699, ‏`CasperIT black dragon m1 6am to 6pm gmt+2.set`:
  - `Magic=123654`, ‏`sOrdComm=EA Black Dragon`
  - `Flag_Use_hedge=true`, ‏`flag_Hand_Ord=true`, שעות 6–18
  - פורסם שוב ב-31.01.2026 ‏#86746: "Attached is the set file i'm using as @Now... time zone GMT+2"
- **[VERIFIED] ‏Ramil עצמו העלה מחדש** את `CasperIT_BlackDragon_Safe_50k_3digits/2digit.set` עם Magic=123654 ב-13.02.2026 ‏#89067–89068. באותו batch: ‏Hybrid=334455 ו-Aggressive=556677.
- **[VERIFIED]** ‏`CasperIT_BlackDragon_Aggressive_M1_50k_2digits/3digits.set`, עם Magic=123654 ו-sOrdComm=`EABlackDragon_CasperIT_Aggressive_M1_50k`:
  - ‏Martin 1.5, ‏MaxOrders 12, ‏SL_=0, ‏hedge=true, ‏Hand_Ord=true
  - פורסם ב-03.03.2026 ‏#91320 וב-09.03.2026 ‏#92229
  - BembesX פרסם עותק ב-17.02.2026 ‏(#89492/89508)
- [OBSERVED, deals] 56,468 deals ב-BD2, ‏BD6 ו-BD7, בין 15.04 ל-29.05.2026. כל ה-comments הם "EABlackDragon_CasperIT_Aggress…", כלומר ה-set האגרסיבי של M1. היה SL אחד בלבד.
- **פירוש:** BD עם ה-set של CasperIT Aggressive M1. **זה לא protection, ‏hedge נפרד או recovery EA.** [VERIFIED מה-set וה-comments]

### magic 223344: ‏set של CasperIT ל-BD (Hybrid/Safe M1, 2-digit)
- **[VERIFIED, Telegram] ‏@Golden_CasperIT, ‏03.03.2026 ‏#91322 ו-#91324,** בתגובה לשאלה של Ramil ב-#91318: "What time frames are these sets?":
  - `CasperIT_BlackDragon_Hybrid_M1_50k_2digits.set`: ‏Magic=223344, ‏Martin 1.2, ‏MaxOrders 8
  - `..._Safe_M1_50k_2digits.set`: ‏Magic=223344, ‏Martin 1.1, ‏MaxOrders 6
  - בשניהם hedge=true, ‏Hand_Ord=true, ‏SL_=0
- [OBSERVED, deals] 4,172 deals, רק ב-BD2, בין 07.04 ל-15.04.2026. ה-comment הוא "EABlackDragon_CasperIT_Hybrid_…", כלומר Hybrid M1. אחרי 15.04 החשבון עבר ל-123654.
- **פירוש:** BD עם ה-set של CasperIT Hybrid M1. **לא protection, ‏hedge נפרד או recovery.** [VERIFIED]

### magic 1878943: ‏set של JPB (Jens) ל-BD, עם SL
- **[VERIFIED, Telegram] ‏@Jens_P_B, ‏05.06.2026 ‏#102037–102039:** "...I have attached the mt4 and mt5 versions... times are for gmt+3 broker. Please do not adjust any setting beside of the trading time frame..."
  - הקבצים: `1878943_eabd_jpb_xauusd_2d_mt5_v1.00.set` / `_mt4_`
  - `Magic=1878943`, ‏sOrdComm=`9-13 EABD JPB XAUUSD SL 2D V1.00`
  - שעות 9–13, ‏**SL_=8000** (‏SL קשיח), ‏Martin 1.3, ‏MaxOrders 14, ‏MaxLot 0.04
  - hedge=true, ‏Hand_Ord=false
- [VERIFIED, web] חיפוש ציבורי של "1878943" לא העלה שום EA (רק מק"טים לא קשורים). המספר הוא של Jens, לא default של מוצר.
- [OBSERVED, deals] 2,500 deals, רק ב-BD6, בין 09.06 ל-24.06.2026. ה-comment הוא "9-13 EABD JPB XAUUSD SL 2D V1.00".
- **פירוש:** BD עם ה-set של JPB (session 9–13 עם SL). **לא protection נפרד**, אבל ה-set עצמו כולל SL פנימי.

### magic 5000: ‏UNKNOWN מבחינת Telegram
- **[UNKNOWN]** אין אף set file עם Magic=5000 בכל 117 ה-sets של הקבוצה, ואין אזכור של "magic 5000" בהודעות של Ramil, של Lars או בשאר המקורות.
  - האזכורים של "5000" בקבוצה הם גדלי חשבון ("5000USc"), ‏Autolotsize או Order Distance. אף אחד מהם לא magic.
- [VERIFIED, web] בחיפוש ציבורי לא נמצא EA מוכר עם default magic 5000. נמצאו defaults אחרים (144401, ‏345678, ‏55555, ‏22203011), אף אחד מהם לא 5000.
- [OBSERVED, deals] 4,466 deals, רק ב-BD8, בין **29.09 ל-09.10.2025**. ה-comment הוא "EA Black Dragon", ב-XAUUSDc (ו-3 ב-XAGUSDc), כל הכניסות reason=3. `scripts/strategy_baskets.py` מתייג את זה "BD 5000 (2025)".
- **פירוש:** BD עם magic שהוגדר ידנית (ה-comment הוא ה-default של BD), בתקופה **שקודמת לכיסוי של נתוני הקבוצה (27.10.2025)**. [ASSUMED] נדב או מי שהתקין בחר 5000 בעצמו. מקור ה-set ‏[UNKNOWN]. אין ראיה ל-protection, ‏hedge או recovery.

## protection / hedge / recovery: ממצאים כלליים (לא קשורים ל-magic)
- [VERIFIED] אין בקבוצה **אף** אזכור של recovery EA או protection bot עם magic מסוים.
- [VERIFIED] יש אזכור אחד של recovery EA: חבר, 11.04.2026 ‏#96693: "use caspar 1M 5k set and use AW Recovery pro (buy it...) when drawdown reaches 20%". בלי magic, ו-[UNKNOWN] אם מישהו מהחשבונות שלנו השתמש בו.
- [VERIFIED] חשד ל-"Recovery EA?" ב-28.08.2026 ‏(#111136) התברר כ-news filter ‏(#111140).
- [VERIFIED] על hedge: אין ל-Ramil הודעה שמתארת hedge EA נפרד. השאלה ב-31.08.2026 ‏(#111258) על הגדרת hedge נוגעת לפרמטר הפנימי.
- **מסקנה:** כל ה-magics שאינם 0 הם **Black Dragon** עם sets שונים. ה-sets הם של Ramil (1111), ‏CasperIT ‏(123654, ‏223344), ‏JPB ‏(1878943) ומקור לא ידוע (5000). רק magic 0 מכיל פעולות של protection (‏`n_*_v`) ופעולות ידניות.

## השלכה ל-BD live-vs-tester
- [ASSUMED] כל השוואה בין live ל-tester צריכה להפריד לפי magic ולהריץ בטסטר את ה-set המתאים (1111-stoch/casper/1H_Ramil, ‏123654 Aggressive M1, ‏223344 Hybrid M1, ‏1878943 JPB SL, ‏5000 unknown set).
- יציאות `n_*_v` עם magic 0 צריכות להיות מטופלות כ-overlay של ההגנה, ולא כהתנהגות של BD.

## קבצים
- `RESULTS_t373_magics.md` (הקובץ הזה)
- `t373_magic_quotes.csv`: ‏18 ציטוטים מתוארכים, עם msg_id ומקור.
