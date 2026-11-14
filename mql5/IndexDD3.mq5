//+------------------------------------------------------------------+
//| IndexDD3: "3 days down" close-to-close long on an index CFD        |
//| (Grok t199u US500_3DD; pre-registered docs/THIRD_COMPONENT_PLAN.md |
//|  12.11.2026, rules frozen before the tester run)                  |
//| Once a day at DecideHHMM (server time) the close of the M1 bar    |
//| that just closed is the day's "close". On that daily series:      |
//|   signal = C[d] < C[d-1] < C[d-2] < C[d-3]  (Streak down closes)   |
//|   flat & signal -> buy;  long & !signal -> close; else hold       |
//| Size: notional = equity x Notional (no stop, no TP, one position). |
//| Server = New York + 7h: 15:58 NY = 22:58 server.                  |
//| Half days (13:00 NY close): no 22:58 bar -> no decision that day.  |
//+------------------------------------------------------------------+
#property strict
#include <Trade\Trade.mqh>

input int    DecideHHMM = 2258;   // server time of the daily decision (the M1 bar ending then is the day's close)
input int    Streak     = 3;      // number of consecutive lower closes
input double Notional   = 1.0;    // position notional as a multiple of equity
input long   Magic      = 7402;

CTrade trade;
datetime lastDay = 0;

int Daily(double &c[])   // closes of the M1 bar ending at DecideHHMM, one per day, oldest first (last ~15 days)
  {
   MqlRates R[]; int n = CopyRates(_Symbol, PERIOD_M1, 1, 1440 * 15, R);
   if(n <= 0) return 0;
   int hh = DecideHHMM / 100, mm = DecideHHMM % 100, k = 0;
   ArrayResize(c, n);
   for(int i = 0; i < n; i++)
     {
      MqlDateTime t; TimeToStruct(R[i].time + 60, t);   // bar end time
      if(t.hour == hh && t.min == mm) c[k++] = R[i].close;
     }
   ArrayResize(c, k);
   return k;
  }

bool InPos() { for(int i = PositionsTotal() - 1; i >= 0; i--) if(PositionGetTicket(i) > 0 && PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == Magic) return true; return false; }

void CloseAll() { for(int i = PositionsTotal() - 1; i >= 0; i--) { ulong t = PositionGetTicket(i); if(t > 0 && PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == Magic) trade.PositionClose(t); } }

int OnInit() { trade.SetExpertMagicNumber(Magic); return INIT_SUCCEEDED; }

void OnTick()
  {
   MqlDateTime now; TimeToStruct(TimeCurrent(), now);
   if(now.hour * 100 + now.min < DecideHHMM) return;
   datetime day = TimeCurrent() - (now.hour * 3600 + now.min * 60 + now.sec);
   if(day == lastDay) return;
   // the decision bar must be today's: the M1 bar ending at DecideHHMM has closed
   datetime barEnd = day + (DecideHHMM / 100) * 3600 + (DecideHHMM % 100) * 60;
   if(iTime(_Symbol, PERIOD_M1, 1) + 60 != barEnd) { if(TimeCurrent() > barEnd + 120) lastDay = day; return; }
   lastDay = day;
   double c[]; int n = Daily(c);
   if(n < Streak + 1) return;
   bool sig = true;
   for(int j = 0; j < Streak; j++) if(!(c[n - 1 - j] < c[n - 2 - j])) { sig = false; break; }
   bool in = InPos();
   if(in && !sig) { CloseAll(); return; }
   if(!in && sig)
     {
      double st = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP), ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
      double lot = MathFloor(AccountInfoDouble(ACCOUNT_EQUITY) * Notional / (ask / ts * tv) / st) * st;
      lot = MathMin(MathMax(lot, SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN)), SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX));
      trade.Buy(lot, _Symbol, 0, 0, 0, "IndexDD3");
     }
  }
