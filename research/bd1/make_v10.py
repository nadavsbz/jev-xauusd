"""Builds DragonClone_v10.mq5 = v7 + three mechanisms against the floor cuts that erase the grid's profit
(docs/BD_EVERYYEAR_PLAN.md, round 3; user 29.10.2026: profitable every year, >= 20%). With the default inputs it trades exactly like v7.
  FloorPauseDays  after a floor cut, no new baskets for this many days (the cuts cluster: 11+12.8.2020, three in April 2023)
  TrendDays/TrendK/TrendMode  a strong trend = the move of the last TrendDays closed D1 bars is above TrendK x the average D1 range
                  of the last 20 bars; TrendMode 1: no new basket against it, 2: no new basket at all
  TrendBlockAdds  ...and no new grid levels on the side that is against the trend (the depth that reaches the floor)
Usage: python research/bd1/make_v10.py   (after make_v7.py)"""
src = open("mql5/DragonClone_v7.mq5", encoding="utf-8").read()
def rep(a, b):
    global src
    assert src.count(a) == 1, a[:60]; src = src.replace(a, b)

rep("input double G_BasketStopPct = 0;", """input int    FloorPauseDays = 0;      // v10: after a floor cut, no new baskets for this many days (0 = off)
input int    TrendDays = 0;           // v10: strong trend = move of the last TrendDays closed D1 bars ... (0 = off)
input double TrendK = 2.0;            // v10: ... above this x the average D1 range of the last 20 bars
input int    TrendMode = 1;           // v10: 1 = no new basket against the trend, 2 = no new basket at all
input bool   TrendBlockAdds = false;  // v10: no new grid levels on the side against the trend
input double G_BasketStopPct = 0;""")
rep("double flFloor = 0; datetime flSet = 0;", """double flFloor = 0; datetime flSet = 0; datetime fpUntil = 0;
int TrendDir()   // v10: +1 strong up, -1 strong down, 0 none; closed D1 bars only, computed once per D1 bar
  {
   static datetime bar = 0; static int dirC = 0;
   if(TrendDays <= 0) return 0;
   datetime b0 = iTime(_Symbol, PERIOD_D1, 0);
   if(b0 == bar) return dirC;
   bar = b0; dirC = 0;
   double c1 = iClose(_Symbol, PERIOD_D1, 1), c0 = iClose(_Symbol, PERIOD_D1, 1 + TrendDays), s = 0; int n = 0;
   for(int i = 1; i <= 20; i++) { double h = iHigh(_Symbol, PERIOD_D1, i), l = iLow(_Symbol, PERIOD_D1, i); if(h > 0 && h >= l) { s += h - l; n++; } }
   if(n < 10 || c0 <= 0) return 0;
   double mv = c1 - c0, r = s / n;
   dirC = mv > TrendK * r ? 1 : (mv < -TrendK * r ? -1 : 0);
   return dirC;
  }
bool TrendAgainst(int side) { int t = TrendDir(); return (side == 0 && t < 0) || (side == 1 && t > 0); }""")
rep("bool V4AddOk(int side, Bsk &b, double lot) { return !InNewsPause(); }",
    "bool V4AddOk(int side, Bsk &b, double lot) { return !InNewsPause() && !(TrendBlockAdds && TrendAgainst(side)); }")
rep("      if(FloorHit()) { CloseSide(0); CloseSide(1); continue; }",
    "      if(FloorHit()) { CloseSide(0); CloseSide(1); if(FloorPauseDays > 0) fpUntil = TimeCurrent() + FloorPauseDays * 86400; continue; }")
rep("      if(dir == 1 && d1 > ed) return;\n     }\n   Bsk b; Scan(dir, b);", """      if(dir == 1 && d1 > ed) return;
     }
   if(fpUntil > TimeCurrent()) return;   // v10: pause after a floor cut
   if(TrendDays > 0 && (TrendMode == 2 ? TrendDir() != 0 : TrendAgainst(dir))) return;   // v10: trend block
   Bsk b; Scan(dir, b);""")
open("mql5/DragonClone_v10.mq5", "w", encoding="utf-8").write(src.replace("DragonClone_v7", "DragonClone_v10"))

# base set for the tester: dcv7_2d.set + the new inputs at their defaults (run_queue needs every overridden input in the base set)
s = open("research/bd1/sets/dcv7_2d.set", "rb").read().decode("utf-16")
nl = "\r\n" if "\r\n" in s else "\n"
k = "G_BasketStopPct="
i = s.index(k)
s = s[:i] + nl.join(["FloorPauseDays=0", "TrendDays=0", "TrendK=2.0", "TrendMode=1", "TrendBlockAdds=false"]) + nl + s[i:]
open("research/bd1/sets/dcv10_2d.set", "wb").write(s.encode("utf-16"))
print("v10")
