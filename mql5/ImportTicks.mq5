//+------------------------------------------------------------------+
//| ImportTicks: loads one chunk of real ticks into a custom symbol   |
//| (docs/CRASH_LINK_PLAN.md: Dukascopy XAUUSD 2016-2022 for the      |
//| tester). Reads MQL5\Files\dk_job.txt: "<custom>;<origin>;<file>"  |
//| and the binary file: records of int64 time_msc (server time),     |
//| double bid, double ask, sorted. Creates the custom symbol from    |
//| the origin's spec when missing, replaces ticks over the chunk's   |
//| time span, writes the result to dk_done.txt and closes the        |
//| terminal. Run by research/growth/dk_import.py only, in the        |
//| dedicated tester terminal C:\MT5_JEV_TEST. It never trades.       |
//+------------------------------------------------------------------+
#property script_show_inputs false

void Done(string s)
{
   int h = FileOpen("dk_done.txt", FILE_WRITE | FILE_TXT | FILE_ANSI);
   if(h != INVALID_HANDLE) { FileWriteString(h, s); FileClose(h); }
   TerminalClose(0);
}

void OnStart()
{
   int j = FileOpen("dk_job.txt", FILE_READ | FILE_TXT | FILE_ANSI);
   if(j == INVALID_HANDLE) { Done("ERR no job"); return; }
   string line = FileReadString(j); FileClose(j);
   string p[]; if(StringSplit(line, ';', p) != 3) { Done("ERR bad job " + line); return; }
   string sym = p[0], origin = p[1], file = p[2];
   bool custom = false;
   if(!SymbolExist(sym, custom))
   {
      if(!CustomSymbolCreate(sym, "Jev", origin)) { Done("ERR create " + IntegerToString(GetLastError())); return; }
   }
   SymbolSelect(sym, true);
   int h = FileOpen(file, FILE_READ | FILE_BIN);
   if(h == INVALID_HANDLE) { Done("ERR open " + file); return; }
   int n = (int)(FileSize(h) / 24);
   MqlTick t[]; ArrayResize(t, n);
   for(int i = 0; i < n; i++)
   {
      ZeroMemory(t[i]);
      t[i].time_msc = FileReadLong(h); t[i].bid = FileReadDouble(h); t[i].ask = FileReadDouble(h);
      t[i].time = (datetime)(t[i].time_msc / 1000); t[i].flags = TICK_FLAG_BID | TICK_FLAG_ASK;
   }
   FileClose(h);
   if(n == 0) { Done("OK 0"); return; }
   int r = CustomTicksReplace(sym, t[0].time_msc, t[n - 1].time_msc, t);
   Done(StringFormat("%s %d of %d err %d", r == n ? "OK" : "PART", r, n, GetLastError()));
}
