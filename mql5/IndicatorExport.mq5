//+------------------------------------------------------------------+
//| IndicatorExport: writes the buffers of a compiled indicator to CSV |
//| (docs/CRASH_DETECT_PLAN.md, stage 1b, signal T7). Tester only.    |
//| It never trades. One line per closed bar: time, then buffers 0..N |
//| of the PREVIOUS bar (shift 1), so every value was known at the    |
//| close of that bar (no look-ahead).                                |
//+------------------------------------------------------------------+
#property strict
// the tester loads an iCustom indicator automatically only when its name is a constant; with an input name it
// must be declared (review PR #34)
#property tester_indicator "Strong_Support.ex5"
#property tester_indicator "Trend AI.ex5"
#property tester_indicator "Trend Catcher.ex5"
input string IndicatorName = "Strong_Support";   // path under MQL5/Indicators, without .ex5
input int    MaxBuffers    = 10;                 // buffers tried; the ones that fail are written as empty
input string OutFile       = "indicator_export.csv";

int handle = INVALID_HANDLE, fh = INVALID_HANDLE;
datetime last_bar = 0;
long     valid = 0;          // buffer values actually read: 0 at the end = the export failed (review PR #34)

int OnInit()
  {
   handle = iCustom(_Symbol, _Period, IndicatorName);
   if(handle == INVALID_HANDLE) { Print("iCustom failed: ", GetLastError()); return INIT_FAILED; }
   fh = FileOpen(OutFile, FILE_WRITE | FILE_CSV | FILE_ANSI | FILE_COMMON, ',');
   if(fh == INVALID_HANDLE) { Print("file open failed: ", GetLastError()); return INIT_FAILED; }
   string head = "time,open,high,low,close";
   for(int b = 0; b < MaxBuffers; b++) head += ",b" + IntegerToString(b);
   FileWriteString(fh, head + "\n");
   return INIT_SUCCEEDED;
  }

void OnTick()
  {
   datetime t = iTime(_Symbol, _Period, 1);
   if(t == last_bar || t == 0) return;
   last_bar = t;
   string line = TimeToString(t, TIME_DATE | TIME_MINUTES) + "," +
                 DoubleToString(iOpen(_Symbol, _Period, 1), _Digits) + "," + DoubleToString(iHigh(_Symbol, _Period, 1), _Digits) + "," +
                 DoubleToString(iLow(_Symbol, _Period, 1), _Digits) + "," + DoubleToString(iClose(_Symbol, _Period, 1), _Digits);
   double v[1];
   for(int b = 0; b < MaxBuffers; b++)
     {
      if(CopyBuffer(handle, b, 1, 1, v) == 1 && v[0] != EMPTY_VALUE) { line += "," + DoubleToString(v[0], 6); valid++; }
      else line += ",";
     }
   FileWriteString(fh, line + "\n");
  }

void OnDeinit(const int reason)
  {
   if(fh != INVALID_HANDLE) { FileWriteString(fh, "#valid_values=" + IntegerToString(valid) + "\n"); FileClose(fh); }
   if(valid == 0) Print("EXPORT FAILED: no buffer value was read");
   if(handle != INVALID_HANDLE) IndicatorRelease(handle);
  }
