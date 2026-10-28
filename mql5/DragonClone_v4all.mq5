//+------------------------------------------------------------------+
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
input int    EntryTickDelay = 0;      // ours, measured 25.10: a third of BD first entries fill at a later tick of the bar-open second
input bool   TrailBySL = true;        // ours, measured 25.10: BD basket exits never below iTS-iTD, i.e. a real stop at the server
input bool   OpenUsesBarAdd = true;   // ours, measured: no level 2 in the bar where the basket opened
input bool   LotFromOldest = true;    // ours, measured 25.10: next lot = oldest open lot x Martin_^(open count); explains 3.11/4.63/4.67 after Overlap
input bool   EntryRetrySpread = true;  // ours, VERIFIED 25.10 with MaxSpred=200 (reproduces the 28.5.2026 14:30 wipe): a bar skipped for spread is retried on later ticks of the same bar
input bool   OverlapResetsTrail = false; // ours, tested 25.10 (exp4_jun26): no effect on any deal; kept off
input bool   TrailIncludesSwap = true;  // ours, VERIFIED 25.10 (8.6.2026 02:28, reproduces the June wipe): basket trailing counts from the breakeven price incl. swap
input bool   OverlapAtCount = true;
input string qw8 = "//--- v4all (ours) ---//";
input int    LotAfterOverlap = 0;     // v4a: after an Overlap close cap the next lots: 1 = the closed oldest lot, 2 = the closed newest lot, 3 = closed newest / Martin_
input double ExpoLotsPer100k = 0;     // v4b: no add that takes the side above this many lots per 100,000 of equity (0 = off)
input int    NewsPauseFrom = 0;       // v4c: server time HHMM where the pause starts on weekdays (0 = off)
input int    NewsPauseMin = 0;        // v4c: pause length in minutes: no new baskets and no adds   // ours, measured 25.10: Overlap fires with OverlapOrderNumber orders on the side (>=), not more
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
double ovNewV[2], ovOldV[2]; int ovCnt[2];
double hiWater[2], peakBasketProfit[2], trailAvg[2];
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

double OldestLot(double oldestV, int n)   // oldest open lot x Martin_^n (25.10: 0.41 x 1.5^5 = 3.11, 0.61 x 1.5^5 = 4.63)
  {
   double l = NormalizeDouble(oldestV * MathPow(Martin_, n), 2);
   return MathMin(MathMax(l, SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN)), MaxLot_);
  }

double DistFor(int level)  // distance before opening order number `level` (2..N), in price
  {
   if(level < Order_dinamic_distance) return Fix_Distance * _Point;
   return Dynamic_distance_start * _Point * MathPow(Distance_multiplier, level - Order_dinamic_distance);
  }

struct Bsk { int n; double swap; double newestV; double oldestV; double vol; double pv; double last; double profit; ulong oldest; double oldestP; ulong newest; double newestP; datetime oldestT; datetime newestT; };

