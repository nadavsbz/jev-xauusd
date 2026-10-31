"""Builds DragonClone_v11.mq5 = v10 + two ideas taken from C1 (user 30.10.2026: "combine C1's strategies into the BD clone,
like a protection at half the drop"). With the default inputs it trades exactly like v10 (= v7).
  DonchMode   the C1 trend state of the symbol: Donchian ensemble {10,20,30,60,90,150,250} on closed H6 bars, long-short,
              mean state in [-1, 1]. 1: no new basket against a state of at least DonchThr; 2: ... and no new grid levels on
              the side against it
  DDScalePct  'half-drop' protection: when equity is DDScalePct below its peak since G_FloorFrom (the user's floor is 15%),
              the lot of new baskets and new levels is multiplied by DDScaleMult; back to full size at a new peak
Usage: python research/bd1/make_v11.py   (after make_v10.py)"""
src = open("mql5/DragonClone_v10.mq5", encoding="utf-8").read()
def rep(a, b):
    global src
    assert src.count(a) == 1, a[:60]; src = src.replace(a, b)

rep("input double G_BasketStopPct = 0;", """input int    DonchMode = 0;           // v11: C1 trend state filter: 0 off, 1 no new basket against it, 2 + no new levels against it
input double DonchThr = 0.5;          // v11: |state| at least this counts as a trend
input double DDScalePct = 0;          // v11: equity this % below its peak since G_FloorFrom -> smaller lots (0 = off)
input double DDScaleMult = 0.5;       // v11: lot multiplier while in that drawdown
input double G_BasketStopPct = 0;""")
rep("int TrendDir()   // v10", """double eqPeak = 0;
double DDMult()   // v11: 'half-drop' lot multiplier
  {
   if(DDScalePct <= 0) return 1.0;
   MqlDateTime d; TimeToStruct(TimeCurrent(), d);
   if(d.year * 10000 + d.mon * 100 + d.day < G_FloorFrom) return 1.0;
   double e = AccountInfoDouble(ACCOUNT_EQUITY); eqPeak = MathMax(eqPeak, e);
   return e < eqPeak * (1 - DDScalePct / 100) ? DDScaleMult : 1.0;
  }
double DonchState()   // v11: C1 Donchian ensemble, long-short, on closed H6 bars; computed once per H6 bar
  {
   static datetime bar = 0; static double stC = 0;
   if(DonchMode <= 0) return 0;
   datetime b0 = iTime(_Symbol, PERIOD_H6, 0);
   if(b0 == bar) return stC;
   double c[]; ArraySetAsSeries(c, false);
   int n = CopyClose(_Symbol, PERIOD_H6, 1, 600, c);
   if(n < 300) return stC;
   bar = b0; stC = 0;
   int LB[7] = {10, 20, 30, 60, 90, 150, 250};
   for(int k = 0; k < 7; k++)
     {
      int N = LB[k], H = N / 2; double q = 0;
      for(int i = N - 1; i < n; i++)
        {
         double hi = c[i], lo = c[i], xl = c[i], xh = c[i];
         for(int j = i - N + 1; j <= i; j++) { hi = MathMax(hi, c[j]); lo = MathMin(lo, c[j]); }
         for(int j = i - H + 1; j <= i; j++) { xl = MathMin(xl, c[j]); xh = MathMax(xh, c[j]); }
         if(q == 0) q = c[i] >= hi ? 1 : (c[i] <= lo ? -1 : 0);
         else if(q > 0 && c[i] <= xl) q = 0;
         else if(q < 0 && c[i] >= xh) q = 0;
        }
      stC += q / 7.0;
     }
   return stC;
  }
bool DonchAgainst(int side) { double s = DonchState(); return (side == 0 && s <= -DonchThr) || (side == 1 && s >= DonchThr); }
int TrendDir()   // v10""")
# lot scaling: both lot paths start from the autolot base
rep("""   double l = Lot_Init_;
   if(Autolot_) l = MathMax(0.01, NormalizeDouble(AccountInfoDouble(ACCOUNT_BALANCE) / Autolotsize_ * 0.01, 2));
   l = NormalizeDouble(l * MathPow(Martin_, level - 1), 2);""", """   double l = Lot_Init_;
   if(Autolot_) l = MathMax(0.01, NormalizeDouble(AccountInfoDouble(ACCOUNT_BALANCE) / Autolotsize_ * 0.01 * DDMult(), 2));
   l = NormalizeDouble(l * MathPow(Martin_, level - 1), 2);""")
rep("""double BaseLot()   // level-1 lot without MaxLot_
  {
   double l = Lot_Init_;
   if(Autolot_) l = MathMax(0.01, NormalizeDouble(AccountInfoDouble(ACCOUNT_BALANCE) / Autolotsize_ * 0.01, 2));""", """double BaseLot()   // level-1 lot without MaxLot_
  {
   double l = Lot_Init_;
   if(Autolot_) l = MathMax(0.01, NormalizeDouble(AccountInfoDouble(ACCOUNT_BALANCE) / Autolotsize_ * 0.01 * DDMult(), 2));""")
rep("return !InNewsPause() && !(TrendBlockAdds && TrendAgainst(side));",
    "return !InNewsPause() && !(TrendBlockAdds && TrendAgainst(side)) && !(DonchMode == 2 && DonchAgainst(side));")
rep("   if(fpUntil > TimeCurrent()) return;   // v10: pause after a floor cut",
    "   if(fpUntil > TimeCurrent()) return;   // v10: pause after a floor cut\n   if(DonchMode > 0 && DonchAgainst(dir)) return;   // v11: C1 trend state")
open("mql5/DragonClone_v11.mq5", "w", encoding="utf-8").write(src.replace("DragonClone_v10", "DragonClone_v11"))

s = open("research/bd1/sets/dcv10_2d.set", "rb").read().decode("utf-16")
nl = "\r\n" if "\r\n" in s else "\n"
i = s.index("G_BasketStopPct=")
s = s[:i] + nl.join(["DonchMode=0", "DonchThr=0.5", "DDScalePct=0", "DDScaleMult=0.5"]) + nl + s[i:]
open("research/bd1/sets/dcv11_2d.set", "wb").write(s.encode("utf-16"))
print("v11")
