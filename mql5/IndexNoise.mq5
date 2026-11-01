//+------------------------------------------------------------------+
//| IndexNoise: test EA for I2 in research/stable/second4.py          |
//| (Zarattini, Aziz & Barbon 2024 'noise area' intraday momentum,    |
//| adapted to H1). At each close of the server-hour bars 16..21:     |
//| long above upper, short below lower, flat inside; flat at the     |
//| close of bar 22. Fixed lots: it measures the edge per trade and   |
//| the real ECN costs, not the sizing.                               |
//+------------------------------------------------------------------+
#property strict
#include <Trade/Trade.mqh>
input int    OpenHour  = 16;     // server hour whose bar open is the day open O (NY 9:00)
input int    LastCheck = 21;     // last check bar (its close = NY 15:00)
input int    ExitHour  = 22;     // flat at the close of this bar (NY 16:00)
input int    Lookback  = 14;     // days in the noise average
input double Lots      = 1.0;
input long   Magic     = 7302;

CTrade tr;
datetime lastBar = 0;

// day start (00:00) of a time
datetime Day(datetime t) { return t - t % 86400; }

// open of the OpenHour bar and close of hour k on day d; false when missing
bool DayVals(const MqlRates &r[], int n, datetime d, int k, double &o, double &c)
{
   o = 0; c = 0;
   for(int i = 0; i < n; i++)
   {
      if(Day(r[i].time) != d) continue;
      MqlDateTime t; TimeToStruct(r[i].time, t);
      if(t.hour == OpenHour) o = r[i].open;
      if(t.hour == k) c = r[i].close;
   }
   return o > 0 && c > 0;
}

int Pos()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
      if(PositionGetTicket(i) > 0 && PositionGetInteger(POSITION_MAGIC) == Magic && PositionGetString(POSITION_SYMBOL) == _Symbol)
         return PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 1 : -1;
   return 0;
}

void Go(int q)
{
   int p = Pos();
   if(p == q) return;
   if(p != 0) tr.PositionClose(_Symbol);
   if(q > 0) tr.Buy(Lots, _Symbol); else if(q < 0) tr.Sell(Lots, _Symbol);
}

int OnInit() { tr.SetExpertMagicNumber(Magic); return INIT_SUCCEEDED; }

void OnTick()
{
   datetime b = iTime(_Symbol, PERIOD_H1, 0);
   if(b == lastBar) return;
   lastBar = b;
   MqlRates r[]; int n = CopyRates(_Symbol, PERIOD_H1, 1, 24 * (Lookback + 12), r);   // r[n-1] = the bar that just closed
   if(n < 24 * (Lookback + 2)) return;
   MqlDateTime t; TimeToStruct(r[n - 1].time, t); int k = t.hour;
   if(k == ExitHour || Day(r[n - 1].time) != Day(b)) { Go(0); return; }      // the day's exit (or a new day began)
   if(k < OpenHour || k > LastCheck) return;
   datetime d = Day(r[n - 1].time);
   double o, c; if(!DayVals(r, n, d, k, o, c)) return;
   // previous trading day's ExitHour close, and the noise average of the Lookback trading days before today
   double prev = 0, sum = 0; int m = 0;
   for(datetime e = d - 86400; e > d - 86400 * (Lookback + 12) && m < Lookback; e -= 86400)
   {
      double oe, ce, pe, xe;
      if(!DayVals(r, n, e, k, oe, ce)) continue;
      if(prev == 0 && DayVals(r, n, e, ExitHour, pe, xe)) prev = xe;
      sum += MathAbs(ce / oe - 1); m++;
   }
   if(m < Lookback || prev == 0) return;
   double s = sum / m, up = MathMax(o, prev) * (1 + s), lo = MathMin(o, prev) * (1 - s);
   Go(c > up ? 1 : (c < lo ? -1 : 0));
}