void Scan(int side, Bsk &b)   // side 0 buy, 1 sell
  {
   b.n = 0; b.swap = 0; b.newestV = 0; b.oldestV = 0; b.vol = 0; b.pv = 0; b.last = 0; b.profit = 0; b.oldest = 0; b.newest = 0; b.oldestT = D'2100.01.01'; b.newestT = 0; b.oldestP = 0; b.newestP = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(!PositionSelectByTicket(t) || PositionGetInteger(POSITION_MAGIC) != Magic || PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      int s = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 0 : 1;
      if(s != side) continue;
      double v = PositionGetDouble(POSITION_VOLUME), p = PositionGetDouble(POSITION_PRICE_OPEN);
      double pr = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
      datetime ot = (datetime)PositionGetInteger(POSITION_TIME);
      b.n++; b.swap += PositionGetDouble(POSITION_SWAP); b.vol += v; b.pv += v * p; b.profit += pr;
      if(ot < b.oldestT) { b.oldestT = ot; b.oldest = t; b.oldestP = pr; b.oldestV = v; }
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

void SetSideSL(int side, double slPx)   // move every position of the side to one stop; only ever tighten
  {
   slPx = NormalizeDouble(slPx, _Digits);
   double minD = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point;
   double px = side == 0 ? SymbolInfoDouble(_Symbol, SYMBOL_BID) : SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   if(side == 0 ? slPx > px - minD : slPx < px + minD) { CloseSide(side); return; }   // already through the stop
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(!PositionSelectByTicket(t) || PositionGetInteger(POSITION_MAGIC) != Magic || PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      int s = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 0 : 1;
      if(s != side) continue;
      double cur = PositionGetDouble(POSITION_SL);
      bool better = cur == 0 || (side == 0 ? slPx > cur + _Point / 2 : slPx < cur - _Point / 2);
      if(better) trade.PositionModify(t, slPx, PositionGetDouble(POSITION_TP));
     }
  }

void ClearTrail(int side)   // trailing off and the stops removed from the rest of the side
  {
   trailOn[side] = false; hiWater[side] = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(!PositionSelectByTicket(t) || PositionGetInteger(POSITION_MAGIC) != Magic || PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      int s = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 0 : 1;
      if(s == side && PositionGetDouble(POSITION_SL) != 0) trade.PositionModify(t, 0, PositionGetDouble(POSITION_TP));
     }
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

// ---- v4all hooks ----
bool InNewsPause()
  {
   if(NewsPauseFrom <= 0 || NewsPauseMin <= 0) return false;
   MqlDateTime t; TimeToStruct(TimeCurrent(), t);
   if(t.day_of_week == 0 || t.day_of_week == 6) return false;
   int m = t.hour * 60 + t.min, s = (NewsPauseFrom / 100) * 60 + NewsPauseFrom % 100;
   return m >= s && m < s + NewsPauseMin;
  }

double V4Lot(int side, Bsk &b, double lot)
  {
   if(LotAfterOverlap <= 0 || ovCnt[side] == 0) return lot;
   double cap = LotAfterOverlap == 1 ? ovOldV[side] : LotAfterOverlap == 2 ? ovNewV[side] : ovNewV[side] / Martin_;
   cap = MathMax(NormalizeDouble(cap, 2), SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN));
   return MathMin(lot, cap);
  }

bool V4AddOk(int side, Bsk &b, double lot)
  {
   if(InNewsPause()) return false;
   if(ExpoLotsPer100k <= 0) return true;
   return b.vol + lot <= ExpoLotsPer100k * AccountInfoDouble(ACCOUNT_EQUITY) / 100000.0;
  }

double V4Dist(int lvl) { return DistFor(lvl); }

void V4OnOverlap(int side, Bsk &b) { ovNewV[side] = b.newestV; ovOldV[side] = b.oldestV; ovCnt[side]++; }

void V4Reset(int side) { ovNewV[side] = 0; ovOldV[side] = 0; ovCnt[side] = 0; }

bool V4EntryOk() { return !InNewsPause(); }

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
      if(b.n == 0) { trailOn[side] = false; hiWater[side] = 0; V4Reset(side); continue; }
      double avg = b.pv / b.vol, px = side == 0 ? bid : ask, sg = side == 0 ? 1 : -1;
      if(TrailIncludesSwap) avg -= sg * b.swap / (b.vol * SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE));   // negative swap moves breakeven away
      // keep the trailing stop an absolute price when an Overlap pair close shifts the average (Codex PR 40, P2)
      if(trailOn[side] && trailAvg[side] > 0 && MathAbs(avg - trailAvg[side]) > _Point / 2) hiWater[side] += sg * (trailAvg[side] - avg);
      trailAvg[side] = avg;
      double move = sg * (px - avg);
      // basket stop (guard)
      if(G_BasketStopPct > 0 && b.profit < -G_BasketStopPct / 100 * AccountInfoDouble(ACCOUNT_EQUITY)) { CloseSide(side); continue; }
      // hard TP
      if(TP_Mode > 0 && TP_ > 0 && move >= TP_ * _Point) { CloseSide(side); continue; }
      // basket trailing on the average price
      if(Trail_Mode > 0)
        {
         if(move >= iTS * _Point) { trailOn[side] = true; hiWater[side] = MathMax(hiWater[side], move); }
         if(trailOn[side] && TrailBySL) SetSideSL(side, avg + sg * (hiWater[side] - iTD * _Point));
         else if(trailOn[side] && move <= hiWater[side] - iTD * _Point) { CloseSide(side); continue; }
        }
      // overlap: newest + oldest together when their gross sum covers OverlapPercent% of the oldest loss
      // (25.10, val_sep26_bdreal: all 26 BD pair closes fire with 7 orders on the side and just above 3%, e.g. 60.36 vs 59.1)
      int ovN = OverlapAtCount ? OverlapOrderNumber : OverlapOrderNumber + 1;
      if(Overlap && b.n >= ovN && b.oldestP < 0 && b.newestP > 0 && b.newest != b.oldest)
        {
         if(b.newestP + b.oldestP >= -b.oldestP * OverlapPercent / 100)
           {   // close the oldest only after the newest (the profit that covers it) is really closed (QA PR 40)
            if(trade.PositionClose(b.newest) && trade.ResultRetcode() == TRADE_RETCODE_DONE) trade.PositionClose(b.oldest);
            if(OverlapResetsTrail) ClearTrail(side);
            V4OnOverlap(side, b);
            continue;
           }
        }
      // next level
      int maxo = side == 0 ? MaxOrdersBuy : MaxOrdersSell;
      int lvl = b.n + 1;
      if(b.n < maxo && !(crash && lvl > G_MaxLevelInCrash))
        {
         double d = V4Dist(lvl);
         bool hit = side == 0 ? (ask <= b.last - d) : (bid >= b.last + d);
         long spr = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
         datetime barNow = iTime(_Symbol, PERIOD_M15, 0);
         if(hit && spr <= MaxSpred && !(OneAddPerBar && lastAddBar[side] == barNow))
           {
            // lot: the newest open order x Martin_ (measured 7.10.2026: after an Overlap pair close BD adds
            // 3.08 after a remaining 2.05, i.e. the progression continues from the newest order, it does not
            // restart from the remaining count; QA PR 40). LotFromNewest=false restores the old count rule.
            double lot = LotFromOldest ? OldestLot(b.oldestV, b.n) : LotFromNewest ? NextLot(b.newestV) : LotFor(lvl);
            lot = V4Lot(side, b, lot);
            if(!V4AddOk(side, b, lot)) continue;
            bool ok = side == 0 ? trade.Buy(lot, _Symbol, 0, 0, 0, sOrdComm) : trade.Sell(lot, _Symbol, 0, 0, 0, sOrdComm);
            if(ok && trade.ResultRetcode() == TRADE_RETCODE_DONE && trade.ResultDeal() > 0) lastAddBar[side] = barNow;
           }
        }
     }

   // new baskets on a new M15 bar
   datetime bt = iTime(_Symbol, PERIOD_M15, 0);
   static int tickInBar = 0; static bool pending = false;
   if(bt != lastBar) { lastBar = bt; tickInBar = 0; pending = true; }
   else tickInBar++;
   if(EntryRetrySpread) { if(!pending) return; }                   // until the bar's entry decision is made
   else if(tickInBar != EntryTickDelay) return;   // act once per bar, on tick number EntryTickDelay (0 = the first tick)
   if(!NewCycle_ || crash) return;
   if(!V4EntryOk()) return;
   MqlDateTime dt; TimeToStruct(now, dt);
   if(dt.hour < Start_Hour || dt.hour >= End_Hour) return;
   if(LogSpread) PrintFormat("SPR %s %d %.2f", TimeToString(bt), (int)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD), SymbolInfoDouble(_Symbol, SYMBOL_BID));
   if(SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) > MaxSpred) return;   // with EntryRetrySpread: try again next tick
   pending = false;
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
   // the opening order also uses the bar's one add (measured 25.10: 82% of BD level-2 adds fall on the NEXT bar open)
   bool opened = false;
   if(dir == 0 && Flag_Trade_Buy_) opened = trade.Buy(LotFor(1), _Symbol, 0, 0, 0, sOrdComm);
   if(dir == 1 && Flag_Trade_Sell_) opened = trade.Sell(LotFor(1), _Symbol, 0, 0, 0, sOrdComm);
   if(opened && OpenUsesBarAdd && trade.ResultRetcode() == TRADE_RETCODE_DONE) lastAddBar[dir] = bt;
  }
