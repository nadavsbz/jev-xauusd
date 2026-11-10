//+------------------------------------------------------------------+
//| IndexMR: Connors RSI(2) mean reversion, long only, on an index CFD |
//| (docs/THIRD_COMPONENT_PLAN.md, candidate 1, rules frozen 10.11.2026)|
//| Once a day at DecideHHMM (server time) the price of the M15 bar   |
//| that just closed is the day's "close". On that daily series:      |
//|   entry if RSI(2) < RsiLevel and close > SMA(SmaLong)             |
//|   exit  if close > SMA(SmaExit)                                   |
//| Size: notional = equity x Notional (no stop).                     |
//| Server = New York + 7h: US cash close 16:00 NY = 23:00 server.    |
//|   .USTECHCash/.US500Cash 2245, .DE40Cash 1815, .JP225Cash 0745    |
//+------------------------------------------------------------------+
#property strict
#include <Trade\Trade.mqh>

input int    DecideHHMM = 2245;   // server time of the daily decision (the M15 bar ending then is the day's close)
input int    RsiPeriod  = 2;
input double RsiLevel   = 10;
input int    SmaLong    = 200;
input int    SmaExit    = 5;
input double Notional   = 1.0;    // position notional as a multiple of equity
input long   Magic      = 7401;

CTrade trade;
datetime lastDay = 0;

int Daily(double &c[])   // the daily series: close of the M15 bar that ends at DecideHHMM, one per day, oldest first
  {
   MqlRates R[]; int n = CopyRates(_Symbol, PERIOD_M15, 1, 96 * 330, R);
   if(n <= 0) return 0;
   int hh = DecideHHMM / 100, mm = DecideHHMM % 100, k = 0;
   ArrayResize(c, n);
   for(int i = 0; i < n; i++)
     {
      MqlDateTime t; TimeToStruct(R[i].time + 15 * 60, t);   // bar end time
      if(t.hour == hh && t.min == mm) c[k++] = R[i].close;
     }
   ArrayResize(c, k);
   return k;
  }

double Rsi(const double &c[], int n, int p)   // Wilder RSI on the series, value at the last element
  {
   double up = 0, dn = 0, a = 1.0 / p;
   for(int i = 1; i < n; i++)
     {
      double d = c[i] - c[i - 1];
      up = (1 - a) * up + a * MathMax(d, 0);
      dn = (1 - a) * dn + a * MathMax(-d, 0);
     }
   if(dn == 0) return 100;
   return 100 - 100 / (1 + up / dn);
  }

double Sma(const double &c[], int n, int p) { double s = 0; for(int i = n - p; i < n; i++) s += c[i]; return s / p; }

bool InPos() { for(int i = PositionsTotal() - 1; i >= 0; i--) if(PositionGetTicket(i) > 0 && PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == Magic) return true; return false; }

void CloseAll() { for(int i = PositionsTotal() - 1; i >= 0; i--) { ulong t = PositionGetTicket(i); if(t > 0 && PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == Magic) trade.PositionClose(t); } }

int OnInit() { trade.SetExpertMagicNumber(Magic); return INIT_SUCCEEDED; }

void OnTick()
  {
   MqlDateTime now; TimeToStruct(TimeCurrent(), now);
   if(now.hour * 100 + now.min < DecideHHMM) return;
   datetime day = TimeCurrent() - (now.hour * 3600 + now.min * 60 + now.sec);
   if(day == lastDay) return;
   // the decision bar must be today's: the M15 bar ending at DecideHHMM has closed
   datetime barEnd = day + (DecideHHMM / 100) * 3600 + (DecideHHMM % 100) * 60;
   if(iTime(_Symbol, PERIOD_M15, 1) + 15 * 60 != barEnd) { if(now.hour * 100 + now.min > DecideHHMM + 30) lastDay = day; return; }
   lastDay = day;
   double c[]; int n = Daily(c);
   if(n < SmaLong + 5) return;
   double close = c[n - 1], r = Rsi(c, n, RsiPeriod);
   bool in = InPos();
   if(in && close > Sma(c, n, SmaExit)) { CloseAll(); return; }
   if(!in && r < RsiLevel && close > Sma(c, n, SmaLong))
     {
      double cs = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE), st = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double lot = MathFloor(AccountInfoDouble(ACCOUNT_EQUITY) * Notional / (ask * cs) / st) * st;
      lot = MathMin(MathMax(lot, SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN)), SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX));
      trade.Buy(lot, _Symbol, 0, 0, 0, "IndexMR");
     }
  }
