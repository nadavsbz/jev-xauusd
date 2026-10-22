//+------------------------------------------------------------------+
//| SemiTrend: the developer's semi-manual "trade with the trend"     |
//| method (guides for Trend AI / Trend Catcher + EA Black Dragon),   |
//| automated for the tester only (docs/SEMI_TREND_PLAN.md).          |
//| Entry: H4 trend (indicator direction + close vs SMA200) agrees     |
//| with a fresh M15 signal (indicator flip + close vs SMA200).        |
//| Then a Black Dragon style martingale grid with the semi-manual set |
//| (distance $3, TP $1 over the average, x1.5, max 10, max lot 5),    |
//| cut everything when the M15 signal flips against the cycle.        |
//+------------------------------------------------------------------+
#property strict
#property tester_indicator "Trend AI.ex5"
#property tester_indicator "Trend Catcher.ex5"
#include <Trade\Trade.mqh>

input string Ind        = "Trend Catcher"; // direction indicator (buffer 7 = +1 up / -1 down)
input int    DirBuffer  = 7;
input int    EntryMode  = 0;     // 0 = only on a fresh M15 flip, 1 = any M15 bar that agrees
input bool   UseH4      = true;  // H4 regime filter
input bool   CutOnFlip  = true;  // close the cycle when the M15 direction turns against it
input double Lot        = 0.01;
input double Martin     = 1.5;
input double MaxLot     = 5.0;
input int    MaxOrders  = 10;
input double Dist       = 3.0;   // $ between levels (300 points on 2 digits)
input int    DynFrom    = 6;     // from this level the distance grows
input double DynMult    = 1.2;
input double TP         = 1.0;   // $ over the average price (100 points on 2 digits)
input long   Magic      = 77001;

CTrade trade;
int hM15 = INVALID_HANDLE, hH4 = INVALID_HANDLE, maM15 = INVALID_HANDLE, maH4 = INVALID_HANDLE;
datetime lastBar = 0;

int OnInit()
  {
   hM15 = iCustom(_Symbol, PERIOD_M15, Ind);
   hH4  = iCustom(_Symbol, PERIOD_H4, Ind);
   maM15 = iMA(_Symbol, PERIOD_M15, 200, 0, MODE_SMA, PRICE_CLOSE);
   maH4  = iMA(_Symbol, PERIOD_H4, 200, 0, MODE_SMA, PRICE_CLOSE);
   if(hM15 == INVALID_HANDLE || hH4 == INVALID_HANDLE || maM15 == INVALID_HANDLE || maH4 == INVALID_HANDLE)
      return INIT_FAILED;
   trade.SetExpertMagicNumber(Magic);
   return INIT_SUCCEEDED;
  }

double Buf(int h, int b, int shift)
  {
   double v[1];
   if(CopyBuffer(h, b, shift, 1, v) != 1) return 0;
   return v[0];
  }

int Dir(int h, int shift) { double v = Buf(h, DirBuffer, shift); return v > 0.5 ? 1 : (v < -0.5 ? -1 : 0); }

double LotN(int n)
  {
   double l = MathMax(0.01, NormalizeDouble(Lot * MathPow(Martin, n), 2));
   return MathMin(l, MaxLot);
  }

double DistN(int n) { return n < DynFrom ? Dist : Dist * MathPow(DynMult, n - DynFrom + 1); }

// open cycle state: side, count, average, last entry price
int Cycle(double &avg, double &last, int &n)
  {
   int side = 0; double vol = 0, pv = 0; n = 0; last = 0; datetime lt = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(!PositionSelectByTicket(t) || PositionGetInteger(POSITION_MAGIC) != Magic) continue;
      side = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 1 : -1;
      double v = PositionGetDouble(POSITION_VOLUME), p = PositionGetDouble(POSITION_PRICE_OPEN);
      vol += v; pv += v * p; n++;
      datetime ot = (datetime)PositionGetInteger(POSITION_TIME);
      if(ot >= lt) { lt = ot; last = p; }
     }
   avg = vol > 0 ? pv / vol : 0;
   return side;
  }

void CloseAll()
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(PositionSelectByTicket(t) && PositionGetInteger(POSITION_MAGIC) == Magic) trade.PositionClose(t);
     }
  }

void OnTick()
  {
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double avg, last; int n;
   int side = Cycle(avg, last, n);
   // manage the grid on every tick
   if(side == 1)
     {
      if(bid >= avg + TP) { CloseAll(); return; }
      if(n < MaxOrders && ask <= last - DistN(n)) trade.Buy(LotN(n), _Symbol);
     }
   else if(side == -1)
     {
      if(ask <= avg - TP) { CloseAll(); return; }
      if(n < MaxOrders && bid >= last + DistN(n)) trade.Sell(LotN(n), _Symbol);
     }
   // signals on a new M15 bar, closed-bar values only
   datetime b = iTime(_Symbol, PERIOD_M15, 0);
   if(b == lastBar) return;
   lastBar = b;
   int d1 = Dir(hM15, 1), d2 = Dir(hM15, 2);
   if(side != 0)
     {
      if(CutOnFlip && d1 == -side) CloseAll();
      return;
     }
   double c15 = iClose(_Symbol, PERIOD_M15, 1), m15 = Buf(maM15, 0, 1);
   int regime = d1;
   if(UseH4)
     {
      int h4 = Dir(hH4, 1); double c4 = iClose(_Symbol, PERIOD_H4, 1), m4 = Buf(maH4, 0, 1);
      int bb4 = c4 > m4 ? 1 : (c4 < m4 ? -1 : 0);
      if(h4 == 0 || h4 != bb4) return;
      regime = h4;
     }
   if(d1 != regime) return;
   if(EntryMode == 0 && d2 == regime) return;                  // wait for a fresh flip ("a new dot")
   int bb15 = c15 > m15 ? 1 : (c15 < m15 ? -1 : 0);
   if(bb15 != regime) return;                                  // above / below the middle band
   if(regime == 1) trade.Buy(LotN(0), _Symbol); else trade.Sell(LotN(0), _Symbol);
  }
