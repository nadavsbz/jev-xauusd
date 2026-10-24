//+------------------------------------------------------------------+
//| DragonClone: a rebuild of EA Black Dragon from its trades          |
//| (docs/BD_CLONE.md), for the tester only. Input names are those of |
//| the BD .set files, so bd_3digit_cal.set loads as it is.           |
//| Measured from 14,286 baskets of bd_cal_full:                      |
//|  - entry on a new M15 bar: buy if close > EMA(EmaPeriod),          |
//|    sell if below (99.4% agreement at EMA 98-100); one basket per  |
//|    side, both sides may be open (hedge), new baskets only between |
//|    Start_Hour and End_Hour                                        |
//|  - lot = Lot_Init_ x Martin_^(level-1), capped at MaxLot_          |
//|  - distance = Fix_Distance points up to level Order_dinamic_distance-1,|
//|    then Dynamic_distance_start x Distance_multiplier^(k)           |
//|  - exit: basket trailing on the average price, start iTS points,  |
//|    distance iTD points (TP_ as a hard take profit)                |
//|  - Overlap from OverlapOrderNumber orders: close the newest order |
//|    together with the oldest (worst) when their sum is >= OverlapPercent% |
//|    of the worst order's loss                                       |
//| Built-in guards (all off by default, docs/BD_CLONE.md):           |
//|  G_Crash: no new basket/level after a fast M1 crash score          |
//|  G_Context: no basket against the D1 EMA                          |
//|  G_BasketStopPct: close a basket whose floating loss > X% equity  |
//|  G_MaxLevelInCrash: during a crash no levels beyond this          |
//+------------------------------------------------------------------+
#property strict
#include <Trade\Trade.mqh>

input string qw0 = "//--- Basic parameters ---//";
input bool   NewCycle_ = true;
input bool   Flag_Trade_Buy_ = true;
input bool   Flag_Trade_Sell_ = true;
input bool   flag_Hand_Ord = false;
input bool   Flag_Use_hedge = true;
input string sOrdComm = "DragonClone";
input int    MaxSpred = 200;
input bool   LogSpread = false;
input bool   OneAddPerBar = true;     // ours, measured: BD never adds more than one level per basket per M15 bar       // ours: print the spread at every new M15 bar in trading hours (calibration)
input bool   LotFromNewest = true;    // ours, measured: next grid lot = newest open order x Martin_
input int    Start_Hour = 2;
input int    End_Hour = 21;
input long   Magic = 5555;
input string qw1 = "//--- Black Dragon parametrs ---//";
input int    TF_DB = 0;
input int    EmaPeriod = 99;           // ours: the trend EMA on M15 (measured)
input string qw2 = "//--- Modified_stochastic---//";
input bool   Use_Stoh = false;
input int    TF_Stoh = 0;
input int    Up_Level = 90;
input int    Down_Level = 10;
input int    KPeriod = 7;
input int    DPeriod = 1;
input int    Slowing = 2;
input string qw3 = "//--- Strategy Settings ---//";
input int    MaxOrdersBuy = 10;
input int    MaxOrdersSell = 10;
input double Lot_Init_ = 0.01;
input bool   Autolot_ = false;
input double Autolotsize_ = 1000;
input double Martin_ = 1.5;
input double MaxLot_ = 5.0;
input int    TP_Mode = 1;
input int    TP_ = 2000;
input int    SL_Mode = 1;
input int    SL_ = 0;
input int    Trail_Mode = 1;
input int    iTS = 600;
input int    iTD = 100;
input bool   Overlap = true;
input int    OverlapOrderNumber = 7;
input double OverlapPercent = 3;
input int    MinuteStop = 0;
input string qw4 = "//--- Distance settings ---//";
input int    Fix_Distance = 3000;
input int    Order_dinamic_distance = 6;
input int    Dynamic_distance_start = 2000;
input double Distance_multiplier = 1.2;
input string qw5 = "//--- News Setting ---//";
input bool   Flag_Use_News = false;
input string qw7 = "//--- Built-in guards (ours) ---//";
input bool   G_Crash = false;
input int    G_CrashBars = 15;
input double G_CrashMult = 3.0;        // drop over G_CrashBars M1 bars > this x avg M1 range x sqrt(bars)
input int    G_CrashPauseMin = 120;
input int    G_MaxLevelInCrash = 3;    // during a crash pause, no levels beyond this
input bool   G_Context = false;
input int    G_ContextEma = 50;
input double G_BasketStopPct = 0;      // 0 = off; close a basket at this floating loss, % of equity

CTrade trade;
int hEma, hEmaD;
datetime lastBar = 0, crashUntil = 0, lastAddBar[2] = {0, 0};
double hiWater[2], peakBasketProfit[2];
bool trailOn[2];

