"""Builds DragonClone_v8.mq5 = v7 + a grid spacing that widens with volatility (docs/BD_OPT_PLAN.md, code round).
Every distance (fixed and dynamic) is multiplied by s = clamp(ATR(H1,14) / ATR(H1, 14 x AtrDistLong), 1, AtrDistMax) ^ AtrDistK,
both ATRs on closed bars; s only widens (never below 1), so calm-hour behaviour is unchanged. AtrDistK = 0 -> identical to v7.
Usage: python research/bd1/make_v8.py   (after make_v7.py)"""
src = open("mql5/DragonClone_v7.mq5", encoding="utf-8").read()
OLD_DIST = """double DistFor(int level)  // distance before opening order number `level` (2..N), in price
  {
   if(level < Order_dinamic_distance) return Fix_Distance * _Point;
   return Dynamic_distance_start * _Point * MathPow(Distance_multiplier, level - Order_dinamic_distance);
  }"""
NEW_DIST = """double AtrScale()   // v8: >= 1, widens every grid distance in volatile hours (1 when AtrDistK = 0)
  {
   if(AtrDistK <= 0) return 1;
   double a[], b[];
   if(CopyBuffer(hAtrS, 0, 1, 1, a) != 1 || CopyBuffer(hAtrL, 0, 1, 1, b) != 1 || b[0] <= 0) return 1;
   return MathPow(MathMin(MathMax(a[0] / b[0], 1.0), AtrDistMax), AtrDistK);
  }
double DistFor(int level)  // distance before opening order number `level` (2..N), in price
  {
   double s = AtrScale();
   if(level < Order_dinamic_distance) return s * Fix_Distance * _Point;
   return s * Dynamic_distance_start * _Point * MathPow(Distance_multiplier, level - Order_dinamic_distance);
  }"""
assert src.count(OLD_DIST) == 1
src = src.replace(OLD_DIST, NEW_DIST)
OLD_IN = "input double G_BasketStopPct = 0;"
assert src.count(OLD_IN) == 1
src = src.replace(OLD_IN, """input double AtrDistK = 0;            // v8: grid distances x (ATR(H1,14)/long ATR(H1))^K when above 1 (0 = off = v7)
input int    AtrDistLong = 20;         // v8: the long ATR is ATR(H1, 14 x this)
input double AtrDistMax = 3;           // v8: cap of the ATR ratio
""" + OLD_IN)
OLD_H = "int hEma, hEmaD;"
assert src.count(OLD_H) == 1
src = src.replace(OLD_H, "int hEma, hEmaD, hAtrS = INVALID_HANDLE, hAtrL = INVALID_HANDLE;")
OLD_I = "   if(hEma == INVALID_HANDLE || hEmaD == INVALID_HANDLE) return INIT_FAILED;"
assert src.count(OLD_I) == 1
src = src.replace(OLD_I, OLD_I + """
   if(AtrDistK > 0)
     {
      hAtrS = iATR(_Symbol, PERIOD_H1, 14); hAtrL = iATR(_Symbol, PERIOD_H1, 14 * AtrDistLong);
      if(hAtrS == INVALID_HANDLE || hAtrL == INVALID_HANDLE) return INIT_FAILED;
     }""")
open("mql5/DragonClone_v8.mq5", "w", encoding="utf-8").write(src.replace("DragonClone_v7", "DragonClone_v8"))
print("v8")
