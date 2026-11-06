//+------------------------------------------------------------------+
//| IndexNoise: I2 in research/stable/second4.py (Zarattini, Aziz &  |
//| Barbon 2024 'noise area' intraday momentum, adapted to H1).      |
//| At each close of the server-hour bars 16..21: long above upper,  |
//| short below lower, flat inside; flat at the close of bar 22.     |
//| Sizing (TargetVol > 0): as second4.scale_s - the rule's own daily |
//| return per 1x notional (recomputed from the bars, as the sim),   |
//| its std over the last 90 days (60 at least) x sqrt(260), and      |
//| lots = min(5, TargetVol / vol) x equity / (O x contract), fixed   |
//| for the day. TargetVol = 0 -> fixed Lots (the edge test).        |
//+------------------------------------------------------------------+
#property strict
#include <Trade/Trade.mqh>
input int    OpenHour  = 16;     // server hour whose bar open is the day open O (NY 9:00)
input int    LastCheck = 21;     // last check bar (its close = NY 15:00)
input int    ExitHour  = 22;     // flat at the close of this bar (NY 16:00)
input int    Lookback  = 14;     // days in the noise average
input double Lots      = 1.0;    // used when TargetVol = 0
input double TargetVol = 0.0;    // annual vol target of the rule (0.10 = the sim); 0 = fixed Lots
input double CostPct   = 0.015;  // per position change, % of notional, in the sizing returns (as the sim: 0.01% + 0.005%)
input long   Magic     = 7302;

CTrade tr;
datetime lastBar = 0, sizedDay = 0;
double dayLots = 0;
MqlRates R[]; int N = 0;

datetime Day(datetime t) { return t - t % 86400; }

// index of the bar of day d and hour k in R, or -1 (R is sorted by time)
int Bar(datetime d, int k)
{
   datetime t = d + k * 3600;
   int lo = 0, hi = N - 1;
   while(lo <= hi) { int m = (lo + hi) / 2; if(R[m].time == t) return m; if(R[m].time < t) lo = m + 1; else hi = m - 1; }
   return -1;
}

// a complete trading day: the open bar, every check bar and the exit bar exist
bool Full(datetime d)
{
   for(int k = OpenHour; k <= ExitHour; k++) if(Bar(d, k) < 0) return false;
   return true;
}

// noise sigma for hour k and the previous day's exit close, from the Lookback full days before d
bool Noise(datetime d, int k, double &sig, double &prev)
{
   double sum = 0; int m = 0; prev = 0;
   for(datetime e = d - 86400; e > d - 86400 * (Lookback * 2 + 14) && m < Lookback; e -= 86400)
   {
      if(!Full(e)) continue;
      if(prev == 0) prev = R[Bar(e, ExitHour)].close;
      sum += MathAbs(R[Bar(e, k)].close / R[Bar(e, OpenHour)].open - 1); m++;
   }
   sig = m == Lookback ? sum / m : 0;
   return m == Lookback && prev > 0;
}

// the position the rule wants at the close of check bar k on day d (0 when the data is missing)
int Want(datetime d, int k)
{
   int io = Bar(d, OpenHour), ik = Bar(d, k);
   if(io < 0 || ik < 0) return 0;
   double s, prev; if(!Noise(d, k, s, prev)) return 0;
   double o = R[io].open, c = R[ik].close;
   if(c > MathMax(o, prev) * (1 + s)) return 1;
   if(c < MathMin(o, prev) * (1 - s)) return -1;
   return 0;
}

// the rule's net return on day d per 1x notional, as second4.strat (0 for an incomplete day)
double DayRet(datetime d)
{
   if(!Full(d)) return 0;
   double s, prev; if(!Noise(d, OpenHour, s, prev)) return 0;
   int q = 0; double r = 0, last = 0;
   for(int k = OpenHour; k <= ExitHour; k++)
   {
      double c = R[Bar(d, k)].close;
      if(last > 0 && q != 0) r += q * (c / last - 1);
      last = c;
      int nq = k == ExitHour ? 0 : Want(d, k);
      r -= MathAbs(nq - q) * CostPct / 100; q = nq;
   }
   return r;
}

