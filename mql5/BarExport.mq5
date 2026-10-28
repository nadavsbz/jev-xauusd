//+------------------------------------------------------------------+
//| BarExport: tester-only helper. Never trades. On every new bar of |
//| the chart period it writes the previous bar (time, OHLC, tick    |
//| volume, spread) to a CSV in the Common Files folder, so crash-day |
//| research (docs/BD_CRASH_SIGNS.md) has the same prices the clone   |
//| traded on.                                                       |
//+------------------------------------------------------------------+
#property strict
input string OutName = "bars";   // file: <OutName>_<symbol>_<period>.csv in Common\Files

int fh = INVALID_HANDLE;
datetime last = 0;

int OnInit()
  {
   string f = StringFormat("%s_%s_%s.csv", OutName, _Symbol, EnumToString((ENUM_TIMEFRAMES)_Period));
   fh = FileOpen(f, FILE_WRITE | FILE_CSV | FILE_COMMON | FILE_ANSI, ',');
   if(fh == INVALID_HANDLE) return INIT_FAILED;
   FileWrite(fh, "time", "open", "high", "low", "close", "tick_volume", "spread");
   return INIT_SUCCEEDED;
  }

void OnTick()
  {
   datetime t = iTime(_Symbol, _Period, 0);
   if(t == last) return;
   last = t;
   MqlRates r[]; ArraySetAsSeries(r, true);
   if(CopyRates(_Symbol, _Period, 1, 1, r) != 1) return;
   FileWrite(fh, (long)r[0].time, DoubleToString(r[0].open, _Digits), DoubleToString(r[0].high, _Digits), DoubleToString(r[0].low, _Digits),
             DoubleToString(r[0].close, _Digits), (long)r[0].tick_volume, r[0].spread);
  }

void OnDeinit(const int reason) { if(fh != INVALID_HANDLE) FileClose(fh); }
