# t311: SARUJA "10K To 1M JOURNEY" (RoboForex Copy Trading): ניתוח שיטה
**מאת:** Grok (המאסטרו) -> Claude | **תאריך:** 20.11.2026 (שעון ישראל) | **סטטוס:** מחקר מקורות פומביים בלבד, בלי כניסה לשום חשבון ובלי API פנימי
**תגיות:** VERIFIED = נקרא במקור · OBSERVED = נצפה בנתון פומבי או חושב ממנו · ASSUMED = הסקה · UNKNOWN = לא ידוע
**פרטיות:** הדוח לא כולל מספרי חשבון של נדב. מספרי החשבון שמופיעים כאן הם של דפי אסטרטגיה פומביים בלבד.

---

## 0. תקציר מנהלים
1. **אסטרטגיית short בלבד על זהב, עם averaging ובלי SL קשיח. זה לא grid "קלאסי" מרובה רמות.** שני חשבונות copy פומביים של עוקבים ב־Myfxbook שמעתיקים את ה־JOURNEY מראים **Shorts 56/62 ו־59/65, Longs 0/0**, win rate של כ־90%, אורך עסקה ממוצע של יום אחד, ומספר פוזיציות פתוחות קטן (1–3) (OBSERVED). המפעיל עצמו מתאר החזקה של פוזיציות מפסידות "עד ה־target", ולא פעם ויתר על סגירה ב־breakeven (VERIFIED, Telegram).
2. **אותו מפעיל קרס לפחות 5 פעמים בתוך 3.5 שנים**, לפי הודעות ה־Telegram שלו עצמו: 04.2023, 10.2023, 03.2024, 04.2024 ו־08.2026. כל מחזור נמשך בין חודש ל־5.5 חודשים: קודם עלייה של מאות עד עשרות אלפי אחוזים, ואחר כך הפסד כבד או מחיקה (VERIFIED). שני חשבונות עוקבים מ־2023/2024 ב־Myfxbook הסתיימו ב־−88.07% וב־−95.27% (VERIFIED).
3. **הרובוט לא נמכר.** אין לו מוצר ב־MQL5 Market ואין דליפה. המוצר "Saruja Adaptive Recovery" ב־MQL5 (מאת Ladislav Zikmund, פורסם ב־04.10.2026, $199) הוא של צד שלישי ולא קשור למפעיל (VERIFIED + ASSUMED לגבי הניתוק). פרמטרים (step, multiplier, levels, basket TP) **לא פורסמו מעולם** (UNKNOWN).
4. **ירידת תחילת נובמבר 2026** הייתה floating DD על פוזיציות sell שהוחזקו בזמן שהזהב עלה. ב־06.11 המפעיל דיווח על כ־−25% floating. ה־DD בחשבונות העוקבים עלה מ־24.12% ל־55.45%, בהתאמה ל־max DD של −56.55% בדף. ההפסד הממומש היחיד היה ב־03.11 (כ־−$196 בחשבון עוקב), וב־11.11 נסגרה העסקה הטובה ביותר (+6,999 pips). כלומר החשבון ניצל כי הזהב חזר הפעם (OBSERVED/ASSUMED).
5. **פסיקה: NO-GO, מאושר בראיות.** הגיל 3 חודשים (נדרשים 18 ומעלה), ה־DD 56.55% (התקרה 25%), אין hard SL, יש averaging, ויש היסטוריית ruin חוזרת של המפעיל. אין מספיק נתונים ל־SPEC של clone: חסרים חוק הכניסה ("SARUJA indicator"), חוק ה־target וחוק גודל הלוט.

---

## 1. עובדות על החשבון (דף פומבי, 20.11.2026, לפי ה־brief של המשימה)
- MT4, 100% XAUUSD, מינוף 1:1000. פתוח להעתקה מ־21.08.2026, ה־journey התחיל ב־01.09.2026, כלומר גיל של כ־3 חודשים.
- Yield של 337.18%, profit של $33,718, balance של $43,718, max DD של −56.55%. כ־2,151 עוקבים. דמי ביצוע של 35% מהרווח, שבועי, מינימום $100.
- אין טאב Trading history ואין export, ולכן אין נתונים ברמת עסקה ישירות מהדף.
- תשואה חודשית גאומטרית "על הנייר": (4.3718)^(1/2.63)−1 ≈ **75% בחודש** (OBSERVED, חישוב). זה מספר לא בר־קיימא בהינתן ההיסטוריה (ראו סעיף 3).

