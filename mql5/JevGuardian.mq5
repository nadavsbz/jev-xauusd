//+------------------------------------------------------------------+
//| JevGuardian: a separate guard that runs beside a grid robot on the |
//| same account (we have no source of the robots).                    |
//| 1. Equity floor: when equity falls FloorPct below its peak, close  |
//|    every position of the guarded magic and keep closing new ones   |
//|    (kill switch) until a new ResetToken is given by hand.          |
//| 2. Direction block: a NEW position (opened in the last few         |
//|    seconds) against a gold move of MovePct or more over the last   |
//|    MoveMinutes is closed at once.                                  |
//| DryRun=true (default) only logs what it would do; nothing closes.  |
//| No live use without the user's explicit decision.                 |
//+------------------------------------------------------------------+
#property strict
#property description "Equity floor and direction block beside a grid robot. DryRun by default."
#include <Trade/Trade.mqh>

input long   GuardMagic      = -1;      // magic of the guarded robot - REQUIRED (Black Dragon 5555, BTC Bot 90125; 0 = every position on this symbol)
input bool   DryRun          = true;    // true: log only, never close
input double FloorPct        = 15.0;    // equity floor, % below the equity peak (0 = off)
input bool   DirectionBlock  = true;    // close new positions against a strong move
input int    MoveMinutes     = 60;      // look-back of the move
input double MovePct         = 1.0;     // move size that blocks the opposite side, %
input int    NewWithinSec    = 10;      // a position this young counts as "new"
input int    ResetToken      = 0;       // one-time reset: set a NEW number (e.g. today's date) to start fresh after a floor stop;
                                        // a restart with the same number never resets again

CTrade trade;
string gvPeak, gvKill, gvToken, gvFlows;

// sum of balance operations (deposits +, withdrawals -) on this account so far
// false when the history could not be read (review): then nothing is updated, never "flows = 0"
bool BalanceFlows(double &s)
  {
   s = 0;
   if(!HistorySelect(0, TimeCurrent() + 86400)) return false;
   for(int i = HistoryDealsTotal() - 1; i >= 0; i--)
     {
      ulong d = HistoryDealGetTicket(i);
      if(HistoryDealGetInteger(d, DEAL_TYPE) == DEAL_TYPE_BALANCE) s += HistoryDealGetDouble(d, DEAL_PROFIT);
     }
   return true;
  }

