//+------------------------------------------------------------------+
//| GoldAsia: round 7 S1 of docs/SCAN_PLAN.md (pre-registered 11.11). |
//| Long XAUUSD from the open of server bar EntryHour (01) to the    |
//| close of bar LastHour (09), every weekday; flat otherwise, so no |
//| swap. Sizing (TargetVol > 0): as scan.scale - the rule's own     |
//| daily return per 1x notional from the bars, its std over the     |
//| last 90 days (60 at least) x sqrt(260), lev = min(5, TV / vol),  |
//| lots = lev x equity / (open x contract). TargetVol = 0 -> Lots.  |
//| Restart safety: never enters later than EntryWindow minutes into |
//| the entry bar (the 9.11 demo restart entered mid-bar in I2).     |
//+------------------------------------------------------------------+
#property strict
#include <Trade/Trade.mqh>
input int    EntryHour   = 1;      // server hour; buy at the open of this bar (after the 00:00 rollover)
input int    LastHour    = 9;      // flat at the close of this bar (before London)
input int    EntryWindow = 20;     // minutes after the entry bar opens in which an entry is still allowed
input double Lots        = 1.0;    // used when TargetVol = 0
input double TargetVol   = 0.10;   // annual vol target of the rule (0.10 = the sim)
input double CostPct     = 0.01;   // per round trip, % of notional, in the sizing returns (as the sim: 2 x 0.005%)
input double MaxLev      = 5.0;
input long   Magic       = 7401;

CTrade tr;
MqlRates R[]; int N = 0;
datetime enteredDay = 0;

datetime Day(datetime t) { return t - t % 86400; }

int Bar(datetime d, int k)
{
   datetime t = d + k * 3600;
   int lo = 0, hi = N - 1;
   while(lo <= hi) { int m = (lo + hi) / 2; if(R[m].time == t) return m; if(R[m].time < t) lo = m + 1; else hi = m - 1; }
   return -1;
}

double SizeFor(datetime d, double px)
{
   if(TargetVol <= 0) return Lots;
   N = CopyRates(_Symbol, PERIOD_H1, 1, 24 * 200, R);
   if(N < 24 * 60) return 0;
   double x[]; int m = 0; ArrayResize(x, 90);
   for(datetime e = d - 86400; e > d - 86400 * 200 && m < 90; e -= 86400)
   {
      int a = Bar(e, EntryHour), b = Bar(e, LastHour);
      if(a < 0 || b < 0) continue;                          // weekend or a missing bar, as the sim skips the day
      x[m++] = R[b].close / R[a].open - 1 - CostPct / 100;
   }
   if(m < 60) return 0;
   double mu = 0, v = 0; for(int i = 0; i < m; i++) mu += x[i]; mu /= m;
   for(int i = 0; i < m; i++) v += (x[i] - mu) * (x[i] - mu);
   double vol = MathSqrt(v / (m - 1)) * MathSqrt(260); if(vol <= 0) return 0;
   double lev = MathMin(MaxLev, TargetVol / vol);
   double cs = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE), st = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double lots = MathFloor(lev * AccountInfoDouble(ACCOUNT_EQUITY) / (px * cs) / st) * st;
   return MathMin(lots, SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX));
}

bool Has()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
      if(PositionGetTicket(i) > 0 && PositionGetInteger(POSITION_MAGIC) == Magic && PositionGetString(POSITION_SYMBOL) == _Symbol) return true;
   return false;
}

void Flat()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t > 0 && PositionGetInteger(POSITION_MAGIC) == Magic && PositionGetString(POSITION_SYMBOL) == _Symbol) tr.PositionClose(t);
   }
}

int OnInit() { tr.SetExpertMagicNumber(Magic); return INIT_SUCCEEDED; }

void OnTick()
{
   datetime now = TimeCurrent(); MqlDateTime t; TimeToStruct(now, t);
   bool inside = t.hour >= EntryHour && t.hour <= LastHour;
   if(!inside) { if(Has()) Flat(); return; }                 // the exit: first tick after the close of LastHour (or any stray)
   datetime d = Day(now);
   if(enteredDay == d || Has()) return;
   if(t.hour != EntryHour || t.min >= EntryWindow) return;  // late (e.g. a restart): skip the day, never enter mid-session
   if(t.day_of_week == 0 || t.day_of_week == 6) return;
   double px = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double lots = SizeFor(d, px);
   enteredDay = d;                                           // one attempt per day; a failed order is not chased later
   if(lots < SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN)) return;
   tr.Buy(lots, _Symbol);
}