double SizeFor(datetime d)
{
   if(TargetVol <= 0) return Lots;
   double x[]; int m = 0; ArrayResize(x, 90);
   for(datetime e = d - 86400; e > d - 86400 * 200 && m < 90; e -= 86400)
   {
      if(!Full(e)) continue;   // complete trading days, as the rows of the sim
      x[m++] = DayRet(e);
   }
   if(m < 60) return 0;
   double mu = 0, v = 0; for(int i = 0; i < m; i++) mu += x[i]; mu /= m;
   for(int i = 0; i < m; i++) v += (x[i] - mu) * (x[i] - mu);
   double vol = MathSqrt(v / (m - 1)) * MathSqrt(260); if(vol <= 0) return 0;
   double lev = MathMin(5.0, TargetVol / vol);
   int io = Bar(d, OpenHour); if(io < 0) return 0;
   double cs = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE), st = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double lots = MathFloor(lev * AccountInfoDouble(ACCOUNT_EQUITY) / (R[io].open * cs) / st) * st;
   return MathMin(lots, SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX));
}

int Pos()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
      if(PositionGetTicket(i) > 0 && PositionGetInteger(POSITION_MAGIC) == Magic && PositionGetString(POSITION_SYMBOL) == _Symbol)
         return PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 1 : -1;
   return 0;
}

// close every position of this EA on this symbol, by ticket (the account may hold other EAs' positions);
// true only when none is left (Codex PR 44, 1.11: check the close before opening the other side)
bool Flat()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t > 0 && PositionGetInteger(POSITION_MAGIC) == Magic && PositionGetString(POSITION_SYMBOL) == _Symbol)
         tr.PositionClose(t);
   }
   return Pos() == 0;
}

// move to position q; false when an order failed, so the same bar is tried again on the next tick
bool Go(int q)
{
   int p = Pos();
   if(p == q) return true;
   if(p != 0 && !Flat()) return false;
   if(q == 0 || dayLots < SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN)) return true;
   bool ok = q > 0 ? tr.Buy(dayLots, _Symbol) : tr.Sell(dayLots, _Symbol);
   return ok && (tr.ResultRetcode() == TRADE_RETCODE_DONE || tr.ResultRetcode() == TRADE_RETCODE_PLACED);
}

// minutes left in the trade session that contains now (weekly schedule of the symbol); -1 when none is found.
// Holiday early closes are not in the weekly schedule unless the server updates it (known limit, docs).
int SessionLeft()
{
   MqlDateTime t; datetime now = TimeCurrent(); TimeToStruct(now, t);
   int sec = t.hour * 3600 + t.min * 60 + t.sec; datetime from, to;
   for(uint i = 0; SymbolInfoSessionTrade(_Symbol, (ENUM_DAY_OF_WEEK)t.day_of_week, i, from, to); i++)
   {
      int a = (int)(from % 86400), b = (int)(to % 86400); if(b == 0) b = 86400;
      if(sec >= a && sec < b) return (b - sec) / 60;
   }
   return -1;
}

int OnInit() { tr.SetExpertMagicNumber(Magic); return INIT_SUCCEEDED; }

void OnTick()
{
   // time guard on every tick (Codex PR 44, 1.11): flat after the exit bar or before the open bar even when a bar is
   // missing, and before an early end of the trade session
   MqlDateTime now; TimeToStruct(TimeCurrent(), now);
   int left = SessionLeft();
   if(Pos() != 0 && (now.hour > ExitHour || now.hour < OpenHour || (left >= 0 && left <= 10))) { Flat(); return; }
   datetime b = iTime(_Symbol, PERIOD_H1, 0);
   if(b == lastBar) return;
   N = CopyRates(_Symbol, PERIOD_H1, 1, 24 * 220, R);   // R[N-1] = the bar that just closed
   if(N < 24 * 30) return;
   MqlDateTime t; TimeToStruct(R[N - 1].time, t); int k = t.hour;
   datetime d = Day(R[N - 1].time);
   bool done = true;
   if(k == ExitHour || d != Day(b)) done = Flat();                          // the day's exit (or a new day began)
   else if(k >= OpenHour && k <= LastCheck)
   {
      if(R[N - 1].time != b - 3600) done = Pos() == 0 || Flat();           // a gap: the check bar is stale, do not enter
      else if(left >= 0 && left <= 70) done = Flat();                       // the session ends before the next check
      else
      {
         if(sizedDay != d) { dayLots = SizeFor(d); sizedDay = d; }
         done = Go(Want(d, k));
      }
   }
   if(done) lastBar = b;                                                    // otherwise the same bar is retried next tick
}