int OnInit()
  {
   if(GuardMagic < 0) { Print("JevGuardian: set GuardMagic explicitly (Black Dragon 5555, BTC Bot 90125)"); return(INIT_PARAMETERS_INCORRECT); }
   gvPeak = "JevGuardian.peak." + (string)AccountInfoInteger(ACCOUNT_LOGIN) + "." + (string)GuardMagic;
   gvKill = "JevGuardian.kill." + (string)AccountInfoInteger(ACCOUNT_LOGIN) + "." + (string)GuardMagic;
   gvToken = "JevGuardian.token." + (string)AccountInfoInteger(ACCOUNT_LOGIN) + "." + (string)GuardMagic;
   gvFlows = "JevGuardian.flows." + (string)AccountInfoInteger(ACCOUNT_LOGIN) + "." + (string)GuardMagic;
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   // after a floor stop, deleting only the kill switch is not enough: the old peak would trip the
   // floor again at once. A reset sets both: peak = equity now, kill switch off. It happens once per
   // new ResetToken, so a terminal/VPS restart with unchanged inputs keeps the kill switch on.
   bool fresh = ResetToken != 0 && (!GlobalVariableCheck(gvToken) || (int)GlobalVariableGet(gvToken) != ResetToken);
   // a reset also drops the old flow baseline (review PR #27): it is set again by the next successful scan
   if(fresh) { GlobalVariableSet(gvPeak, eq); GlobalVariableDel(gvKill); GlobalVariableDel(gvFlows); GlobalVariableSet(gvToken, ResetToken);
               Print("JevGuardian reset (new token): peak = equity now, kill switch off"); }
   double f0;
   if((fresh || !GlobalVariableCheck(gvFlows)) && BalanceFlows(f0)) GlobalVariableSet(gvFlows, f0);
   // a deposit made while the guard was not running must move the peak once, by the flow adjustment,
   // before equity is compared with the peak (review)
   if(GlobalVariableCheck(gvPeak) && GlobalVariableCheck(gvFlows)) SyncFlows(true);
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

ulong retry[];   // positions whose close was not confirmed: tried again on every check

void AddRetry(const ulong t) { for(int i = 0; i < ArraySize(retry); i++) if(retry[i] == t) return;
                               int n = ArraySize(retry); ArrayResize(retry, n + 1); retry[n] = t; }

// true only when the server confirmed the close (review: PositionClose()=true is not enough)
bool ClosePos(const ulong ticket, const string why)
  {
   if(DryRun) { PrintFormat("DRY would close #%I64u: %s", ticket, why); return true; }
   bool sent = trade.PositionClose(ticket);
   uint rc = trade.ResultRetcode();
   if(sent && (rc == TRADE_RETCODE_DONE || rc == TRADE_RETCODE_DONE_PARTIAL) && !PositionSelectByTicket(ticket))
     { PrintFormat("closed #%I64u: %s", ticket, why); return true; }
   PrintFormat("close #%I64u not confirmed (%u %s): %s - will retry", ticket, rc, trade.ResultRetcodeDescription(), why);
   AddRetry(ticket);
   return false;
  }

void RetryPending()
  {
   for(int i = ArraySize(retry) - 1; i >= 0; i--)
     {
      ulong t = retry[i];
      bool gone = !PositionSelectByTicket(t) || ClosePos(t, "retry");
      if(gone)
        {
         for(int j = i; j < ArraySize(retry) - 1; j++) retry[j] = retry[j + 1];
         ArrayResize(retry, ArraySize(retry) - 1);
        }
     }
  }

// gold move over the last MoveMinutes, in % (closed M1 bars only)
double MovePctNow()
  {
   double c0 = iClose(_Symbol, PERIOD_M1, 1);
   double cN = iClose(_Symbol, PERIOD_M1, 1 + MoveMinutes);
   if(c0 <= 0 || cN <= 0) return 0;
   return (c0 - cN) / cN * 100.0;
  }

// deposits and withdrawals are not trading results: move the peak by the same amount.
// The history scan runs at most every 30 s, and always right before a floor stop is decided.
double SyncFlows(const bool force)
  {
   static datetime lastScan = 0;
   double peak = GlobalVariableGet(gvPeak);
   if(!force && TimeCurrent() - lastScan < 30) return peak;
   lastScan = TimeCurrent();
   double flows;
   if(!BalanceFlows(flows)) { lastScan = 0; return peak; }      // try again on the next check
   // no baseline yet (the first scan at start failed): set it now WITHOUT moving the peak (review)
   if(!GlobalVariableCheck(gvFlows))
     {
      // first baseline after a failed start scan: a flow may already be inside it, so the peak is reset to
      // the equity now (review) - the floor restarts from here rather than firing on a withdrawal
      double e = AccountInfoDouble(ACCOUNT_EQUITY);
      GlobalVariableSet(gvFlows, flows); GlobalVariableSet(gvPeak, e);
      PrintFormat("flows baseline set late: peak reset to equity %.2f", e);
      return e;
     }
   double seen = GlobalVariableGet(gvFlows);
   if(MathAbs(flows - seen) > 0.005)
     {
      PrintFormat("balance operation %.2f: peak %.2f -> %.2f", flows - seen, peak, peak + flows - seen);
      peak += flows - seen; GlobalVariableSet(gvPeak, peak); GlobalVariableSet(gvFlows, flows);
     }
   return peak;
  }

void CheckFloor()
  {
   double peak = SyncFlows(false);
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   // a new equity high may contain a deposit not scanned yet (review): sync first, so the deposit
   // is counted once (by the flow adjustment), then raise the peak
   if(eq > peak) { peak = SyncFlows(true); if(eq > peak) { GlobalVariableSet(gvPeak, eq); peak = eq; } }
   bool kill = GlobalVariableCheck(gvKill) && GlobalVariableGet(gvKill) > 0;
   if(!kill && !GlobalVariableCheck(gvFlows)) return;            // no flow baseline yet: the floor waits (review)
   if(!kill && FloorPct > 0 && eq <= peak * (1.0 - FloorPct / 100.0)) peak = SyncFlows(true);   // a withdrawal is not a loss
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

void OnTimer() { RetryPending(); CheckFloor(); CheckDirection(); }
void OnTick()  { RetryPending(); CheckFloor(); CheckDirection(); }
//+------------------------------------------------------------------+
