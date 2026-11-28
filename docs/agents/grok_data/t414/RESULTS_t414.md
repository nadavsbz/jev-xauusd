# RESULTS t414 — זרימות ETF ספוט → לונג BTC 24h: **KILL ב-dev** (holdout לא נפתח)
**נכתב:** 26.11.2026 05:25 שעון ישראל (UTC+2). ריצה אחת לפי PREREG_t414.md המוקפא.

## הקפאה (לפני כל תשואה) [VERIFIED — SHA256SUMS_prereg.txt]
- PREREG_t414.md `011b6ae193d0ae8c2a0f9d30a081cc0667926ab66886e20e4529fd99f1b7e303`
- t414.py `1a3ccbe74c9e2c509275fc50deabe70d8759f3ca5b6edfded0a8a3b33421f18c`
- data/farside_btc_flows.csv `6c230fc4f4a9baaf7bb27a3261231c448d3c49ac78da829c94814307a399d7eb` (גלם webfetch `debfe6f6…`)
- data/pubtime.csv `3e8cf846ceb6c663297af6acebebd1536479e0d8866a568472a10a4c9b04f0d7` (נוצר בשלב pubtime בלי תשואות, נרשם לפני dev; הקוד בודק)
- BTCUSDT_1h.csv `90f638adf57cc0d019ad3558976c53c732ab73263d0dac5f77fdd2d75d8b11e8` (עד 09.11.2026 23:00 UTC)

## נתונים
- Farside all-data נקרא בקריאה רגילה (WebFetch), בלי הרשמה ובלי עקיפה. curl ישיר = 403 Cloudflare, לא נעקף [VERIFIED]. לא BLOCKED-DATA.

## זמני פרסום (Wayback, 710 ימי מסחר 11.01.2024–09.11.2026) [VERIFIED ספירה]
| סטטוס | dev | holdout |
|---|---:|---:|
| VERIFIED לפני 14:00 UTC של T+1 | 67 | 74 |
| שורה קיימת אבל ערך חלקי/שונה | 41 | 33 |
| שורה חסרה ב-snapshot האחרון לפני הדדליין | 22 | 27 |
| אין snapshot בחלון | 235 | 208 |
| כשל הורדה | 2 | 1 |
- [OBSERVED] בימים עם snapshot בחלון: כ-53% מאומתים לפני 14:00 UTC T+1; הרבה snapshots ערב T מראים שורה **חלקית** (למשל IBIT "-"), כלומר Farside ממלא את השורה בהדרגה עד בוקר T+1.
- [OBSERVED] snapshot מאומת: 26.6h–88.2h אחרי T 00:00 UTC, חציון 36.1h (≈12:07 UTC ב-T+1). זה חסם עליון בלבד.
- [VERIFIED] snapshot ראשון מאומת: 09.08.2024. לפני כן אין כיסוי ⇒ T+2 שמרני.

## dev (כניסות 11.01.2024–30.06.2025) [VERIFIED — RESULTS_t414.json]
- n=87 (16 ב-T+1, ‏71 ב-T+2; ‏7 דילוגי overlap).
- gross ‏**−10.35bp**/עסקה (t=−0.42). נטו **−15.00bp** (t=−0.61), ‏SD 230bp. עלות ממוצעת 4.65bp.
- bootstrap LB90 ‏**−46.2bp** (B=10000, seed 414). hit 43.7%. ‏DSR (N=4600) ≈1e-5.
- תיאורי בלבד: T+1 ‏+32.6bp (n=16, t=0.44); T+2 ‏−25.7bp (n=71, t=−1.02). 2024 ‏−14.9, ‏2025 ‏−15.1.
- **הכרעה: KILL** (gross ≤0). holdout נעול בקוד, לא נפתח. אין היפוך כיוון ואין "T+1 בלבד".
- [OBSERVED] תואם ל-Fabus et al.: אחרי יישור לזמן פרסום אין אות.