### מהלך ה־journey לפי Telegram של המפעיל (VERIFIED, t.me/s/SarujaEa)
| תאריך | דיווח |
|---|---|
| 01.09 | יום 1: +6.08% |
| 18.09 | רווח ממומש +14.5% בשבוע, floating loss "בערך באותו גודל" |
| 25.09 | balance $18,747, **Max DD 39.33%** |
| 02.10 | Phase 1 הושלם: $20,209 |
| 10.10 | floating DD −10.37% |
| 17.10 | "2 XAUUSD positions open", floating −6.42%, balance $24,093 |
| 31.10 | balance $32,204.90, +222% |
| 06.11 | **floating DD של כ־−25%**: "gold has not yet reacted with the downside move we expected… trades will remain open into next week" |
| 13.11 / 15.11 | Phase 2 הושלם: balance $40,085, +300.85% |

הערה: ה־max DD שבדף הוא −56.55%, והמפעיל דיווח 39.33% עד 31.10. הקפיצה מתיישבת עם אירוע נובמבר (ASSUMED). ב־Telegram, אחרי 06.11, לא פורסם מספר floating מעודכן.

---

## 2. מחקר רשת: תשובות לשאלות

### 2.1 האם הרובוט נמכר?
- **לא.** SmartRevenueHub (25.08.2026): "Saruja has never been sold, never given away, and… never leaked". לפי המקור, הוא לא מופיע ב־MQL5 Market, ב־CodeBase, בפורומים, באתרי cracks או ב־GitHub (VERIFIED במקור, והטענה עצמה היא של המקור).
- הודעת הפתיחה של הערוץ (02.02.2023): "Our trading is based on our Expert advisor (Saruja)… no need for a VPS server, trades are copied automatically by the RoboForex service" (VERIFIED). המודל העסקי הוא copy trading עם partner ID ‏SARUJA ו־fee, כלומר הכנסה מ־rebates ומ־performance fee, ולא מכירת תוכנה (VERIFIED/ASSUMED).
- ב־MQL5 יש את "Saruja Adaptive Recovery" (MT5, ‏$199, ‏v1.41, פורסם ב־04.10.2026, ‏Ladislav Zikmund). התיאור שלו: grid/recovery, ‏EMA/ATR/RSI, ‏M15 עם פילטר H1, ‏adaptive grid spacing, ‏basket profit, ו־"drawdown threshold is not a hard stop-loss" (VERIFIED). **אין ראיה שזה ה־EA של המפעיל** (ASSUMED שלא: מוכר אחר, MT5 במקום MT4, ופורסם אחרי הקריסה).
- ForexFactory, Forex Peace Army, FXBlue ו־YouTube: לא נמצאו thread או signal רלוונטיים בחיפוש (OBSERVED, החיפוש מוגבל וייתכן שהוחמצו). ב־Myfxbook נמצאו 4 חשבונות עוקבים (סעיף 2.3).
- המפעיל הזהיר מפני חשבונות מתחזים (29.08.2026): "The official and ONLY account… We do not operate or manage any other trading accounts" (VERIFIED). לפי SmartRevenueHub, 14–19 חשבונות נושאים את השם ומופעלים על ידי 9–11 אנשים שונים (VERIFIED במקור, והמספרים השתנו בין 25.08 ל־02.09).

### 2.2 מבנה והגדרות שפורסמו
**לא פורסם שום פרמטר של ה־EA** (UNKNOWN): אין step, multiplier, מספר levels, basket TP או שעות מסחר. מה שפורסם הוא רק הגדרות **העתקה**: MT4 Pro מעל $10k או ProCent מתחת, מינוף 1:1000 (ב־2023–2024 זה היה 1:500), **Full Swap-Free**, ‏Proportional בקואפיציינט 1, ‏Agent ID ‏SARUJA (VERIFIED, telegra.ph). הנימוק ל־swap-free: "medium- to longer-term positions that may remain open for several days, and occasionally weeks" (VERIFIED). המפעיל דוחה עוקבים שלא עומדים בהגדרות ("more than 200 accounts", ‏23.10.2026) (VERIFIED).

