//+------------------------------------------------------------------+
//| BDPartialGuard: runs NEXT TO EA Black Dragon on the same account  |
//| (its own chart, same symbol). It never opens trades.              |
//| Rule (docs/BD_V5_PLAN.md, tested as DragonClone_v5b):             |
//|  - per side, the BD basket = all positions with BD's magic.       |
//|  - when the basket loss reaches P_At % of BALANCE, close the      |
//|    oldest positions until P_Frac of the side's volume is closed.  |
//|    Once per basket; re-armed when the side is empty.              |
//|  - optional backstop: close the whole side at G_StopPctEquity %   |
//|    of equity (the tester used 20, like the live guard).           |
//| Same logic as DragonClone_v5b (LossPct, CloseOldest) so the       |
//| tester result applies. Demo first; live only by the user.         |
//+------------------------------------------------------------------+
#property strict
#include <Trade/Trade.mqh>

input long   BD_Magic = 5555;          // magic of the BD positions to watch
input double P_At = 10;                // partial cut at this basket loss, % of balance (0 = off)
input double P_Frac = 0.3;             // share of the side's volume to close (oldest first)
input double G_StopPctEquity = 20;     // backstop: close the side at this loss, % of equity (0 = off)
input bool   DryRun = false;           // true = only log what it would close
input int    TimerMs = 250;            // check interval (also checked on every tick)

CTrade trade;
bool pDone[2];

int OnInit()
  {
   if(AccountInfoInteger(ACCOUNT_MARGIN_MODE) != ACCOUNT_MARGIN_MODE_RETAIL_HEDGING) { Print("BDPartialGuard needs a hedging account"); return INIT_FAILED; }
   trade.SetExpertMagicNumber(0);       // its own closes carry no magic, like the live guard
   pDone[0] = pDone[1] = false;
   EventSetMillisecondTimer(TimerMs);
   PrintFormat("BDPartialGuard on %s: magic %I64d, partial %.1f%% -> %.0f%% of volume, backstop %.1f%%, dry run %s",
               _Symbol, BD_Magic, P_At, P_Frac * 100, G_StopPctEquity, DryRun ? "yes" : "no");
   return INIT_SUCCEEDED;
  }

void OnDeinit(const int reason) { EventKillTimer(); }

struct Side { int n; double vol; double profit; };

void Scan(int side, Side &s)
  {
   s.n = 0; s.vol = 0; s.profit = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(!PositionSelectByTicket(t) || PositionGetInteger(POSITION_MAGIC) != BD_Magic || PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if((PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 0 : 1) != side) continue;
      s.n++; s.vol += PositionGetDouble(POSITION_VOLUME); s.profit += PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
     }
  }

double LossPct(Side &s) { return s.profit < 0 ? -s.profit / AccountInfoDouble(ACCOUNT_BALANCE) * 100 : 0; }

bool CloseTicket(ulong t, string why)
  {
   if(DryRun) { PrintFormat("DRY %s: would close #%I64u", why, t); return true; }
   bool ok = trade.PositionClose(t) && trade.ResultRetcode() == TRADE_RETCODE_DONE;
   PrintFormat("%s: close #%I64u -> %s (%u)", why, t, ok ? "done" : "FAILED", trade.ResultRetcode());
   return ok;
  }

void CloseOldest(int side, double volTarget)   // oldest first, until volTarget lots are closed
  {
   double done = 0; ulong skip[]; int ns = 0;
   while(done < volTarget - 1e-9)
     {
      ulong best = 0; datetime bt = D'2100.01.01'; double bv = 0;
      for(int i = PositionsTotal() - 1; i >= 0; i--)
        {
         ulong t = PositionGetTicket(i);
         if(!PositionSelectByTicket(t) || PositionGetInteger(POSITION_MAGIC) != BD_Magic || PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
         if((PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 0 : 1) != side) continue;
         bool skipped = false; for(int k = 0; k < ns; k++) if(skip[k] == t) skipped = true;
         datetime ot = (datetime)PositionGetInteger(POSITION_TIME);
         if(!skipped && ot < bt) { bt = ot; best = t; bv = PositionGetDouble(POSITION_VOLUME); }
        }
      if(best == 0) break;
      if(!CloseTicket(best, "partial cut")) break;
      done += bv;
      if(DryRun) { ArrayResize(skip, ns + 1); skip[ns++] = best; }   // in a dry run nothing closes: walk on
     }
  }

void CloseSide(int side)
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(!PositionSelectByTicket(t) || PositionGetInteger(POSITION_MAGIC) != BD_Magic || PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if((PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 0 : 1) == side) CloseTicket(t, "backstop");
     }
  }

void Check()
  {
   for(int side = 0; side < 2; side++)
     {
      Side s; Scan(side, s);
      if(s.n == 0) { pDone[side] = false; continue; }
      if(G_StopPctEquity > 0 && s.profit < -G_StopPctEquity / 100 * AccountInfoDouble(ACCOUNT_EQUITY))
        { PrintFormat("backstop: side %d loss %.2f", side, s.profit); CloseSide(side); continue; }
      if(P_At > 0 && !pDone[side] && LossPct(s) >= P_At)
        {
         PrintFormat("partial cut: side %d loss %.2f%% of balance, closing %.2f of %.2f lots", side, LossPct(s), P_Frac * s.vol, s.vol);
         pDone[side] = true; CloseOldest(side, P_Frac * s.vol);
        }
     }
  }

void OnTick()  { Check(); }
void OnTimer() { Check(); }
