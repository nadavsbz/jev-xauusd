"""Builds DragonClone_v7.mq5: the frozen v3 + the user's floor guard + every crash-day mechanism behind its own flag
(docs/BD_V7_PLAN.md, user request 26.10.2026). With the default inputs it trades exactly like v3 (+ floor off).
Flags:
  LotAfterOverlap  1..3 as v4a; 4 = after an Overlap the ladder restarts from the base lot by the open count
                   (user, 30.7: add by what was closed, do not continue from the maximum lots)
  MaxLotMult       cap every lot at base lot x this (a MaxLot_ that scales with the balance; 0 = off)
  DayOffMask       no new baskets on these weekdays (v4f)
  NewsPauseFrom/Min fixed daily pause (v4c)
  NewsFile         pause around the events listed in Common\\Files\\<NewsFile> (one 'unix_time' per line):
                   NewsBeforeMin before .. NewsAfterMin after, no new baskets and no adds (0/'' = off)
Built in two steps: make_v4.build (hooks) -> make_v5.build (floor guard + v5b partial-cut inputs, off by default)."""
import make_v4, make_v5

LOT = """double BaseLot()   // level-1 lot without MaxLot_
  {
   double l = Lot_Init_;
   if(Autolot_) l = MathMax(0.01, NormalizeDouble(AccountInfoDouble(ACCOUNT_BALANCE) / Autolotsize_ * 0.01, 2));
   return l;
  }
double V4Lot(int side, Bsk &b, double lot)
  {
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   if(LotAfterOverlap > 0 && ovCnt[side] > 0)
     {
      double cap = LotAfterOverlap == 1 ? ovOldV[side] : LotAfterOverlap == 2 ? ovNewV[side] : LotAfterOverlap == 3 ? ovNewV[side] / Martin_
                 : BaseLot() * MathPow(Martin_, b.n);
      lot = MathMin(lot, MathMax(NormalizeDouble(cap, 2), vmin));
     }
   if(MaxLotMult > 0) lot = MathMin(lot, MathMax(NormalizeDouble(BaseLot() * MaxLotMult, 2), vmin));
   return lot;
  }"""

PAUSE = """long nwT[]; int nwN = -1;
bool InNewsPause()
  {
   datetime now = TimeCurrent();
   if(NewsPauseFrom > 0 && NewsPauseMin > 0)
     {
      MqlDateTime t; TimeToStruct(now, t);
      int m = t.hour * 60 + t.min, s = (NewsPauseFrom / 100) * 60 + NewsPauseFrom % 100;
      if(t.day_of_week >= 1 && t.day_of_week <= 5 && m >= s && m < s + NewsPauseMin) return true;
     }
   if(NewsFile == "") return false;
   if(nwN < 0)
     {
      nwN = 0;
      int h = FileOpen(NewsFile, FILE_READ | FILE_TXT | FILE_COMMON | FILE_ANSI);
      if(h == INVALID_HANDLE) { Print("v7: news file not found: ", NewsFile); return false; }
      while(!FileIsEnding(h)) { string s = FileReadString(h); if(StringLen(s) < 5) continue; ArrayResize(nwT, nwN + 1); nwT[nwN++] = StringToInteger(s); }
      FileClose(h); PrintFormat("v7: %d news events loaded", nwN);
     }
   static int k = 0;   // the file is sorted and tester time only moves forward: skip the events whose window has ended
   while(k < nwN && nwT[k] + NewsAfterMin * 60 <= now) k++;
   return k < nwN && now >= nwT[k] - NewsBeforeMin * 60;
  }"""

ENTRY = """bool V4EntryOk()
  {
   if(InNewsPause()) return false;
   if(DayOffMask <= 0) return true;
   MqlDateTime t; TimeToStruct(TimeCurrent(), t);
   return t.day_of_week < 1 || t.day_of_week > 5 || (DayOffMask & (1 << (t.day_of_week - 1))) == 0;
  }"""

INPUTS = [
 "input int    LotAfterOverlap = 0;     // v7: after an Overlap cap the next lots: 1 closed oldest, 2 closed newest, 3 closed newest / Martin_, 4 base lot x Martin_^open count (0 = off)",
 "input double MaxLotMult = 0;          // v7: cap every lot at the level-1 lot x this (0 = off)",
 "input int    DayOffMask = 0;          // v7: weekdays without NEW baskets, bits Mon=1 Tue=2 Wed=4 Thu=8 Fri=16 (0 = off)",
 "input int    NewsPauseFrom = 0;       // v7: fixed daily pause start, server HHMM (0 = off)",
 "input int    NewsPauseMin = 0;        // v7: ...its length in minutes",
 "input string NewsFile = \"\";           // v7: event times file in Common\\\\Files, one unix time (server clock) per line ('' = off)",
 "input int    NewsBeforeMin = 30;      // v7: pause starts this many minutes before an event",
 "input int    NewsAfterMin = 60;       // v7: ...and ends this many minutes after it",
]

if __name__ == "__main__":
    make_v4.VARIANTS["v7h"] = ("all crash-day flags (v7)", INPUTS, "double ovNewV[2], ovOldV[2]; int ovCnt[2];",
        {"lot": LOT, "add": "bool V4AddOk(int side, Bsk &b, double lot) { return !InNewsPause(); }", "entry": ENTRY, "extra": PAUSE,
         "ov": make_v4.VARIANTS["v4a"][3]["ov"], "reset": make_v4.VARIANTS["v4a"][3]["reset"]})
    make_v4.build("v7h", *make_v4.VARIANTS["v7h"])
    make_v5.build("v7", "floor guard + partial-cut inputs on all crash-day flags (v7h)", *make_v5.VARIANTS["v5b"][1:], src="mql5/DragonClone_v7h.mq5")
    print("v7")