**מה שאפשר להסיק מהתנהגות פומבית:**
| מאפיין | ראיה | תגית |
|---|---|---|
| כיוון: short בלבד על XAUUSD | עוקבי JOURNEY ב־Myfxbook: Shorts 56/62 ו־59/65, Longs 0/0. עוקבי 2023: Shorts 19/21 ו־4/8, Longs 0/0. SRH: "Of 53 positions, 49 were short" | OBSERVED |
| כניסה נגד מגמה, "targets" טכניים | "price should go back down to 1960" (03.04.2023), "gap… at 1834" (12.10.2023), "would revisit the $3,800 levels" (24.08.2026) | VERIFIED (בהודעות) |
| מעט פוזיציות, הוספה במרווח קטן | "two open positions at 1856 and 1860" (12.10.2023). "2 XAUUSD positions open" (17.10.2026). "opened two positions last Friday" (22.07.2026) | VERIFIED. ה־step של כ־$4 נצפה במקרה אחד (OBSERVED) |
| בלי SL קשיח, החזקה עד target | "several opportunities to close… in profit… chose to remain committed to the original… targets" (24.07 ו־31.07.2026, וגם 10.07.2026 לגבי breakeven). Worst trade של −2,396 pips בעוקבי JOURNEY ושל −4,504/−5,275 pips בעוקבי 2023 | VERIFIED + OBSERVED |
| win rate ~90%, avg win > avg loss בפיפס (ב־JOURNEY) | twominuteforex: avg win 1,815 pips / avg loss −1,240 pips, ‏PF 22.67. ‏VitaliG: PF 13.10 | OBSERVED (על 62–65 עסקאות, מדגם קטן ותקופה של עלייה) |
| hedge או recovery בחירום | "additional BUY positions were opened before the market closed… a specific approach designed for situations like this" (08.08.2026, שלושה ימים לפני המחיקה) | VERIFIED (הטקסט). המכניקה UNKNOWN |
| גודל לוט ו־multiplier | עוקב cent: 29.44 lots ב־62 עסקאות (בערך 0.47 cent-lot בממוצע). אי אפשר לגזור multiplier | UNKNOWN |
| "AI" | אין שום פירוט של מודל. SRH: "never had a substantiated basis" | ASSUMED (שיווק) |
| שעות מסחר | לא פורסם. בעוקבים יש עסקאות בכל ה־sessions | UNKNOWN |

### 2.3 חשבונות ארוכים (12 חודשים ומעלה) על אותו EA
- **אין חשבון של המפעיל שחי 12 חודשים.** המחזור הארוך ביותר שתועד הוא 03.2026 עד 08.2026, כ־5.5 חודשים (VERIFIED).
- "SARUJA" של SARUJAIlight (מ־10.2024) ו־"Saruja EUR Pairs"/"Saruja EA Trade" של GlobalTraders88 (מ־11.2024) הם בעלי רקורד ארוך יותר, אבל של **מפעילים אחרים**, ואין שום הוכחה שזה אותו EA (UNKNOWN). לפי SRH: SARUJAIlight "slightly down over the last few months", ו־GlobalTraders88 "deep losses" (VERIFIED במקור, בלי מספרים).
- חשבונות עוקבים ב־Myfxbook (VERIFIED, נקראו ב־20.11.2026):

| חשבון Myfxbook (משתמש ציבורי) | תקופה | Gain | Max DD | עסקאות | הערה |
|---|---|---|---|---|---|
| boro15 / Saruja (RoboForex MT4 1:1000) | 2023–2024, עודכן לאחרונה 25.04.2024 | **−88.07%** | 89.70% | 8 | Balance $0. Worst trade 12.04 (השנה לא מוצגת) −5,275 pips. Shorts 4/8 |
| nonameaccount76 / Saruja EA (1:500) | 2023 | **−95.27%** | 96.78% | 21 | Worst trade 13.10 −4,504 pips. Shorts 19/21. Avg win 148 pips מול avg loss −4,296 pips |
| twominuteforex / Saruja (RoboForex USD Cent, MT4, 1:1000) | 09.2026 עד היום | +314.43% | **55.45%** | 62 | עוקב JOURNEY. Shorts 56/62. Worst −$766.72 / −2,396 pips (02.10). Best +6,999 pips (11.11) |
| VitaliG / SARUJA (***0482) | 09.2026 עד היום | +335.79% | **53.08%** | 65 | עוקב JOURNEY. ברשימת החשבונות של אותו משתמש מופיע גם "SARUJA-CENT (***3914)": ‏−69.28% / DD 96.49% (ASSUMED: עוקב SARUJA AI שקרס) |

