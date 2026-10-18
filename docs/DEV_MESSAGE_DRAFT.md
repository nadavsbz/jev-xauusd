# טיוטת הודעה למפתח של Black Dragon (לשיקול המשתמש, לא נשלחה)

**נכתב ב-19.10.2026.** ההחלטה אם לשלוח שמורה למשתמש. בהודעה אין מספר חשבון, סיסמה או פרט מזהה.

## מה שואלים, ולמה

מה למדנו מהבדיקות:
- **הנפילות נגרמות על ידי שרשרת אחת שממשיכה להוסיף רמות במגמה חד-כיוונית.** ב-7.6.2024 היו 31 כניסות בירידה של 3.6%. (`BD1_CRASH_CAUSE.md`)
- **שום הגנה מבחוץ לא פותרת את זה:** רצפה, שומר, חסימת כיוון, תקרת לוט, גידור ומסנן סטוכסטי. (`OPEN_QUESTIONS.md`, `BD_ANTICRASH_PLAN.md`, `DEPTH_HEDGE_PLAN.md`)
- **המסנן הסטוכסטי המובנה עוזר רק בחלק מהתקופות, ומוריד את הרווח בכ-90%.**

**לכן הבקשה היא לשנות את הלוגיקה בתוך הרובוט.**

## הנוסח (באנגלית)

> Hi, I've been running Black Dragon on XAUUSD for a while and I'm very happy with it. I've done extensive backtesting (real ticks, 2022–2026) and I'd like to ask about one specific risk.
>
> On strong one-way days (e.g. 7 June 2024, gold −3.6% in one direction), one chain keeps adding levels until it reaches MaxLot, and the drawdown becomes very deep. With my settings (Martin 1.5, MaxLot 5, Fix_Distance 300, Distance_multiplier 1.2) the 2024 period wipes the account at my lot/deposit ratio.
>
> Questions:
> 1. How does `Use_Stoh` work exactly? Does it block only new chains, or also adding levels? In my tests it removes ~90% of entries, so profit drops a lot.
> 2. Is there (or could you add) an option to **pause adding levels** when a chain is deep (N levels) and price keeps moving the same way beyond X — resuming only after a pullback of Y?
> 3. Alternatively: a **maximum total open lots per side** (wait, do not close), or a **maximum number of new levels per day**?
> 4. What does the lot of a new level depend on after an Overlap close? (It is not always last lot × Martin.)
>
> I'm happy to share my backtest results if useful. Thank you!

## מה נעשה עם התשובה

- **אם המפתח יוסיף אפשרות:** בדיקה רשומה מראש בטסטר, אותה שיטה שבה השתמשנו עד עכשיו. בחירה על 2024–2025, ובדיקה פעם אחת על התקופה של חשבון 1.
- **אם המפתח יסביר את הלוגיקה:** השחזור בסימולטור יהיה נאמן, ונוכל לבדוק מנגנונים בעצמנו. (`GRID_REPLICA_PLAN.md`)
