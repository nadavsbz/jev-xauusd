//+------------------------------------------------------------------+
//| JevGuardian: a separate guard that runs beside a grid robot on the |
//| same account (we have no source of the robots).                    |
//| 1. Equity floor: when equity falls FloorPct below its peak, close  |
//|    every position of the guarded magic and keep closing new ones   |
//|    (kill switch) until the global variable is reset by hand.       |
//| 2. Direction block: a NEW position (opened in the last few         |
//|    seconds) against a gold move of MovePct or more over the last   |
//|    MoveMinutes is closed at once.                                  |
//| DryRun=true (default) only logs what it would do; nothing closes.  |
//| No live use without the user's explicit decision.                 |
//+------------------------------------------------------------------+
#property strict
#property description "Equity floor and direction block beside a grid robot. DryRun by default."
#include <Trade/Trade.mqh>

input long   GuardMagic      = 90125;   // magic of the guarded robot (0 = every position on this symbol)
input bool   DryRun          = true;    // true: log only, never close
input double FloorPct        = 15.0;    // equity floor, % below the equity peak (0 = off)
input bool   DirectionBlock  = true;    // close new positions against a strong move
input int    MoveMinutes     = 60;      // look-back of the move
input double MovePct         = 1.0;     // move size that blocks the opposite side, %
input int    NewWithinSec    = 10;      // a position this young counts as "new"
input bool   ResetOnStart    = false;   // true: start fresh (peak = equity now, kill switch off); use after a floor stop

CTrade trade;
string gvPeak, gvKill;

int OnInit()
  {
   gvPeak = "JevGuardian.peak." + (string)AccountInfoInteger(ACCOUNT_LOGIN) + "." + (string)GuardMagic;
   gvKill = "JevGuardian.kill." + (string)AccountInfoInteger(ACCOUNT_LOGIN) + "." + (string)GuardMagic;
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   // after a floor stop, deleting only the kill switch is not enough: the old peak would trip the
   // floor again at once. A reset sets both: peak = equity now, kill switch off.
   if(ResetOnStart) { GlobalVariableSet(gvPeak, eq); GlobalVariableDel(gvKill); Print("JevGuardian reset: peak = equity now, kill switch off"); }
   if(!GlobalVariableCheck(gvPeak) || GlobalVariableGet(gvPeak) < eq) GlobalVariableSet(gvPeak, eq);
   trade.SetAsyncMode(false);
   PrintFormat("JevGuardian start: magic=%I64d dry=%s floor=%.1f%% block=%s %.2f%%/%dmin peak=%.2f",
               GuardMagic, DryRun ? "yes" : "no", FloorPct, DirectionBlock ? "yes" : "no", MovePct, MoveMinutes,
               GlobalVariableGet(gvPeak));
   EventSetTimer(1);
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason) { EventKillTimer(); }

bool Guarded(const ulong ticket)
  {
   if(!PositionSelectByTicket(ticket)) return false;
   if(PositionGetString(POSITION_SYMBOL) != _Symbol) return false;
   return GuardMagic == 0 || PositionGetInteger(POSITION_MAGIC) == GuardMagic;
  }

void ClosePos(const ulong ticket, const string why)
  {
   if(DryRun) { PrintFormat("DRY would close #%I64u: %s", ticket, why); return; }
   if(!trade.PositionClose(ticket))
      PrintFormat("close #%I64u failed (%u %s): %s", ticket, trade.ResultRetcode(), trade.ResultRetcodeDescription(), why);
   else
      PrintFormat("closed #%I64u: %s", ticket, why);
  }

// gold move over the last MoveMinutes, in % (closed M1 bars only)
double MovePctNow()
  {
   double c0 = iClose(_Symbol, PERIOD_M1, 1);
   double cN = iClose(_Symbol, PERIOD_M1, 1 + MoveMinutes);
   if(c0 <= 0 || cN <= 0) return 0;
   return (c0 - cN) / cN * 100.0;
  }

void CheckFloor()
  {
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   double peak = GlobalVariableGet(gvPeak);
   if(eq > peak) { GlobalVariableSet(gvPeak, eq); peak = eq; }
   bool kill = GlobalVariableCheck(gvKill) && GlobalVariableGet(gvKill) > 0;
   if(!kill && FloorPct > 0 && eq <= peak * (1.0 - FloorPct / 100.0))
     {
      PrintFormat("FLOOR hit: equity %.2f <= %.2f (peak %.2f - %.1f%%)", eq, peak * (1.0 - FloorPct / 100.0), peak, FloorPct);
      if(!DryRun) GlobalVariableSet(gvKill, 1);
      kill = true;
     }
   if(!kill) return;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(Guarded(t)) ClosePos(t, "equity floor / kill switch");
     }
  }

void CheckDirection()
  {
   if(!DirectionBlock) return;
   double mv = MovePctNow();
   if(MathAbs(mv) < MovePct) return;
   datetime now = TimeCurrent();
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(!Guarded(t)) continue;
      if(now - (datetime)PositionGetInteger(POSITION_TIME) > NewWithinSec) continue;
      long type = PositionGetInteger(POSITION_TYPE);
      bool against = (type == POSITION_TYPE_BUY && mv <= -MovePct) || (type == POSITION_TYPE_SELL && mv >= MovePct);
      if(against) ClosePos(t, StringFormat("new %s against a %.2f%% move in %d min", type == POSITION_TYPE_BUY ? "BUY" : "SELL", mv, MoveMinutes));
     }
  }

void OnTimer() { CheckFloor(); CheckDirection(); }
void OnTick()  { CheckFloor(); CheckDirection(); }
//+------------------------------------------------------------------+
