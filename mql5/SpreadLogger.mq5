// SpreadLogger: research-only EA, never trades. For each target time (server clock, unix seconds, one per line in
// Common\Files\t391_ts.txt, sorted) writes every tick within +-5 s: time_msc,bid,ask,spread_points to Common\Files\t391_spread.csv.
// Used for Grok t391/t392 (tester tick spread at live entry/add times). 25.11.2026.
#property strict
long T[]; int n = 0, k = 0, fh = INVALID_HANDLE;
int OnInit()
  {
   int f = FileOpen("t391_ts.txt", FILE_READ | FILE_TXT | FILE_COMMON | FILE_ANSI);
   if(f == INVALID_HANDLE) return INIT_FAILED;
   while(!FileIsEnding(f)) { string s = FileReadString(f); if(StringLen(s) > 0) { ArrayResize(T, n + 1); T[n++] = StringToInteger(s); } }
   FileClose(f);
   fh = FileOpen("t391_spread.csv", FILE_WRITE | FILE_TXT | FILE_COMMON | FILE_ANSI);
   FileWriteString(fh, "target,time_msc,bid,ask,spread_points\n");
   return INIT_SUCCEEDED;
  }
void OnTick()
  {
   MqlTick t; if(!SymbolInfoTick(_Symbol, t)) return;
   long s = (long)t.time;
   while(k < n && T[k] + 5 < s) k++;
   for(int j = k; j < n && T[j] - 5 <= s; j++)
      FileWriteString(fh, StringFormat("%I64d,%I64d,%.2f,%.2f,%d\n", T[j], t.time_msc, t.bid, t.ask, (int)MathRound((t.ask - t.bid) / _Point)));
  }
void OnDeinit(const int r) { if(fh != INVALID_HANDLE) FileClose(fh); }