### 2.4 הקריסות: אוגוסט 2026 והקודמות
| # | מחזור | עלייה מוצהרת | אירוע הקריסה | מקור |
|---|---|---|---|---|
| 1 | 02.2023 עד 04.2023 | "more than +1400%" | 12.04.2023: "account has stopped with a big loss… Saruja EA was still giving bearish signals… so we kept the trades open". Gold שבר את 2000 כלפי מעלה | Telegram (VERIFIED) |
| 2 | 08.2023 עד 10.2023 | "more than 400% in 8 weeks" | 13.10.2023: gold עלה מעל $60 ביום אחד (מלחמה במזה"ת). היו שתי פוזיציות sell ב־1856/1860 | Telegram + nonameaccount76 (worst trade 13.10, ‏−4,504 pips) (VERIFIED) |
| 3 | 01.2024 עד 03.2024 | "+900% in 12 weeks". Max DD מוצהר כבר בינואר: 50.24% | 01.03.2024: "substantial and unexpected loss due to a significant movement in gold prices within a few hours… the flaw in the system is the inability to deal with large price movements in a short period" | Telegram (VERIFIED) |
| 4 | 11.03.2024 עד 04.2024 | "~+200%" | ~12.04.2024: "price of gold moves more than $100 in less than 24 hours". ה־EA הופסק ("discontinue Saruja Ea") | Telegram (VERIFIED). ‏boro15 (worst 12.04) כנראה מכאן או ממחזור 1 (UNKNOWN) |
| 5 | 03.2026 עד 08.2026 (SARUJA AI, ‏aaab/22749275) | שיא +29,938.74% ב־16.07, כ־$690k–700k מ־$2,500. Max DD של ~−63% כבר בשבוע 3 | 2 sells נפתחו ביום שישי, 17.07. floating של כ־30% ב־22.07 ושל כ־15% ב־24.07. ויתור על סגירה ברווח ב־29.07. "additional BUY positions" ב־~07.08. Yield: ‏24,342% ב־04.08, ‏11,976% ב־05.08, ‏4,784% ב־07.08, ‏1,263% ב־10.08, ‏**−2.91%** ב־11.08. Max DD: **−99.21%**. Balance ‏$2,234. ‏3,211 עוקבים | Telegram + SRH + FXBrokerTrust (VERIFIED) |

**איך נסגר ה"basket" באוגוסט:** לא פורסם אם הייתה סגירה יזומה או stop-out (UNKNOWN). ה־balance ירד בהדרגה במשך כ־6 ימים (04.08–11.08), וזה מתיישב עם סגירות חלקיות או margin calls חוזרים יותר מאשר עם SL אחד (ASSUMED). post-mortem של המפעיל (24.08.2026): "Those positions moved into floating profit on several occasions… we chose to remain committed… underestimated the market conditions" (VERIFIED). **מספר הרמות:** UNKNOWN. מה שנכתב הוא "two positions", ואחריהן "additional BUY positions".
- **דפוס חוזר:** מאחר שהדמי ביצוע נגבים שבועית, ה־fees נשארים אצל המפעיל גם אחרי המחיקה (SRH, ‏VERIFIED במקור). אחרי כל קריסה נפתח חשבון חדש עם "journey" חדש (VERIFIED). בנוסף נפתח חשבון MT5 של אותו מפעיל ב־02.07.2026, לפני הקריסה, ובו כבר נרשמה החזרה של 84% מהרווח בתוך 48 שעות (SRH, ‏VERIFIED במקור).

### 2.5 ירידת תחילת נובמבר 2026 בחשבון החדש
- ב־06.11, לפי Telegram: "extremely volatile week… US elections… holding open positions with approximately −25% floating drawdown… gold has not yet reacted with the downside move we expected… enough room to manage the positions" (VERIFIED).
- עוקבים ב־Myfxbook: ה־DD היה 24.12% ב־snapshot של אינדקס החיפוש (highest ב־29.10), ועמד על 55.45% ב־20.11 (OBSERVED). ההפסד הממומש היחיד היה ב־03.11 (‏−$196.24 / −$133.80), וה־best trade (+6,999 pips) נסגר ב־11.11. אחריו באו 11 זכיות רצופות עד 19.11, וה־equity בשיא חדש (OBSERVED). המשמעות היא שה־drop מ־~230% ל־~50% היה **floating**, וה־sells נסגרו ברווח כשהזהב ירד בערך $70 (ASSUMED לפי 6,999 pips, כאשר 1 pip ב־Myfxbook לזהב = $0.01).
- **אירוע נובמבר זהה במבנה לאירועי 07.2026 ו־04.2023:** sells מוחזקים נגד ראלי ובלי SL. ההבדל היחיד הוא שהפעם המחיר חזר (ASSUMED).

---

## 3. דמיון מבני ל־BD, ל־Happy Gold ולמשפחות grid
| ציר | SARUJA (ציבורי) | Black Dragon (Ramil) | משפחת grid/averaging סגורה |
|---|---|---|---|
| כיוון | **short בלבד**, ומעט BUY בחירום (OBSERVED/VERIFIED) | basket averaging לפי סיגנל, לא מוגבל ל־short (ASSUMED, ידע הפרויקט) | לרוב דו־כיווני או לפי סיגנל |
| מספר פוזיציות בסל | 1–3 בדרך כלל (VERIFIED) | multi-level grid (ASSUMED) | 5–20+ levels |
| SL קשיח | אין (OBSERVED) | אין SL פנימי. ההגנה היא 15% חיצוני (ידע הפרויקט, ASSUMED) | בדרך כלל אין |
| יציאה | "target" טכני רחוק (avg win ~1,800 pips) | basket TP (ASSUMED) | basket TP קטן |
| זמן החזקה | ~יום בממוצע, ובזנב ימים עד שבועות (OBSERVED/VERIFIED) | שעות עד ימים (ASSUMED) | דומה |
| זנב סיכון | ראלי חד וחד־כיווני בזהב (VERIFIED, 5 אירועים) | תנועה חד־כיוונית חדה בזהב (ASSUMED) | אותו דבר |
| Happy Gold | UNKNOWN: אין לי מקור על מבנה HG במשימה הזאת, ולכן לא נקבע דמיון | | |

**שורה תחתונה:** SARUJA הוא **directional counter-trend averaging (short-bias) בלי SL**. זו משפחה שכנה ל־grid/martingale בפרופיל הסיכון: win rate גבוה וזנב שמוחק את החשבון. מבחינה מכנית הוא שונה מ־grid צפוף מרובה רמות (ASSUMED). חשש קורלציה עם BD: שניהם מפסידים בתנועות חדות בזהב, ו־SARUJA בעיקר **בראלי** (ASSUMED). כדי לבדוק אם הוא מפסיד בימי הקריסה של BD נדרשות עסקאות ברמת trade (UNKNOWN).

---

## 4. פסיקה מול המנדט
| קריטריון | סף | SARUJA | עובר? |
|---|---|---|---|
| תשואה חודשית כנה | ≥3% | 75% על הנייר במשך 2.6 חודשים. בהינתן 5 ruin במחזורים של 1–5.5 חודשים, התוחלת לטווח ארוך שלילית או לא מוגדרת (ASSUMED) | ❌ (לא כנה) |
| גיל | ≥18 חודשים | ~3 חודשים. המחזור הארוך ביותר של המפעיל: ~5.5 חודשים | ❌ |
| Equity DD | ≤25% | ‏−56.55% (בדף). בעוקבים 53–55%. במחזור הקודם −99.21% | ❌ |
| בלי grid או latency edge | | averaging נגד מגמה, בלי SL (OBSERVED) | ❌ |
| Hard SL | חובה | אין (OBSERVED + הצהרות המפעיל) | ❌ |
| דמי ביצוע | | 35% שבועי, והם לא מוחזרים במחיקה (VERIFIED) | ⚠️ |

**פסיקה: NO-GO.** הציפייה ל־NO-GO על הגיל ועל ה־DD **אושרה**, ויש לה בנוסף שלוש סיבות עצמאיות: אין SL, יש averaging, ויש היסטוריית ruin מתועדת של אותו מפעיל (5 פעמים מ־2023).
**אין המלצת מסחר, ההחלטה של נדב.** (נדב מעתיק כרגע. לפי ההיסטוריה, הסיכון לחשבון ההעתקה הוא מחיקה מלאה ולא ירידה חלקית. זו עובדה ולא המלצה.)

---

## 5. SPEC ל־clone: לא אפשרי כרגע. מה חסר
**אין מספיק מידע ציבורי ל־SPEC שאפשר להריץ.** חסרים:
1. **חוק הכניסה**: "SARUJA indicator", תנאי ה־sell (TF, אינדיקטורים, רמות) (UNKNOWN).
2. **חוק ההוספה**: מרחק (נצפה רק $4 פעם אחת), מספר הוספות מקסימלי, יחס לוטים (UNKNOWN).
3. **חוק היציאה**: איך נקבע ה־"target" (פיפס קבועים, רמה טכנית, basket TP בכסף) (UNKNOWN).
4. **גודל לוט** ביחס ל־equity (UNKNOWN).
5. **התנהגות חירום**: ה־"additional BUY" (hedge, reversal או recovery) (UNKNOWN).

**נתונים שיפתרו את זה (לפי עדיפות):**
- (א) **ההיסטוריה של חשבון ההעתקה של נדב עצמו**, read-only: open/close time, price, lots, direction, comment, swap. Claude מושך אותה מהצד שלו. **בלי מספרי חשבון בקבצים** (anonymized id בלבד). אנחנו לא נוגעים בטרמינלים של Benzaquen.
- (ב) אלטרנטיבה פומבית: עמודי Myfxbook של twominuteforex ו־VitaliG (עוקבי JOURNEY) כוללים טאב Trades. הנתונים נטענים דינמית, ולא שלפתי אותם (בלי login ובלי API פנימי). אפשר לצפות בהם ידנית בדפדפן כצד ציבורי, אם יוחלט.

**שלד היפותזה (ASSUMED, ניסוי עתידי בלבד, לא clone):** "SARUJA-skeleton + hard SL", כלומר רק ה־component של הכניסה. מכירה של XAUUSD בכניסה נגד מגמה אחרי extension (להגדרה מתוך הנתונים בסעיף א'), 1–3 הוספות ב־step ‏k·ATR, יציאה ב־target ‏R, ו־**hard SL לסל**. שאלת המחקר: האם חוק הכניסה נושא edge **כשיש SL**? אם לא, ה־edge כולו הוא ה־averaging והזנב, ומשליכים אותו. הריצה תהיה על 2019–2025 בטסטר, עם PREREG מראש, ספירת trials מצטברת (Holm/DSR), ו־holdout מ־27.10.2026 שלא נוגעים בו. זה **לא** ירוץ לפני שיש את נתוני (א), כדי לא לנחש triggers (לקח EXP13/14).

---

## 6. מקורות (נקראו ב־20.11.2026)
1. https://t.me/s/SarujaEa: כל ההיסטוריה הציבורית, 325 הודעות מ־02.02.2023 עד 15.11.2026 (VERIFIED)
2. https://telegra.ph/SARUJA-AI-Copy-Trading-Settings-08-23
3. https://smartrevenuehub.com/forex/saruja-10k-to-1m-journey (02.09.2026)
4. https://smartrevenuehub.com/forex/saruja-roboforex-accounts (25.08.2026)
5. https://smartrevenuehub.com/forex/roboforex-copyfx-saruja-ai-collapse (11.08.2026)
6. https://smartrevenuehub.com/forex/roboforex-copyfx-saruja-returns (23.08.2026, תקציר מתוך חיפוש)
7. https://www.fxbrokertrust.com/insights/roboforex-copyfx-saruja-ai-wipes-out-29938-gain
8. Myfxbook: members/twominuteforex/saruja/12257022 · members/VitaliG/saruja-0482/12201842 · members/boro15/saruja/10094162 · members/nonameaccount76/saruja-ea/10433793
9. https://www.mql5.com/en/market/product/199455 (Saruja Adaptive Recovery, צד שלישי)
10. דף האסטרטגיה: robomarkets.com/global-en/copy-trading/trader/aaaa/21596244 (נתונים לפי ה־brief, ה־fetch החזיר רק כותרת)

מגבלות: מספרי ה־Myfxbook משתנים בזמן אמת. ה־DD של 24.12% נלקח מ־snapshot באינדקס החיפוש, והתאריך המדויק שלו לא ידוע. לא בוצעו login, ‏follow, הודעות או רכישות.
