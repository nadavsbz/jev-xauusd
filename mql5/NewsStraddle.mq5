//+------------------------------------------------------------------+
//| NewsStraddle: round 44a forward test (docs/SCAN_PLAN.md, round   |
//| 45 pre-registration). DEMO ONLY - refuses a real account.         |
//| Before each pre-registered high-impact USD release it places a    |
//| buy-stop and a sell-stop Dist pips around the mid PlaceSec seconds|
//| before the release on each symbol, deletes the other side on      |
//| fill, cancels unfilled orders at T+CancelSec, SL 18 / TP 100,     |
//| lock-and-trail after +3 pips, force close at T+CloseSec.          |
//| Goal: measure REAL fills (slippage vs the stop price) on RF ECN,  |
//| which the tester cannot model. Every trade -> MQL5\Files CSV.     |
//| Calendar times are trade-server time (same clock as TimeTradeServer).
//+------------------------------------------------------------------+
#property strict
#include <Trade/Trade.mqh>

input string Symbols   = "EURUSD,USDJPY,AUDUSD,GBPUSD";
input double RiskPct   = 1.0;     // % of equity lost at the stop
input double Dist      = 10;      // pips from the mid
input double SLPips    = 18;
input double TPPips    = 100;
input double LockPips  = 3;
input double TrailPips = 3;
input int    PlaceSec  = 2;       // seconds before the release
input int    CancelSec = 60;
input int    CloseSec  = 900;
input long   Magic     = 440045;
input string LogName   = "news_live.csv";

string FAM[] = {"Nonfarm Payrolls", "CPI m/m", "Core CPI m/m", "Initial Jobless Claims", "PPI m/m", "Retail Sales m/m",
                "ISM Manufacturing PMI", "ISM Non-Manufacturing PMI", "JOLTS Job Openings", "Fed Interest Rate Decision", "GDP q/q",
                "Core PCE Price Index m/m", "ADP Nonfarm Employment Change", "Durable Goods Orders m/m"};

struct Slot
{
   string   sym;
   datetime T;
   string   names;
   double   mid, bstop, sstop;
   ulong    bt, st;          // pending tickets
   ulong    pos;             // position ticket
   int      dir;
   double   trig, fill, peak, slnow, spreadAtFill;
   long     fillMsc, placeMsc;
   bool     placed, filled, armed, done;
};

CTrade tr;
string syms[];
Slot   slots[];
datetime evT[]; string evN[];
datetime lastLoad = 0;

double Pip(string s) { int d = (int)SymbolInfoInteger(s, SYMBOL_DIGITS); double p = SymbolInfoDouble(s, SYMBOL_POINT); return (d == 3 || d == 5) ? p * 10 : p; }

bool IsFam(string n) { for(int i = 0; i < ArraySize(FAM); i++) if(n == FAM[i]) return true; return false; }

void LoadCalendar()
{
   MqlCalendarValue v[];
   datetime now = TimeTradeServer();
   int n = CalendarValueHistory(v, now - 600, now + 86400 * 3, NULL, "USD");
   if(n <= 0) { PrintFormat("calendar not ready (%d) err %d", n, GetLastError()); return; }
   ArrayResize(evT, 0); ArrayResize(evN, 0);
   for(int i = 0; i < n; i++)
   {
      MqlCalendarEvent e;
      if(!CalendarEventById(v[i].event_id, e)) continue;
      if(e.importance != CALENDAR_IMPORTANCE_HIGH || !IsFam(e.name)) continue;
      int k = -1;
      for(int j = 0; j < ArraySize(evT); j++) if(evT[j] == v[i].time) k = j;
      if(k < 0) { k = ArraySize(evT); ArrayResize(evT, k + 1); ArrayResize(evN, k + 1); evT[k] = v[i].time; evN[k] = e.name; }
      else if(StringFind(evN[k], e.name) < 0) evN[k] += "|" + e.name;
   }
   lastLoad = now;
   string s = "";
   for(int j = 0; j < ArraySize(evT); j++) s += TimeToString(evT[j], TIME_DATE | TIME_SECONDS) + " " + evN[j] + "; ";
   PrintFormat("calendar: %d upcoming releases (server time): %s", ArraySize(evT), s);
}

bool HaveSlot(string sym, datetime T) { for(int i = 0; i < ArraySize(slots); i++) if(slots[i].sym == sym && slots[i].T == T) return true; return false; }

