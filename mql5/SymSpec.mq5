//+------------------------------------------------------------------+
//| SymSpec: tester-only helper, never trades. Writes one line per   |
//| test to Common\Files\symspec.csv: the symbol's contract specs,   |
//| its median daily range and median spread over the test period.   |
//| Used to scale the Black Dragon clone to other symbols            |
//| (docs/BD_V7_PLAN.md, part 4: other RoboForex assets).            |
//+------------------------------------------------------------------+
#property strict

double dayHi = 0, dayLo = 0, ranges[], spreads[];
int day = -1, nr = 0, ns = 0;
datetime lastBar = 0, firstT = 0;

void OnTick()
  {
   double b = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(firstT == 0) firstT = TimeCurrent();
   MqlDateTime t; TimeToStruct(TimeCurrent(), t);
   if(t.day_of_year != day)
     {
      if(day >= 0 && dayHi > dayLo) { ArrayResize(ranges, nr + 1); ranges[nr++] = dayHi - dayLo; }
      day = t.day_of_year; dayHi = b; dayLo = b;
     }
   dayHi = MathMax(dayHi, b); dayLo = MathMin(dayLo, b);
   datetime bt = iTime(_Symbol, PERIOD_M15, 0);
   if(bt != lastBar) { lastBar = bt; ArrayResize(spreads, ns + 1); spreads[ns++] = (double)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD); }
  }

double Median(double &a[], int n)
  {
   if(n == 0) return 0;
   double c[]; ArrayCopy(c, a, 0, 0, n); ArraySort(c);
   return n % 2 ? c[n / 2] : (c[n / 2 - 1] + c[n / 2]) / 2;
  }

void OnDeinit(const int reason)
  {
   int h = FileOpen("symspec.csv", FILE_READ | FILE_WRITE | FILE_CSV | FILE_COMMON | FILE_ANSI, ',');
   if(h == INVALID_HANDLE) return;
   if(FileSize(h) == 0) FileWrite(h, "symbol", "from", "to", "digits", "point", "contract", "tick_value", "tick_size", "vol_min", "vol_step",
                                  "profit_ccy", "median_day_range", "median_spread_pts", "days", "last_bid");
   FileSeek(h, 0, SEEK_END);
   FileWrite(h, _Symbol, TimeToString(firstT, TIME_DATE), TimeToString(TimeCurrent(), TIME_DATE),
             (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS), DoubleToString(_Point, 8), SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE),
             DoubleToString(SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), 6), DoubleToString(SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE), 8),
             SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP), SymbolInfoString(_Symbol, SYMBOL_CURRENCY_PROFIT),
             DoubleToString(Median(ranges, nr), 6), Median(spreads, ns), nr, DoubleToString(SymbolInfoDouble(_Symbol, SYMBOL_BID), 6));
   FileClose(h);
  }