int OnInit()
  {
   hEma = iMA(_Symbol, PERIOD_M15, EmaPeriod, 0, MODE_EMA, PRICE_CLOSE);
   hEmaD = iMA(_Symbol, PERIOD_D1, G_ContextEma, 0, MODE_EMA, PRICE_CLOSE);
   if(hEma == INVALID_HANDLE || hEmaD == INVALID_HANDLE) return INIT_FAILED;
   if(AccountInfoInteger(ACCOUNT_MARGIN_MODE) != ACCOUNT_MARGIN_MODE_RETAIL_HEDGING) { Print("DragonClone needs a hedging account"); return INIT_FAILED; }
   trade.SetExpertMagicNumber(Magic);
   trailOn[0] = trailOn[1] = false; hiWater[0] = hiWater[1] = 0;
   return INIT_SUCCEEDED;
  }

double B(int h, int s) { double v[1]; return CopyBuffer(h, 0, s, 1, v) == 1 ? v[0] : 0; }

double LotFor(int level)   // level 1..N
  {
   double l = Lot_Init_;
   if(Autolot_) l = MathMax(0.01, NormalizeDouble(AccountInfoDouble(ACCOUNT_BALANCE) / Autolotsize_ * 0.01, 2));
   l = NormalizeDouble(l * MathPow(Martin_, level - 1), 2);
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   return MathMin(MathMax(l, vmin), MaxLot_);
  }

double NextLot(double newestV)   // the level whose lot is the newest open order, plus one (BD rounds from Lot_Init_, not step by step)
  {
   int k = 1; double best = DBL_MAX;
   for(int lv = 1; lv <= 60; lv++) { double d = MathAbs(LotFor(lv) - newestV); if(d < best - 1e-9) { best = d; k = lv; } }
   return LotFor(k + 1);
  }

double DistFor(int level)  // distance before opening order number `level` (2..N), in price
  {
   if(level < Order_dinamic_distance) return Fix_Distance * _Point;
   return Dynamic_distance_start * _Point * MathPow(Distance_multiplier, level - Order_dinamic_distance);
  }

struct Bsk { int n; double newestV; double vol; double pv; double last; double profit; ulong oldest; double oldestP; ulong newest; double newestP; datetime oldestT; datetime newestT; };

void Scan(int side, Bsk &b)   // side 0 buy, 1 sell
  {
   b.n = 0; b.newestV = 0; b.vol = 0; b.pv = 0; b.last = 0; b.profit = 0; b.oldest = 0; b.newest = 0; b.oldestT = D'2100.01.01'; b.newestT = 0; b.oldestP = 0; b.newestP = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(!PositionSelectByTicket(t) || PositionGetInteger(POSITION_MAGIC) != Magic || PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      int s = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 0 : 1;
      if(s != side) continue;
      double v = PositionGetDouble(POSITION_VOLUME), p = PositionGetDouble(POSITION_PRICE_OPEN);
      double pr = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
      datetime ot = (datetime)PositionGetInteger(POSITION_TIME);
      b.n++; b.vol += v; b.pv += v * p; b.profit += pr;
      if(ot < b.oldestT) { b.oldestT = ot; b.oldest = t; b.oldestP = pr; }
      if(ot >= b.newestT) { b.newestT = ot; b.newest = t; b.newestP = pr; b.last = p; b.newestV = v; }
     }
  }

void CloseSide(int side)
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(!PositionSelectByTicket(t) || PositionGetInteger(POSITION_MAGIC) != Magic || PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      int s = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 0 : 1;
      if(s == side) trade.PositionClose(t);
     }
   trailOn[side] = false; hiWater[side] = 0;
  }

bool CrashNow()
  {
   int n = G_CrashBars; MqlRates r[]; ArraySetAsSeries(r, true);
   if(CopyRates(_Symbol, PERIOD_M1, 1, n + 60, r) < n + 60) return false;
   double avg = 0; for(int i = n; i < n + 60; i++) avg += r[i].high - r[i].low; avg /= 60;
   double hi = r[0].high, lo = r[0].low; for(int i = 0; i < n; i++) { hi = MathMax(hi, r[i].high); lo = MathMin(lo, r[i].low); }
   double lim = G_CrashMult * avg * MathSqrt(n);
   return (hi - r[0].close > lim) || (r[0].close - lo > lim);   // a fast move either way
  }

