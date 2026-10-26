"""Builds DragonClone_v9.mq5 = v7 + a volatility regime switch (docs/BD_REGIME2_PLAN.md, user request 26.10.2026).
When a basket OPENS, the average daily range of the last RegimeDays closed D1 bars (high-low)/close in % is compared with
RegimeRangePct: above it the basket runs for its whole life with the 'wide' settings (W_iTS, W_Fix, W_Dyn, W_DMul), else with the
normal inputs. RegimeRangePct = 0 -> identical to v7.
Usage: python research/bd1/make_v9.py   (after make_v7.py)"""
src = open("mql5/DragonClone_v7.mq5", encoding="utf-8").read()
def rep(a, b):
    global src
    assert src.count(a) == 1, a[:60]; src = src.replace(a, b)

rep("input double G_BasketStopPct = 0;", """input double RegimeRangePct = 0;      // v9: a basket opened when the 20-day avg daily range % is above this uses the W_ settings (0 = off = v7)
input int    RegimeDays = 20;          // v9: closed D1 bars in that average
input int    W_iTS = 900;              // v9 wide regime: trailing start (points)
input int    W_Fix = 3500;             // v9 wide regime: Fix_Distance
input int    W_Dyn = 1500;             // v9 wide regime: Dynamic_distance_start
input double W_DMul = 1.0;             // v9 wide regime: Distance_multiplier
input double G_BasketStopPct = 0;""")
rep("""double DistFor(int level)  // distance before opening order number `level` (2..N), in price
  {
   if(level < Order_dinamic_distance) return Fix_Distance * _Point;
   return Dynamic_distance_start * _Point * MathPow(Distance_multiplier, level - Order_dinamic_distance);
  }""", """bool wideB[2]; int curSide = 0;   // v9: regime of each side's basket, fixed when it opens; the side being processed
bool RegimeWide()
  {
   if(RegimeRangePct <= 0) return false;
   double s = 0; int n = 0;
   for(int i = 1; i <= RegimeDays; i++)
     {
      double h = iHigh(_Symbol, PERIOD_D1, i), l = iLow(_Symbol, PERIOD_D1, i), c = iClose(_Symbol, PERIOD_D1, i);
      if(c > 0 && h >= l) { s += (h - l) / c * 100; n++; }
     }
   return n >= RegimeDays / 2 && s / n > RegimeRangePct;
  }
int    TS()   { return wideB[curSide] ? W_iTS : iTS; }
double DistFor(int level)  // distance before opening order number `level` (2..N), in price
  {
   bool w = wideB[curSide];
   if(level < Order_dinamic_distance) return (w ? W_Fix : Fix_Distance) * _Point;
   return (w ? W_Dyn : Dynamic_distance_start) * _Point * MathPow(w ? W_DMul : Distance_multiplier, level - Order_dinamic_distance);
  }""")
rep("""   for(int side = 0; side < 2; side++)
     {
      Bsk b; Scan(side, b);""", """   for(int side = 0; side < 2; side++)
     {
      curSide = side;
      Bsk b; Scan(side, b);""")
rep("if(move >= iTS * _Point) { trailOn[side] = true;", "if(move >= TS() * _Point) { trailOn[side] = true;")
rep("   bool opened = false;\n", "   bool opened = false;\n   wideB[dir] = RegimeWide();   // v9: the regime is fixed for the life of the basket\n")
open("mql5/DragonClone_v9.mq5", "w", encoding="utf-8").write(src.replace("DragonClone_v7", "DragonClone_v9"))
print("v9")
