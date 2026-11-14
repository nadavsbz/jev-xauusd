//+------------------------------------------------------------------+
//| HappyClone: a reimplementation of EA Happy Gold from its public   |
//| description only (happyforex.de, MQL5 signals; no source, no ex). |
//| docs/HAPPY_CLONE_PLAN.md. On the closed bars of the chart:        |
//| a percent ZigZag (a swing needs ZZPct % of price); a Buy Stop at  |
//| the last swing high + Distance and a Sell Stop at the last swing  |
//| low - Distance, refreshed on every new bar; one position at a     |
//| time (the other pending is deleted when one fills); hard SL,      |
//| fixed TP, break-even and trailing; trading hours; spread filter.  |
//| Lots: Risk % of equity lost at the SL, or FixLot when Risk = 0.   |
//| Mode 1 (news straddle, the GridNews/2-minute-hold hypothesis):    |
//| NewsBefore min before each event of NewsFile (Common\Files, one  |
//| unix server time per line) a Buy Stop at Ask + Distance and a     |
//| Sell Stop at Bid - Distance; unfilled ones are deleted NewsAfter  |
//| min after the event. MaxHoldMin closes a position after N min.    |
//+------------------------------------------------------------------+
#property strict
#include <Trade/Trade.mqh>
input double ZZPct      = 0.3;    // ZigZag: minimum swing, % of price
input int    ZZBars     = 500;    // closed bars scanned for the swings
input int    Distance   = 50;     // pending order beyond the swing, points
input int    SL         = 240;    // hard stop loss, points (the vendor's "-24 pips")
input int    TP         = 600;    // take profit, points (0 = none)
input int    BEStart    = 0;      // move the SL to entry + BEPoint after this profit, points (0 = off)
input int    BEPoint    = 10;
input int    TrailStart = 100;    // trailing starts after this profit, points (0 = off)
input int    TrailDist  = 50;     // trailing distance, points
input int    StartHour  = 1;      // server hours when new pendings may be placed [StartHour, EndHour)
input int    EndHour    = 23;
input int    MaxSpread  = 60;     // no new pendings above this spread, points
input double Risk       = 1.0;    // % of equity lost at the SL; 0 = FixLot
input double FixLot     = 0.01;
input long   Magic      = 8801;
input int    Mode       = 0;      // 0 = ZigZag swings, 1 = news straddle
input string NewsFile   = "news_high_rf.txt";
input int    NewsBefore = 2;      // minutes before the event the straddle is placed
input int    NewsAfter  = 5;      // minutes after the event unfilled pendings are deleted
input int    MaxHoldMin = 0;      // close a position after this many minutes (0 = off)

CTrade tr;
datetime lastBar = 0, placedFor = 0;
long nw[]; int nwN = 0, nwI = 0;

int LoadNews()
{
   int h = FileOpen(NewsFile, FILE_READ | FILE_TXT | FILE_COMMON | FILE_ANSI);
   if(h == INVALID_HANDLE) return 0;
   while(!FileIsEnding(h)) { string l = FileReadString(h); if(StringLen(l) < 5) continue; ArrayResize(nw, nwN + 1); nw[nwN++] = StringToInteger(l); }
   FileClose(h); ArraySort(nw); return nwN;
}

void NewsTick()
{
   datetime now = TimeCurrent();
   while(nwI < nwN && nw[nwI] + NewsAfter * 60 < now) nwI++;
   if(nwI >= nwN) return;
   datetime ev = (datetime)nw[nwI];
   if(now >= ev + NewsAfter * 60) return;
   if(now >= ev - NewsBefore * 60 && placedFor != ev)
   {
      placedFor = ev; DeletePendings();
      if(SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) > MaxSpread) return;
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), v = LotsFor();
      double bp = NormalizeDouble(ask + Distance * _Point, _Digits), sp = NormalizeDouble(bid - Distance * _Point, _Digits);
      tr.BuyStop(v, bp, _Symbol, NormalizeDouble(bp - SL * _Point, _Digits), TP > 0 ? NormalizeDouble(bp + TP * _Point, _Digits) : 0);
      tr.SellStop(v, sp, _Symbol, NormalizeDouble(sp + SL * _Point, _Digits), TP > 0 ? NormalizeDouble(sp - TP * _Point, _Digits) : 0);
   }
}