void OnTick()
  {
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   datetime now = TimeCurrent();
   if(G_Crash)
     {
      static datetime lastM1 = 0; datetime m1 = iTime(_Symbol, PERIOD_M1, 0);
      if(m1 != lastM1) { lastM1 = m1; if(CrashNow()) crashUntil = now + G_CrashPauseMin * 60; }
     }
   bool crash = G_Crash && now < crashUntil;

   for(int side = 0; side < 2; side++)
     {
      Bsk b; Scan(side, b);
      if(b.n == 0) { trailOn[side] = false; hiWater[side] = 0; continue; }
      double avg = b.pv / b.vol, px = side == 0 ? bid : ask, sg = side == 0 ? 1 : -1;
      double move = sg * (px - avg);
      // basket stop (guard)
      if(G_BasketStopPct > 0 && b.profit < -G_BasketStopPct / 100 * AccountInfoDouble(ACCOUNT_EQUITY)) { CloseSide(side); continue; }
      // hard TP
      if(TP_Mode > 0 && TP_ > 0 && move >= TP_ * _Point) { CloseSide(side); continue; }
      // basket trailing on the average price
      if(Trail_Mode > 0)
        {
         if(move >= iTS * _Point) { trailOn[side] = true; hiWater[side] = MathMax(hiWater[side], move); }
         if(trailOn[side] && move <= hiWater[side] - iTD * _Point) { CloseSide(side); continue; }
        }
      // overlap: newest + oldest together when their sum covers OverlapPercent% of the oldest loss;
      // measured on 7.10.2026 (live1m_bdreal): BD closes the pair only with MORE than OverlapOrderNumber orders
      if(Overlap && b.n > OverlapOrderNumber && b.oldestP < 0 && b.newestP > 0 && b.newest != b.oldest)
        {
         if(b.newestP + b.oldestP >= -b.oldestP * OverlapPercent / 100)
           {   // close the oldest only after the newest (the profit that covers it) is really closed (QA PR 40)
            if(trade.PositionClose(b.newest) && trade.ResultRetcode() == TRADE_RETCODE_DONE) trade.PositionClose(b.oldest);
            continue;
           }
        }
      // next level
      int maxo = side == 0 ? MaxOrdersBuy : MaxOrdersSell;
      int lvl = b.n + 1;
      if(b.n < maxo && !(crash && lvl > G_MaxLevelInCrash))
        {
         double d = DistFor(lvl);
         bool hit = side == 0 ? (ask <= b.last - d) : (bid >= b.last + d);
         long spr = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
         datetime barNow = iTime(_Symbol, PERIOD_M15, 0);
         if(hit && spr <= MaxSpred && !(OneAddPerBar && lastAddBar[side] == barNow))
           {
            // lot: the newest open order x Martin_ (measured 7.10.2026: after an Overlap pair close BD adds
            // 3.08 after a remaining 2.05, i.e. the progression continues from the newest order, it does not
            // restart from the remaining count; QA PR 40). LotFromNewest=false restores the old count rule.
            double lot = LotFromNewest ? NextLot(b.newestV) : LotFor(lvl);
            bool ok = side == 0 ? trade.Buy(lot, _Symbol, 0, 0, 0, sOrdComm) : trade.Sell(lot, _Symbol, 0, 0, 0, sOrdComm);
            if(ok && trade.ResultRetcode() == TRADE_RETCODE_DONE && trade.ResultDeal() > 0) lastAddBar[side] = barNow;
           }
        }
     }

   // new baskets on a new M15 bar
   datetime bt = iTime(_Symbol, PERIOD_M15, 0);
   if(bt == lastBar) return;
   lastBar = bt;
   if(!NewCycle_ || crash) return;
   MqlDateTime dt; TimeToStruct(now, dt);
   if(dt.hour < Start_Hour || dt.hour >= End_Hour) return;
   if(LogSpread) PrintFormat("SPR %s %d %.2f", TimeToString(bt), (int)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD), SymbolInfoDouble(_Symbol, SYMBOL_BID));
   if(SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) > MaxSpred) return;
   double c = iClose(_Symbol, PERIOD_M15, 1), e = B(hEma, 1);
   if(e <= 0) return;
   int dir = c > e ? 0 : (c < e ? 1 : -1);
   if(dir < 0) return;
   if(G_Context)
     {
      double d1 = iClose(_Symbol, PERIOD_D1, 1), ed = B(hEmaD, 1);
      if(dir == 0 && d1 < ed) return;
      if(dir == 1 && d1 > ed) return;
     }
   Bsk b; Scan(dir, b);
   if(b.n > 0) return;
   if(!Flag_Use_hedge) { Bsk o; Scan(1 - dir, o); if(o.n > 0) return; }
   if(dir == 0 && Flag_Trade_Buy_) trade.Buy(LotFor(1), _Symbol, 0, 0, 0, sOrdComm);
   if(dir == 1 && Flag_Trade_Sell_) trade.Sell(LotFor(1), _Symbol, 0, 0, 0, sOrdComm);
  }