void Log(Slot &z, string reason, double exitPx, long exitMsc, double profit)
{
   double pip = Pip(z.sym);
   double gross = z.filled ? z.dir * (exitPx - z.fill) / pip : 0;
   int f = FileOpen(LogName, FILE_READ | FILE_WRITE | FILE_CSV | FILE_ANSI | FILE_SHARE_READ, ',');
   if(f == INVALID_HANDLE) { Print("log open failed ", GetLastError()); return; }
   if(FileSize(f) == 0)
      FileWrite(f, "T_srv", "names", "sym", "place_msc", "mid", "bstop", "sstop", "dir", "trigger", "fill", "fill_msc", "slip_pips",
                "spread_pips_at_fill", "exit", "exit_msc", "reason", "gross_pips", "profit_usd");
   FileSeek(f, 0, SEEK_END);
   FileWrite(f, TimeToString(z.T, TIME_DATE | TIME_SECONDS), z.names, z.sym, z.placeMsc, DoubleToString(z.mid, 6), DoubleToString(z.bstop, 6),
             DoubleToString(z.sstop, 6), z.dir, DoubleToString(z.trig, 6), DoubleToString(z.fill, 6), z.fillMsc,
             DoubleToString(z.filled ? z.dir * (z.fill - z.trig) / pip : 0, 2), DoubleToString(z.spreadAtFill, 2),
             DoubleToString(exitPx, 6), exitMsc, reason, DoubleToString(gross, 2), DoubleToString(profit, 2));
   FileClose(f);
}

double LotsFor(string s)
{
   double tv = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_VALUE), ts = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_SIZE);
   if(tv <= 0 || ts <= 0) return 0;
   double perLot = SLPips * Pip(s) / ts * tv;
   double lots = AccountInfoDouble(ACCOUNT_EQUITY) * RiskPct / 100 / perLot;
   double step = SymbolInfoDouble(s, SYMBOL_VOLUME_STEP), mn = SymbolInfoDouble(s, SYMBOL_VOLUME_MIN), mx = SymbolInfoDouble(s, SYMBOL_VOLUME_MAX);
   lots = MathFloor(lots / step) * step;
   return MathMax(mn, MathMin(mx, lots));
}

void Place(int k)
{
   for(int i = 0; i < ArraySize(syms); i++)
   {
      string s = syms[i];
      if(HaveSlot(s, evT[k])) continue;
      MqlTick t;
      if(!SymbolInfoTick(s, t)) continue;
      int n = ArraySize(slots); ArrayResize(slots, n + 1);
      Slot z; ZeroMemory(z);
      z.sym = s; z.T = evT[k]; z.names = evN[k];
      slots[n] = z;
      if(TimeTradeServer() - t.time > 120) { slots[n].done = true; PrintFormat("%s: no fresh tick, skip", s); continue; }   // market closed
      double pip = Pip(s); int dg = (int)SymbolInfoInteger(s, SYMBOL_DIGITS);
      double M = (t.bid + t.ask) / 2, B = NormalizeDouble(M + Dist * pip, dg), S = NormalizeDouble(M - Dist * pip, dg);
      double lots = LotsFor(s);
      slots[n].mid = M; slots[n].bstop = B; slots[n].sstop = S; slots[n].placeMsc = (long)t.time_msc;
      tr.SetTypeFillingBySymbol(s);
      string c = "N" + IntegerToString((long)evT[k]);
      if(tr.BuyStop(lots, B, s, NormalizeDouble(B - SLPips * pip, dg), NormalizeDouble(B + TPPips * pip, dg), ORDER_TIME_GTC, 0, c)) slots[n].bt = tr.ResultOrder();
      else PrintFormat("%s buystop failed %d %s", s, tr.ResultRetcode(), tr.ResultRetcodeDescription());
      if(tr.SellStop(lots, S, s, NormalizeDouble(S + SLPips * pip, dg), NormalizeDouble(S - TPPips * pip, dg), ORDER_TIME_GTC, 0, c)) slots[n].st = tr.ResultOrder();
      else PrintFormat("%s sellstop failed %d %s", s, tr.ResultRetcode(), tr.ResultRetcodeDescription());
      slots[n].placed = true;
      PrintFormat("%s placed for %s: mid %.5f B %.5f S %.5f lots %.2f", s, TimeToString(evT[k], TIME_SECONDS), M, B, S, lots);
   }
}

bool OrderAlive(ulong t) { return t > 0 && OrderSelect(t); }

// exit price / time / profit of a closed position from its deals
void ClosedInfo(ulong posId, double &px, long &msc, double &profit)
{
   px = 0; msc = 0; profit = 0;
   if(!HistorySelectByPosition(posId)) return;
   for(int i = 0; i < HistoryDealsTotal(); i++)
   {
      ulong d = HistoryDealGetTicket(i);
      profit += HistoryDealGetDouble(d, DEAL_PROFIT) + HistoryDealGetDouble(d, DEAL_SWAP) + HistoryDealGetDouble(d, DEAL_COMMISSION);
      if(HistoryDealGetInteger(d, DEAL_ENTRY) == DEAL_ENTRY_OUT) { px = HistoryDealGetDouble(d, DEAL_PRICE); msc = HistoryDealGetInteger(d, DEAL_TIME_MSC); }
   }
}