// last confirmed swing high and low of a percent ZigZag on closed bars 1..ZZBars
bool Swings(double &hi, double &lo)
{
   MqlRates r[]; ArraySetAsSeries(r, false);
   int n = CopyRates(_Symbol, _Period, 1, ZZBars, r);
   if(n < 50) return false;
   int dir = 0; double ext = r[0].close; hi = 0; lo = 0;
   double eH = r[0].high, eL = r[0].low;
   for(int i = 1; i < n; i++)
   {
      if(dir >= 0)                                  // looking for a top (or undecided)
      {
         if(r[i].high > eH) eH = r[i].high;
         if(r[i].low < eH * (1 - ZZPct / 100)) { hi = eH; dir = -1; eL = r[i].low; continue; }
      }
      if(dir <= 0)                                  // looking for a bottom (or undecided)
      {
         if(r[i].low < eL) eL = r[i].low;
         if(r[i].high > eL * (1 + ZZPct / 100)) { lo = eL; dir = 1; eH = r[i].high; }
      }
   }
   return hi > 0 && lo > 0;
}

int Positions()
{
   int k = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
      if(PositionGetSymbol(i) == _Symbol && PositionGetInteger(POSITION_MAGIC) == Magic) k++;
   return k;
}

void DeletePendings()
{
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
      ulong t = OrderGetTicket(i);
      if(OrderGetString(ORDER_SYMBOL) == _Symbol && OrderGetInteger(ORDER_MAGIC) == Magic) tr.OrderDelete(t);
   }
}

double LotsFor()
{
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP), mn = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), mx = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double v = FixLot;
   if(Risk > 0)
   {
      double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
      double lossPerLot = SL * _Point / ts * tv;
      if(lossPerLot > 0) v = AccountInfoDouble(ACCOUNT_EQUITY) * Risk / 100 / lossPerLot;
   }
   v = MathFloor(v / step) * step;
   return MathMax(mn, MathMin(mx, v));
}

void Manage()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(PositionGetSymbol(i) != _Symbol || PositionGetInteger(POSITION_MAGIC) != Magic) continue;
      ulong t = PositionGetInteger(POSITION_TICKET);
      bool buy = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY;
      double op = PositionGetDouble(POSITION_PRICE_OPEN), sl = PositionGetDouble(POSITION_SL), tp = PositionGetDouble(POSITION_TP);
      double px = buy ? SymbolInfoDouble(_Symbol, SYMBOL_BID) : SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double prof = (buy ? px - op : op - px) / _Point, nsl = sl;
      if(BEStart > 0 && prof >= BEStart)
      {
         double be = buy ? op + BEPoint * _Point : op - BEPoint * _Point;
         if(buy ? be > nsl : (nsl == 0 || be < nsl)) nsl = be;
      }
      if(TrailStart > 0 && prof >= TrailStart)
      {
         double ts = buy ? px - TrailDist * _Point : px + TrailDist * _Point;
         if(buy ? ts > nsl : (nsl == 0 || ts < nsl)) nsl = ts;
      }
      nsl = NormalizeDouble(nsl, _Digits);
      if(MathAbs(nsl - sl) >= _Point) tr.PositionModify(t, nsl, tp);
   }
}

void HoldExit()
{
   if(MaxHoldMin <= 0) return;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
      if(PositionGetSymbol(i) == _Symbol && PositionGetInteger(POSITION_MAGIC) == Magic
         && TimeCurrent() - (datetime)PositionGetInteger(POSITION_TIME) >= MaxHoldMin * 60) tr.PositionClose(PositionGetInteger(POSITION_TICKET));
}

void OnTick()
{
   if(Positions() > 0) { DeletePendings(); Manage(); HoldExit(); return; }
   if(Mode == 1) { NewsTick(); return; }
   datetime b = iTime(_Symbol, _Period, 0);
   if(b == lastBar) return;
   lastBar = b;
   DeletePendings();
   MqlDateTime dt; TimeToStruct(TimeCurrent(), dt);
   if(dt.hour < StartHour || dt.hour >= EndHour) return;
   if(SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) > MaxSpread) return;
   double hi, lo;
   if(!Swings(hi, lo)) return;
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double gap = (SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) + 5) * _Point, v = LotsFor();
   double bp = NormalizeDouble(hi + Distance * _Point, _Digits), sp = NormalizeDouble(lo - Distance * _Point, _Digits);
   if(bp > ask + gap)
      tr.BuyStop(v, bp, _Symbol, NormalizeDouble(bp - SL * _Point, _Digits), TP > 0 ? NormalizeDouble(bp + TP * _Point, _Digits) : 0);
   if(sp < bid - gap)
      tr.SellStop(v, sp, _Symbol, NormalizeDouble(sp + SL * _Point, _Digits), TP > 0 ? NormalizeDouble(sp - TP * _Point, _Digits) : 0);
}

int OnInit()
{
   tr.SetExpertMagicNumber(Magic);
   if(Mode == 1 && LoadNews() <= 0) { Print("HappyClone: no news events loaded from ", NewsFile); return INIT_PARAMETERS_INCORRECT; }
   return INIT_SUCCEEDED;
}
