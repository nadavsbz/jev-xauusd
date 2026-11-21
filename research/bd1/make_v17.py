"""Builds DragonClone_v17.mq5 = v16 + a volatility floor on the level step (Grok t_bdcrash R1, 18.11.2026).
With StepVolK = 0 (default) it trades exactly like v16 (= v7 with all flags off).
  StepVolK   every grid distance is at least StepVolK x Ref5, where Ref5 = the median over the 5 previous server days of each
             day's median M15 bar range (high-low), fixed once per day from closed bars only (no look-ahead). Until 5 full days
             exist the rule is off. Only blocks or delays adds; no gate is widened, nothing is closed.
Usage: python research/bd1/make_v17.py   (after make_v16.py; compile in C:\\MT5_JEV_TEST from PowerShell)"""
src = open("mql5/DragonClone_v16.mq5", encoding="utf-8").read()
def rep(a, b):
    global src
    assert src.count(a) == 1, a[:70]; src = src.replace(a, b)

rep("input int    ThrottleAdds = 0;", """input double StepVolK = 0;            // v17 (Grok R1, 18.11.2026): level distance >= StepVolK x median M15 range of the last 5 days (0 = off)
input int    ThrottleAdds = 0;""")
rep("double V4Dist(int lvl) { return DistFor(lvl); }", """double Ref5()   // v17: median over the 5 previous server days of the day's median M15 range; once per day, closed bars only
  {
   static datetime day = 0; static double ref = 0;
   datetime d0 = iTime(_Symbol, PERIOD_D1, 0);
   if(d0 == 0 || d0 == day) return ref;
   MqlRates r[]; ArraySetAsSeries(r, false);
   int n = CopyRates(_Symbol, PERIOD_M15, d0 - 12 * 86400, d0 - 1, r);
   if(n <= 0) return ref;
   double dm[5]; int k = 0, end = n - 1;
   while(end >= 0 && k < 5)
     {
      datetime dd = r[end].time - r[end].time % 86400;
      double rg[]; int m = 0, j = end;
      while(j >= 0 && r[j].time - r[j].time % 86400 == dd) { ArrayResize(rg, m + 1); rg[m++] = r[j].high - r[j].low; j--; }
      if(m >= 20) { ArraySort(rg); dm[k++] = (m % 2 == 1) ? rg[m / 2] : (rg[m / 2 - 1] + rg[m / 2]) / 2; }
      end = j;
     }
   if(k < 5) return ref;
   ArraySort(dm); ref = dm[2]; day = d0;
   return ref;
  }
double V4Dist(int lvl) { double d = DistFor(lvl); if(StepVolK > 0) d = MathMax(d, StepVolK * Ref5()); return d; }""")
open("mql5/DragonClone_v17.mq5", "w", encoding="utf-8").write(src.replace("DragonClone_v16", "DragonClone_v17"))

s = open("research/bd1/sets/dcv16_2d.set", "rb").read().decode("utf-16")
nl = "\r\n" if "\r\n" in s else "\n"
i = s.index("ThrottleAdds=")
s = s[:i] + "StepVolK=0" + nl + s[i:]
open("research/bd1/sets/dcv17_2d.set", "wb").write(s.encode("utf-16"))
print("v17")
