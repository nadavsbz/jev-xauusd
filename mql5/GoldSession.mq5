//+------------------------------------------------------------------+
//| GoldSession: test EA for the gold session effect (G3/G4 in        |
//| research/stable/second2.py). Holds one position from StartHour    |
//| (+DelayMin) to EndHour, server time, once a day; flat otherwise.  |
//| Purpose: measure the real-tick fill at the 01:00 reopen, which    |
//| H1 bars hide (bar open = first tick, bar spread = minimum).       |
//+------------------------------------------------------------------+
#property strict
#include <Trade/Trade.mqh>
input int    StartHour = 1;      // server hour to enter
input int    EndHour   = 10;     // server hour to exit
input int    DelayMin  = 0;      // minutes after StartHour before entering
input int    Side      = 1;      // 1 = long, -1 = short
input double Lots      = 1.0;    // fixed size: this EA measures the edge per trade, not sizing
input long   Magic     = 7301;

CTrade tr;
int lastDay = -1;

bool HasPos()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
      if(PositionGetTicket(i) > 0 && PositionGetInteger(POSITION_MAGIC) == Magic && PositionGetString(POSITION_SYMBOL) == _Symbol) return true;
   return false;
}

int OnInit() { tr.SetExpertMagicNumber(Magic); return INIT_SUCCEEDED; }

void OnTick()
{
   MqlDateTime t; TimeToStruct(TimeCurrent(), t);
   int m = t.hour * 60 + t.min;
   bool inside = m >= StartHour * 60 + DelayMin && t.hour < EndHour;
   if(HasPos())
   {
      if(!inside) tr.PositionClose(_Symbol);
      return;
   }
   if(inside && t.day_of_year != lastDay)
   {
      // the first ticks at the reopen come while the session is still closed ("Market closed"): retry on every tick
      bool ok = Side > 0 ? tr.Buy(Lots, _Symbol) : tr.Sell(Lots, _Symbol);
      if(ok && tr.ResultRetcode() == TRADE_RETCODE_DONE) lastDay = t.day_of_year;
   }
}
