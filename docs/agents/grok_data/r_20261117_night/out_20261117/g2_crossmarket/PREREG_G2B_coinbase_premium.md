# PREREG G2-B – Coinbase premium (ביקוש ספוט אמריקאי) כאות ל-BTCUSD | Grok | 17.11.2026 00:10 IL
סטטוס: נרשם לפני הרצה. נבדקה רק זמינות (Coinbase candles API מחזיר 200; קובץ Binance BTCUSDT H1 מקומי 2017-08-17 → 2026-11-09). לא חושבה פרמיה ולא תשואה.

## השערה ומקור
- Huang, Lin, Lu, Sun (2023), "The Financialization of Cryptocurrencies" (https://leihuang.xyz/publication/gbtc2023/): שינוי בפרמיית GBTC – ביקוש של משקיעים מסורתיים – הוא המנבא הבודד החזק ביותר לתשואה היומית של BTC; "Bitcoin prices react with a delay". [VERIFIED – תקציר]
- CryptoQuant quicktake (https://cryptoquant.com/insights/quicktake/66533f3321cb350988cdbe47): MA יומי של Coinbase Premium שחוצה מעל השבועי ← עלייה בהמשך. [HUNCH – פוסט פרקטיקנט, בלי סטטיסטיקה]
- CoinGlass docs: premium = Coinbase מול Binance, מדד לביקוש אמריקאי. [VERIFIED – הגדרה]
- מנגנון: זרימת ביקוש אמריקאית (מוסדות/ETF מאז 2024) מתבטאת קודם ב-Coinbase ומתפזרת עם פיגור לשאר השווקים. סיכון: הפרמיה כוללת בסיס USDT/USD (כי Binance ב-USDT); z מול 30 יום מנטרל drift איטי, לא קפיצות.
- לא כפילות: אינו BTC weekend→Monday (r89), אינו lead-lag כללי (r91 – שם מחיר מוביל מחיר; כאן הפרש בין בורסות), אינו C1 (Donchian/מומנטום).

## נתונים
- Coinbase BTC-USD H1: https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=3600 (300 נרות לבקשה).
- Binance BTCUSDT H1: data/binance/BTCUSDT_1h.csv (data.binance.vision).
- מחיר ביצוע: Binance BTCUSDT H1 (פרוקסי ל-RF BTCUSD; RF ECN עוקב אחרי ספוט).

## כלל (קבוע)
- p(h) = close_CB(h) / close_BN(h) − 1 לכל שעה h עם שני המחירים.
- s(d) = ממוצע p על 24 השעות של יום UTC d (נדרש ≥20 שעות).
- z(d) = (s(d) − mean(s, 30 ימים קודמים)) / std(s, 30 ימים קודמים), ללא d.
- כניסה: open של יום d+1 ב-00:00 UTC. z ≥ +1.0 → לונג; z ≤ −1.0 → שורט.
- יציאה: 00:00 UTC של d+2 (החזקה 24 שעות), או SL קשיח 2×ATR(14) יומי (ATR עד d), נבדק על high/low של H1. אין חפיפה (בהחזקה של יום אחד – כל יום בנפרד).
- גודל: סיכון 0.5% לעסקה לפי מרחק SL.

## עלויות RF (קבועות, מ-COST_PRESCREEN t199c / r2)
- ECN ‏2.84bp RT; swap 4.75%/שנה לשני הכיוונים = 1.30bp ללילה, ×3 בשישי. stress: עלות ×2.

## חלוקה
- dev: 2018-01-01 → 2021-12-31. ‏holdout: 2022-01-01 → 2026-10-31, נגיעה אחת, רק אם dev עובר.

## שער (כל התנאים)
dev: n ≥ 100; נטו ממוצע לעסקה ≥ 10bp ו-t ≥ 2.0; שני הצדדים (לונג/שורט) נטו > 0, או לונג > ממוצע כל ימי הלונג ב-dev; MDD ≤ 25% בסיכון 0.5%.
holdout: נטו לעסקה > 0 עם t ≥ 1.5; ≥ 60% שנים חיוביות; MDD ≤ 25%; stress > 0.
- מתאם יומי עם C1 ≤ 0.3 (Claude; C1 הוא BTC/ETH ולכן הבדיקה קריטית).
- KILL על כל כשל. אין שינוי סף/אופק/חלון אחרי צפייה.

## ציפייה כנה
סיכוי ~20%. האות ידוע ומצוטט רבות (CryptoQuant/CoinGlass) ולכן כנראה מתומחר בטווח של שעות; החזקה של 24 שעות עלולה להחמיץ אותו או לאכול רעש.
