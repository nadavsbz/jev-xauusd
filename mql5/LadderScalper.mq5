//+------------------------------------------------------------------+
//| LadderScalper: our own rebuild of the Bull Scalper mechanics      |
//| (docs/BULL_ANATOMY.md), for the tester only.                      |
//| Buy-only ladder: open a buy, add buys lower by an ATR-based step  |
//| (DCA), and when the newest position is trailing add another one   |
//| ("stackable"). Every position has its own trailing stop that      |
//| starts only after it covers its own swap and commission.          |
//| Optional guards from the new version's parameter names:           |
//| market context (D1 EMA), crash pause (fast drop), max total lots. |
//+------------------------------------------------------------------+
#property strict
#include <Trade\Trade.mqh>

input double Lot            = 0.01;
input int    MaxPositions   = 10;
input ENUM_TIMEFRAMES AiTF  = PERIOD_M5;   // ATR timeframe ("AI on 5-15 minutes")
input int    AtrPeriod      = 14;
input double SpaceMult      = 3.0;         // step between ladder entries, in ATR
input double TrailStartMult = 1.0;         // trailing starts after this profit, in ATR
input double TrailDistMult  = 0.5;         // trailing distance, in ATR
input double MinStepMult    = 0.1;         // move the SL only if it improves by this, in ATR
input bool   StackOnTrail   = true;        // add a buy when the newest position is already trailing
input int    CooldownSec    = 60;          // between new entries
input bool   CostAware      = true;        // trailing starts only after swap + commission are covered
input double CommPerLot     = 0.0;         // account currency per lot per side (the tester also charges it)
input bool   UseContext     = false;       // add only if the D1 close is above its EMA
input int    ContextEma     = 50;
input bool   UseCrashPause  = false;       // no new entries after a fast drop
input int    CrashBars      = 15;          // M1 bars
input double CrashAtrMult   = 3.0;         // drop over CrashBars larger than this many AiTF ATRs = crash
input int    CrashPauseMin  = 120;
input double MaxTotalLots   = 1.0;
input long   Magic          = 77101;

CTrade trade;
int hAtr = INVALID_HANDLE, hEma = INVALID_HANDLE;
datetime lastEntry = 0, pauseUntil = 0;

int OnInit()
  {
   hAtr = iATR(_Symbol, AiTF, AtrPeriod);
   hEma = iMA(_Symbol, PERIOD_D1, ContextEma, 0, MODE_EMA, PRICE_CLOSE);
   if(hAtr == INVALID_HANDLE || hEma == INVALID_HANDLE) return INIT_FAILED;
   trade.SetExpertMagicNumber(Magic);
   return INIT_SUCCEEDED;
  }

double Buf(int h, int shift)
  {
   double v[1];
   if(CopyBuffer(h, 0, shift, 1, v) != 1) return 0;
   return v[0];
  }

void OnTick()
  {
   double atr = Buf(hAtr, 1);
   if(atr <= 0) return;
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double tickVal = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   int stopsLvl = (int)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   double minDist = stopsLvl * _Point;

   int n = 0; double lots = 0, lowest = DBL_MAX; datetime newestT = 0; ulong newest = 0; bool newestTrailing = false;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(!PositionSelectByTicket(t) || PositionGetInteger(POSITION_MAGIC) != Magic) continue;
      n++;
      double vol = PositionGetDouble(POSITION_VOLUME), op = PositionGetDouble(POSITION_PRICE_OPEN), sl = PositionGetDouble(POSITION_SL);
      lots += vol; lowest = MathMin(lowest, op);
      datetime ot = (datetime)PositionGetInteger(POSITION_TIME);
      // costs to cover, in price: swap so far (negative = cost) and the round-trip commission
      double cost = 0;
      if(CostAware && tickVal > 0)
        {
         double money = -MathMin(0.0, PositionGetDouble(POSITION_SWAP)) + 2 * CommPerLot * vol;
         cost = money / (tickVal / tickSize * vol);
        }
      double start = op + cost + TrailStartMult * atr;
      bool trailing = sl > 0 && sl >= op;
      if(bid >= start || trailing)
        {
         double nsl = NormalizeDouble(bid - TrailDistMult * atr, _Digits);
         if(nsl >= op + cost && nsl > sl + MinStepMult * atr && bid - nsl > minDist)
           {
            if(trade.PositionModify(t, nsl, 0)) trailing = true;
           }
        }
      if(ot >= newestT) { newestT = ot; newest = t; newestTrailing = trailing; }
     }

   // entries
   datetime now = TimeCurrent();
   if(now - lastEntry < CooldownSec || now < pauseUntil) return;
   if(UseCrashPause)
     {
      double hi = iHigh(_Symbol, PERIOD_M1, iHighest(_Symbol, PERIOD_M1, MODE_HIGH, CrashBars, 1));
      if(hi - bid > CrashAtrMult * atr) { pauseUntil = now + CrashPauseMin * 60; return; }
     }
   if(UseContext && iClose(_Symbol, PERIOD_D1, 1) < Buf(hEma, 1)) return;
   if(n >= MaxPositions || lots + Lot > MaxTotalLots + 1e-9) return;
   bool go = (n == 0) || (ask <= lowest - SpaceMult * atr) || (StackOnTrail && newestTrailing);
   if(go && trade.Buy(Lot, _Symbol)) lastEntry = now;
  }