void Manage(int n)
{
   if(slots[n].done || !slots[n].placed) return;
   string s = slots[n].sym; double pip = Pip(s); int dg = (int)SymbolInfoInteger(s, SYMBOL_DIGITS);
   datetime now = TimeTradeServer();
   if(!slots[n].filled)
   {
      // a position from one of our two orders?
      for(int i = PositionsTotal() - 1; i >= 0; i--)
      {
         ulong p = PositionGetTicket(i);
         if(p == 0 || PositionGetInteger(POSITION_MAGIC) != Magic || PositionGetString(POSITION_SYMBOL) != s) continue;
         ulong id = (ulong)PositionGetInteger(POSITION_IDENTIFIER);
         if(id != slots[n].bt && id != slots[n].st) continue;
         slots[n].filled = true; slots[n].pos = p;
         slots[n].dir = (id == slots[n].bt) ? 1 : -1;
         slots[n].trig = slots[n].dir > 0 ? slots[n].bstop : slots[n].sstop;
         slots[n].fill = PositionGetDouble(POSITION_PRICE_OPEN);
         slots[n].fillMsc = PositionGetInteger(POSITION_TIME_MSC);
         slots[n].slnow = PositionGetDouble(POSITION_SL);
         slots[n].peak = slots[n].fill;
         MqlTick t; SymbolInfoTick(s, t); slots[n].spreadAtFill = (t.ask - t.bid) / pip;
         ulong other = slots[n].dir > 0 ? slots[n].st : slots[n].bt;
         if(OrderAlive(other)) tr.OrderDelete(other);
         PrintFormat("%s filled %s at %.5f (stop %.5f, slip %.2f pips)", s, slots[n].dir > 0 ? "BUY" : "SELL", slots[n].fill, slots[n].trig,
                     slots[n].dir * (slots[n].fill - slots[n].trig) / pip);
         break;
      }
      if(!slots[n].filled && now >= slots[n].T + CancelSec)
      {
         if(OrderAlive(slots[n].bt)) tr.OrderDelete(slots[n].bt);
         if(OrderAlive(slots[n].st)) tr.OrderDelete(slots[n].st);
         slots[n].done = true; Log(slots[n], "nofill", 0, 0, 0);
      }
      return;
   }
   if(!PositionSelectByTicket(slots[n].pos))
   {
      double px; long msc; double pr; ClosedInfo(slots[n].pos, px, msc, pr);
      slots[n].done = true; Log(slots[n], "closed_sl_tp", px, msc, pr); return;
   }
   if(now >= slots[n].T + CloseSec)
   {
      tr.PositionClose(slots[n].pos);
      double px; long msc; double pr; ClosedInfo(slots[n].pos, px, msc, pr);
      slots[n].done = true; Log(slots[n], "time", px, msc, pr); return;
   }
   MqlTick t; if(!SymbolInfoTick(s, t)) return;
   double px = slots[n].dir > 0 ? t.bid : t.ask, e = slots[n].fill;
   slots[n].peak = slots[n].dir > 0 ? MathMax(slots[n].peak, px) : MathMin(slots[n].peak, px);
   if(slots[n].dir * (slots[n].peak - e) / pip >= LockPips) slots[n].armed = true;
   if(!slots[n].armed) return;
   double cand = slots[n].dir > 0 ? MathMax(e + pip, slots[n].peak - TrailPips * pip) : MathMin(e - pip, slots[n].peak + TrailPips * pip);
   cand = NormalizeDouble(cand, dg);
   if(slots[n].dir * (cand - slots[n].slnow) >= 0.2 * pip)
      if(tr.PositionModify(slots[n].pos, cand, PositionGetDouble(POSITION_TP))) slots[n].slnow = cand;
}

int OnInit()
{
   if(AccountInfoInteger(ACCOUNT_TRADE_MODE) != ACCOUNT_TRADE_MODE_DEMO) { Print("NewsStraddle: not a demo account - refusing"); return INIT_FAILED; }
   tr.SetExpertMagicNumber(Magic); tr.SetDeviationInPoints(0);
   StringSplit(Symbols, ',', syms);
   for(int i = 0; i < ArraySize(syms); i++) SymbolSelect(syms[i], true);
   EventSetMillisecondTimer(100);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) { EventKillTimer(); }

void OnTimer()
{
   datetime now = TimeTradeServer();
   if(now - lastLoad > 600) LoadCalendar();
   for(int k = 0; k < ArraySize(evT); k++)
      if(now >= evT[k] - PlaceSec && now < evT[k] + 5) Place(k);
   for(int n = 0; n < ArraySize(slots); n++) Manage(n);
}

void OnTick() { OnTimer(); }
