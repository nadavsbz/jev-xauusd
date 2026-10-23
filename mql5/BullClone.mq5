//+------------------------------------------------------------------+
//| BullClone: a rebuild of EA Bull Scalper (developer's new version, |
//| "BULLScalper4"), for the tester only (docs/BULL_CLONE.md).        |
//| Input names are EXACTLY those of the developer's .set files       |
//| (testbull4.set, bull_new_profit.set, bull100.set), so the files   |
//| load as they are. What each input does is OUR interpretation of   |
//| its name + the observed trades of version 4.3 (BULL_ANATOMY.md):  |
//|  - buy-only ladder, DCA lower, stack more buys while trailing     |
//|  - every position has its own trailing stop that starts only after|
//|    swap + commission are covered                                   |
//|  - guards: crash detection, market context, bear prediction,      |
//|    margin protection, max drawdown.                               |
//| Defaults = testbull4.set.                                         |
//+------------------------------------------------------------------+
#property strict
#include <Trade\Trade.mqh>

// ═══ TRADE BASICS ═══
input int    InpMagicNumber = 110;
input bool   InpOpenInitialBuy = true;
input int    InpMaxPositions = 20;
// ═══ TREND BURST ═══ (bigger lot on a confident up-prediction)
input bool   InpUseTrendBurst = true;
input double InpTrendBurstMultiplier = 3.0;
input double InpTrendBurstMinConfidence = 0.65;
input double InpTrendBurstMinMarginLevel = 400.0;
input double InpLotSize = 0.1;
input int    InpCooldownSeconds = 1;
input int    InpErrorWaitColddown = 10;
// ═══ DCA RECOVERY STACK ═══
input bool   InpUseDynamicValues = true;      // distances from volatility (ATR) instead of fixed points
input int    InpAiLookbackTF = 1;             // ENUM_TIMEFRAMES value: 1=M1, 5=M5, 15=M15, 16385=H1, 16388=H4
input double InpAiSensitivity = 0.7;          // scales the volatility unit
input double InpSpreadValueMult = 15.0;       // DCA step floor, in spreads
input double InpDcaProgressiveStepPct = 10.0; // every next DCA step this % wider
input double InpMinimumSpaceMultiplier = 0.6; // DCA step, in volatility units
input bool   InpUseDcaMagnetizer = true;      // at a DCA level, wait for a bullish M1 close before buying
input double InpMinimumSpacingMult = 0.1;     // minimum distance between any two entries, in volatility units
// ═══ PROFIT LOCK & CHAIN ═══
input bool   InpUseSecureProfit = true;       // lock a small net profit once a position earns enough
input double InpSecureNetProfit = 0.06;       // account currency per 0.01 lot
input double InpLockActivateProfit = 0.15;    // account currency per 0.01 lot
input bool   InpUsePaceKeeper = true;         // keep activity: if no entry for PaceTargetSeconds and the top is trailing, add
input int    InpPaceTargetSeconds = 90;
input bool   InpUseMomentumRide = true;       // widen the trailing when price runs far
input double InpMomentumActivateMult = 3.0;
// ═══ CHAIN SPACING ═══ (stacking above, while the newest position trails)
input bool   InpUseFixedChainSpacing = true;
input int    InpChainSpacingPoints = 30;
input int    InpLockConfirmSeconds = 5;       // profit must hold this long before the first lock
// ═══ COHERENCE BURST ═══ (M1, M5, M15 all rising: add extra buys)
input bool   InpUseCoherenceBurst = true;
input double InpCoherenceMinStrength = 0.5;
input double InpCoherenceExtraDistPct = 0.1;
input int    InpCoherenceBlastBatchSafetyCap = 100;
input bool   InpUseCoherenceClusterBlast = true;
input int    InpCoherenceClusterMaxPositions = 500;
input double InpCoherenceAccountUsagePct = 50.0;
input int    InpCoherenceBlastCooldownMs = 400;
input double InpCoherenceBlastMinMarginLevel = 500.0;
input bool   InpUsePhantomChain = true;       // trailing stop kept virtual; a real safety SL sits further away
input double InpSLTriggerDistance = 2.0;      // real SL = virtual SL - this x trailing distance
input int    InpSecureCheckMs = 25;
// ═══ TRAILING STOP ═══
input int    InpTrailMode = 2;                // 0 points, 1 volatility, 2 the larger of both
input int    InpAiLookbackBars = 200;         // bars for the volatility unit
input double InpTrailStartMult = 1.0;
input double InpTrailDistMult = 0.5;
input int    InpTrailStartPoints = 300;
input int    InpTrailDistPoints = 200;
input double InpTrailNetProfit = 0.4;         // minimum net profit (per 0.01 lot) before trailing starts
input double InpMinSLChangeMult = 0.6;        // SL step, in fractions of the trailing distance
input bool   InpUseTrailingFallback = true;   // close if the profit gives back FallbackPercent of its peak for FallbackSeconds
input int    InpFallbackSeconds = 5;
input double InpFallbackPercent = 5.0;
// ═══ LOT SIZING (Martingale) ═══
input bool   InpUseIncrementalLotTrailing = false;
input bool   InpUseAggressiveTrailing = false;
input bool   InpUseIncrementalLotOpenPrice = false;  // DCA lot grows by one base lot per level
input bool   InpUseAggressiveOpenPrice = false;      // DCA lot doubles per level
input bool   InpUseMartingaleReversal = false;
// ═══ PROFIT COMPOUNDING ═══
input bool   InpUseLogCompounding = true;
input double InpCompoundReinvestRatio = 0.5;
input double InpCompoundMaxLotMult = 2.0;
input int    InpCompoundWindowMin = 60;
// ═══ RISK & DRAWDOWN ═══
input double InpMaxDrawdownPercent = 100.0;
input bool   InpCloseAllOnMaxDrawdown = false;
input bool   InpUseMarginLimit = false;       // no new entry under 1000% margin level
// ═══ MARGIN PROTECTION ═══
input bool   InpUseMarginProtection = true;
input double InpMarginSafetyMultiplier = 1.8; // free margin must cover the new position this many times
input double InpMarginCriticalMultiplier = 1.3; // margin level under 130% x this x stop-out = emergency
input bool   InpAllowEmergencyMarginClose = true;
input bool   InpUseRiskLimit = false;         // close the worst position when its loss exceeds RiskMult volatility units
input double InpRiskMult = 150.0;
input bool   InpUseRiskDelay = true;          // after a risk close, pause entries
input int    InpRiskDelaySeconds = 300;
// ═══ CRASH PROTECTION ═══
input bool   InpUseCrashDetection = true;
input int    InpCrashLookbackBars = 15;
input double InpCrashVelocityMult = 3.0;
input int    InpCrashConsecBearish = 5;
input double InpCrashBodyRatioMult = 2.5;
input int    InpCrashSpreadMult = 3;
input int    InpCrashMinScore = 2;
input int    InpStabilizeConfirmBars = 3;
input int    InpCrashCooldownSeconds = 120;
// ═══ MARKET CONTEXT FILTER ═══
input bool   InpUseMarketContext = true;
input int    InpContextD1EmaPeriod = 50;
input int    InpContextH4EmaPeriod = 20;
input int    InpContextH1EmaPeriod = 20;
input double InpContextRangeRatioMax = 2.0;
input double InpContextTrendRatio = 3.5;
input double InpContextDrawdownPct = 3.0;
input int    InpContextResumeH1Bars = 2;
// ═══ EVERY CANDLE ACTIVITY ═══
input bool   InpUseEveryCandle = true;        // one buy per new AI-timeframe bar when allowed
input int    InpActivityCooldownBars = 1;
input bool   InpUseNewHighFilter = false;     // no initial buy at a new high of HighLookbackHours
input int    InpHighLookbackHours = 6;
input int    InpResistent = 3;                // not interpreted (unknown meaning)
// ═══ PREDICTION TREND LINE ═══
input bool   InpUsePrediction = true;
input int    InpPredLookback = 1500;
input double InpConfRollingDecay = 0.998;
input int    InpPredFutureBars = 10;
input double InpPredConfidenceMin = 0.6;
input double InpPredDcaAdjustPct = 0.8;      // bear prediction: DCA step wider by this fraction
input bool   InpBlockChainOnBearPred = true;
input bool   InpUseDynamicCooldown = true;    // bear prediction: cooldown x3
input bool   InpPredShowLabel = true;
// ═══ bull100.set (older build) ═══
input bool   InpUltraFastMode = false;
input double InpFastTrailStartMult = 5.0;
input double InpFastTrailSpreadMult = 3.0;
input double InpMinFastProfitUSD = 0.05;
input int    InpFastCheckMs = 200;
input bool   InpCloseNearProfit = false;
input double InpNearProfitThreshold = 0.85;
input double InpMinProfitProtect = 0.3;
input double InpTrailSpreadMult = 20.0;
input bool   InpUseSlowTrading = true;
input int    InpSLUpdateCooldownMs = 500;
input double InpEstimatedCommissionPerLot = 7.0;
input bool   InpUseSwapInSLCalc = true;
input bool   InpUseCommissionInSLCalc = true;
input bool   InpUseCascade = false;
input double InpCascadeSwapMultiplier = 2.0;
input double InpCascadeBufferMult = 4.0;
input double InpCascadeSpacingMult = 1.5;
input int    InpCascadeCooldownMs = 3000;
input bool   InpCascadeBaseLotOnly = true;
input int    InpSLNoiseBufferBars = 30;
input double InpSLNoiseMult = 2.0;
input double InpSLSpreadMult = 3.0;
// ═══ DISPLAY ═══ (accepted, unused in the tester)
input bool   InpDisplayPositionCount = true;
input bool   InpShowProfitLabels = true;
input color  InpProfitColor = 32768;
input color  InpNextPosition = 32768;

CTrade trade;
ENUM_TIMEFRAMES TF;
int hAtr, hE1, hE4, hED, hAtrD;
double startBalance, peakEquity, lotMult = 1.0;
datetime lastEntry = 0, lastBar = 0, crashUntil = 0, riskUntil = 0, errUntil = 0, ctxUntil = 0, lastCompound = 0;
ulong lastBlastMs = 0;
int crashCalmBars = 0; bool inCrash = false;

struct PState { ulong t; double vsl; double peak; datetime peakT; datetime lockT; ulong slMs; datetime slFailT; };
PState st[];

int Find(ulong t) { for(int i = 0; i < ArraySize(st); i++) if(st[i].t == t) return i; int n = ArraySize(st); ArrayResize(st, n + 1); st[n].t = t; st[n].vsl = 0; st[n].peak = 0; st[n].peakT = 0; st[n].lockT = 0; st[n].slMs = 0; st[n].slFailT = 0; return n; }

int OnInit()
  {
   TF = (ENUM_TIMEFRAMES)InpAiLookbackTF;
   hAtr = iATR(_Symbol, TF, 14);
   hE1 = iMA(_Symbol, PERIOD_H1, InpContextH1EmaPeriod, 0, MODE_EMA, PRICE_CLOSE);
   hE4 = iMA(_Symbol, PERIOD_H4, InpContextH4EmaPeriod, 0, MODE_EMA, PRICE_CLOSE);
   hED = iMA(_Symbol, PERIOD_D1, InpContextD1EmaPeriod, 0, MODE_EMA, PRICE_CLOSE);
   hAtrD = iATR(_Symbol, PERIOD_D1, 14);
   if(hAtr == INVALID_HANDLE || hE1 == INVALID_HANDLE || hE4 == INVALID_HANDLE || hED == INVALID_HANDLE || hAtrD == INVALID_HANDLE) return INIT_FAILED;
   trade.SetExpertMagicNumber(InpMagicNumber);
   startBalance = AccountInfoDouble(ACCOUNT_BALANCE); peakEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   return INIT_SUCCEEDED;
  }

double B(int h, int s) { double v[1]; return CopyBuffer(h, 0, s, 1, v) == 1 ? v[0] : 0; }

// volatility unit in price: average true range of the AI timeframe, smoothed over AiLookbackBars, x sensitivity
double VolUnit()
  {
   double a[]; int n = MathMax(14, MathMin(InpAiLookbackBars, 500));
   if(CopyBuffer(hAtr, 0, 1, n, a) < 1) return 0;
   double s = 0; for(int i = 0; i < ArraySize(a); i++) s += a[i];
   return s / ArraySize(a) * MathMax(InpAiSensitivity, 0.05);
  }

// linear-regression prediction on M1 closes: slope sign and confidence (R^2, decayed weights)
void Predict(double &slope, double &conf)
  {
   slope = 0; conf = 0;
   int n = MathMin(InpPredLookback, 1500);
   double c[]; if(CopyClose(_Symbol, PERIOD_M1, 1, n, c) < 50) return;
   n = ArraySize(c);
   double sw = 0, sx = 0, sy = 0, sxx = 0, sxy = 0, syy = 0, w = 1;
   for(int i = n - 1; i >= 0; i--)          // newest has weight 1, older decay
     {
      double x = i; sw += w; sx += w * x; sy += w * c[i]; sxx += w * x * x; sxy += w * x * c[i]; syy += w * c[i] * c[i];
      w *= InpConfRollingDecay;
     }
   double vx = sxx / sw - (sx / sw) * (sx / sw), vy = syy / sw - (sy / sw) * (sy / sw), cv = sxy / sw - (sx / sw) * (sy / sw);
   if(vx <= 0 || vy <= 0) return;
   slope = cv / vx; conf = cv * cv / (vx * vy);
  }

int CrashScore(double unit)
  {
   int n = InpCrashLookbackBars; MqlRates r[]; ArraySetAsSeries(r, true);
   if(CopyRates(_Symbol, PERIOD_M1, 1, n + 60, r) < n + 60) return 0;
   double avgRange = 0, avgBody = 0; for(int i = n; i < n + 60; i++) { avgRange += r[i].high - r[i].low; avgBody += MathAbs(r[i].close - r[i].open); }
   avgRange /= 60; avgBody /= 60;
   int score = 0;
   double hi = r[0].high; for(int i = 0; i < n; i++) hi = MathMax(hi, r[i].high);
   if(hi - r[0].close > InpCrashVelocityMult * avgRange * MathSqrt(n)) score++;
   int bear = 0; for(int i = 0; i < n && r[i].close < r[i].open; i++) bear++;
   if(bear >= InpCrashConsecBearish) score++;
   if(r[0].open - r[0].close > InpCrashBodyRatioMult * avgBody) score++;
   double spr = SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double avgSpr = 0; for(int i = 0; i < 60; i++) avgSpr += r[i].spread * _Point; avgSpr /= 60;
   if(avgSpr > 0 && spr > InpCrashSpreadMult * avgSpr) score++;
   return score;
  }

bool ContextOk()
  {
   if(!InpUseMarketContext) return true;
   if(TimeCurrent() < ctxUntil) return false;
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   if(peakEquity > 0 && (peakEquity - eq) / peakEquity * 100 > InpContextDrawdownPct) { ctxUntil = TimeCurrent() + InpContextResumeH1Bars * 3600; return false; }
   double d1 = iClose(_Symbol, PERIOD_D1, 1), h4 = iClose(_Symbol, PERIOD_H4, 1), h1 = iClose(_Symbol, PERIOD_H1, 1);
   int bear = (d1 < B(hED, 1)) + (h4 < B(hE4, 1)) + (h1 < B(hE1, 1));
   double atrD = B(hAtrD, 1), todayRange = iHigh(_Symbol, PERIOD_D1, 0) - iLow(_Symbol, PERIOD_D1, 0);
   if(atrD > 0 && todayRange > InpContextRangeRatioMax * atrD) return false;               // abnormal day
   if(bear == 3) return false;                                                              // D1, H4 and H1 all under their EMA
   if(atrD > 0 && (B(hED, 1) - d1) > InpContextTrendRatio * atrD) return false;             // far below the D1 EMA
   return true;
  }

double CostPrice(ulong t, double vol)
  {
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(tv <= 0 || vol <= 0) return 0;
   double money = 0;
   if(InpUseSwapInSLCalc) money += -MathMin(0.0, PositionGetDouble(POSITION_SWAP));
   if(InpUseCommissionInSLCalc) money += InpEstimatedCommissionPerLot * vol;
   return money / (tv / ts * vol);
  }

double MoneyToPrice(double money, double vol)
  {
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   return (tv <= 0 || vol <= 0) ? 0 : money / (tv / ts * vol);
  }

void OnTick()
  {
   datetime now = TimeCurrent(); ulong ms = GetTickCount64();
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), spread = ask - bid;
   double unit = InpUseDynamicValues ? VolUnit() : 0;
   if(InpUseDynamicValues && unit <= 0) return;
   double eq = AccountInfoDouble(ACCOUNT_EQUITY); peakEquity = MathMax(peakEquity, eq);
   double ml = AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);

   // trailing distances
   double tStart = InpTrailStartPoints * _Point, tDist = InpTrailDistPoints * _Point;
   if(InpTrailMode == 1) { tStart = InpTrailStartMult * unit; tDist = InpTrailDistMult * unit; }
   if(InpTrailMode == 2) { tStart = MathMax(tStart, InpTrailStartMult * unit); tDist = MathMax(tDist, InpTrailDistMult * unit); }
   if(InpUltraFastMode) { tStart = InpFastTrailStartMult * spread; tDist = InpFastTrailSpreadMult * spread; }

   // max drawdown
   if(InpCloseAllOnMaxDrawdown && peakEquity > 0 && (peakEquity - eq) / peakEquity * 100 >= InpMaxDrawdownPercent) { CloseAll(); return; }
   // emergency margin
   if(InpUseMarginProtection && InpAllowEmergencyMarginClose && ml > 0)
     {
      double so = AccountInfoDouble(ACCOUNT_MARGIN_SO_SO);
      if(ml < so * InpMarginCriticalMultiplier) CloseWorst();
     }

   // manage positions
   int n = 0; double lots = 0, lowest = DBL_MAX, highest = 0; datetime newestT = 0; double newestOp = 0; bool newestTrail = false;
   double worstLoss = 0; ulong worstT = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(!PositionSelectByTicket(t) || PositionGetInteger(POSITION_MAGIC) != InpMagicNumber) continue;
      n++;
      double vol = PositionGetDouble(POSITION_VOLUME), op = PositionGetDouble(POSITION_PRICE_OPEN), sl = PositionGetDouble(POSITION_SL);
      double pr = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP) - InpEstimatedCommissionPerLot * vol;
      lots += vol; lowest = MathMin(lowest, op); highest = MathMax(highest, op);
      if(pr < worstLoss) { worstLoss = pr; worstT = t; }
      int k = Find(t);
      double per001 = vol / 0.01;
      double cost = CostPrice(t, vol);
      double be = op + cost;                                    // break-even incl. costs
      // peak tracking for the fallback
      if(pr > st[k].peak) { st[k].peak = pr; st[k].peakT = now; }
      bool trailing = st[k].vsl > 0;
      double dist = tDist;
      if(InpUseMomentumRide && bid - op > InpMomentumActivateMult * MathMax(tStart, _Point)) dist *= 1.5;
      // secure profit lock
      if(InpUseSecureProfit && !trailing && pr >= InpLockActivateProfit * per001)
        {
         if(st[k].lockT == 0) st[k].lockT = now;
         double lk = op + cost + MoneyToPrice(InpSecureNetProfit * per001, vol);
         if(now - st[k].lockT >= InpLockConfirmSeconds && lk <= bid - dist)   // v2: not closer than the trailing distance
            st[k].vsl = MathMax(st[k].vsl, lk);
        }
      else if(!trailing) st[k].lockT = 0;
      // trailing
      if(bid >= be + tStart && pr >= InpTrailNetProfit * per001 * (InpUltraFastMode ? 0 : 1) + (InpUltraFastMode ? InpMinFastProfitUSD * per001 : 0))
        {
         double nv = bid - dist;
         if(nv > st[k].vsl + InpMinSLChangeMult * dist * (InpUseSlowTrading ? 1 : 0.2) && nv >= be) st[k].vsl = nv;
        }
      trailing = st[k].vsl > 0;
      // virtual stop hit -> close
      if(trailing && bid <= st[k].vsl) { trade.PositionClose(t); continue; }
      // fallback (v2): only when the broker refused the SL move for FallbackSeconds and the profit has
      // fallen FallbackPercent below its peak - a backup for "invalid stops", not an exit rule of its own
      if(InpUseTrailingFallback && trailing && st[k].slFailT > 0 && now - st[k].slFailT >= InpFallbackSeconds
         && st[k].peak > 0 && pr < st[k].peak * (1 - InpFallbackPercent / 100) && pr > 0)
        { trade.PositionClose(t); continue; }
      if(InpCloseNearProfit && trailing && st[k].peak > 0 && pr < st[k].peak * InpNearProfitThreshold && pr > 0) { trade.PositionClose(t); continue; }
      // real broker SL: the virtual one itself, or (phantom) further away
      if(trailing)
        {
         double real = InpUsePhantomChain ? st[k].vsl - InpSLTriggerDistance * dist : st[k].vsl;
         real = NormalizeDouble(real, _Digits);
         int lvl = (int)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
         if(real > sl + _Point && bid - real > lvl * _Point && ms - st[k].slMs >= (ulong)InpSLUpdateCooldownMs)
           { if(trade.PositionModify(t, real, 0)) { st[k].slMs = ms; st[k].slFailT = 0; } else if(st[k].slFailT == 0) st[k].slFailT = now; }
        }
      datetime ot = (datetime)PositionGetInteger(POSITION_TIME);
      if(ot >= newestT) { newestT = ot; newestOp = op; newestTrail = trailing; }
     }
   // risk limit: close the worst position when its loss is too deep
   if(InpUseRiskLimit && worstT > 0 && unit > 0)
     {
      if(PositionSelectByTicket(worstT))
        {
         double op = PositionGetDouble(POSITION_PRICE_OPEN);
         if(op - bid > InpRiskMult * unit) { trade.PositionClose(worstT); if(InpUseRiskDelay) riskUntil = now + InpRiskDelaySeconds; }
        }
     }

   // ---- entries ----
   if(now < errUntil || now < riskUntil) return;
   // crash detection
   if(InpUseCrashDetection)
     {
      datetime m1 = iTime(_Symbol, PERIOD_M1, 0);
      static datetime lastM1 = 0;
      if(m1 != lastM1)
        {
         lastM1 = m1;
         if(CrashScore(unit) >= InpCrashMinScore) { inCrash = true; crashCalmBars = 0; crashUntil = now + InpCrashCooldownSeconds; }
         else if(inCrash) { if(iClose(_Symbol, PERIOD_M1, 1) >= iOpen(_Symbol, PERIOD_M1, 1)) crashCalmBars++; else crashCalmBars = 0; if(crashCalmBars >= InpStabilizeConfirmBars) inCrash = false; }
        }
      if(inCrash || now < crashUntil) return;
     }
   if(!ContextOk()) return;
   double slope = 0, conf = 0; bool bearPred = false, bullPred = false;
   if(InpUsePrediction) { Predict(slope, conf); bearPred = slope < 0 && conf >= InpPredConfidenceMin; bullPred = slope > 0 && conf >= InpPredConfidenceMin; }
   int cd = InpCooldownSeconds * ((InpUseDynamicCooldown && bearPred) ? 3 : 1);
   if(now - lastEntry < cd) return;
   if(n >= InpMaxPositions) return;
   if(InpUseMarginLimit && ml > 0 && ml < 1000) return;

   // compounding
   if(InpUseLogCompounding && now - lastCompound >= InpCompoundWindowMin * 60)
     {
      lastCompound = now;
      double gain = AccountInfoDouble(ACCOUNT_BALANCE) / startBalance;
      lotMult = MathMin(InpCompoundMaxLotMult, MathMax(1.0, 1.0 + InpCompoundReinvestRatio * MathLog(MathMax(gain, 1e-9)) * 2.0));
     }
   double lot = InpLotSize * lotMult;

   string why = "";
   double minGap = InpMinimumSpacingMult * unit;
   if(n == 0)
     {
      if(!InpOpenInitialBuy) return;
      if(InpUseNewHighFilter)
        {
         double hh = iHigh(_Symbol, PERIOD_H1, iHighest(_Symbol, PERIOD_H1, MODE_HIGH, InpHighLookbackHours, 1));
         if(ask >= hh) return;
        }
      why = "init";
     }
   else
     {
      // DCA lower
      double step = MathMax(InpMinimumSpaceMultiplier * unit, InpSpreadValueMult * spread);
      int below = 0; for(int i = PositionsTotal() - 1; i >= 0; i--) { ulong t = PositionGetTicket(i); if(PositionSelectByTicket(t) && PositionGetInteger(POSITION_MAGIC) == InpMagicNumber && PositionGetDouble(POSITION_PRICE_OPEN) > ask) below++; }
      step *= MathPow(1 + InpDcaProgressiveStepPct / 100, MathMax(0, below - 1));
      if(InpUseCascade) step *= InpCascadeSpacingMult;
      if(bearPred) step *= 1 + InpPredDcaAdjustPct;
      if(ask <= lowest - step)
        {
         bool ok = true;
         if(InpUseDcaMagnetizer) ok = iClose(_Symbol, PERIOD_M1, 1) > iOpen(_Symbol, PERIOD_M1, 1);
         if(ok)
           {
            why = "dca";
            if(InpUseAggressiveOpenPrice) lot *= MathPow(2, below);
            else if(InpUseIncrementalLotOpenPrice) lot *= (1 + below);
           }
        }
      // chain: stack above while the newest trails
      if(why == "" && newestTrail && !(InpBlockChainOnBearPred && bearPred))
        {
         double cs = MathMax(InpUseFixedChainSpacing ? InpChainSpacingPoints * _Point : minGap, tStart);   // v2
         if(ask >= newestOp + cs) why = "chain";
        }
      // pace keeper
      if(why == "" && InpUsePaceKeeper && newestTrail && now - lastEntry >= InpPaceTargetSeconds && !(InpBlockChainOnBearPred && bearPred) && ask - newestOp >= MathMax(minGap, tStart)) why = "pace";   // v2
      // every candle
      // v2: "every candle" adds only below the whole ladder (a mini-DCA once per bar), never above
      if(why == "" && InpUseEveryCandle && !bearPred)
        {
         datetime bt = iTime(_Symbol, TF, 0);
         if(bt != lastBar && (now - lastEntry) >= InpActivityCooldownBars * PeriodSeconds(TF) && ask <= lowest - MathMax(minGap, tDist)) why = "candle";
        }
      // coherence burst
      if(why == "" && InpUseCoherenceBurst && ms - lastBlastMs >= (ulong)InpCoherenceBlastCooldownMs && (ml == 0 || ml >= InpCoherenceBlastMinMarginLevel))
        {
         int up = (iClose(_Symbol, PERIOD_M1, 1) > iOpen(_Symbol, PERIOD_M1, 1)) + (iClose(_Symbol, PERIOD_M5, 1) > iOpen(_Symbol, PERIOD_M5, 1)) + (iClose(_Symbol, PERIOD_M15, 1) > iOpen(_Symbol, PERIOD_M15, 1));
         if(up / 3.0 >= InpCoherenceMinStrength + 0.34 && MathAbs(ask - newestOp) >= MathMax(minGap, InpCoherenceExtraDistPct / 100 * ask)) { why = "burst"; lastBlastMs = ms; }
        }
     }
   if(why == "") return;
   if(InpUseTrendBurst && bullPred && conf >= InpTrendBurstMinConfidence && (ml == 0 || ml >= InpTrendBurstMinMarginLevel) && why != "dca") lot *= InpTrendBurstMultiplier;
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), vstep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   lot = MathMax(vmin, MathRound(lot / vstep) * vstep);
   // margin safety
   if(InpUseMarginProtection)
     {
      double need = 0;
      if(!OrderCalcMargin(ORDER_TYPE_BUY, _Symbol, lot, ask, need) || AccountInfoDouble(ACCOUNT_MARGIN_FREE) < need * InpMarginSafetyMultiplier) return;
     }
   if(trade.Buy(lot, _Symbol, 0, 0, 0, why)) { lastEntry = now; lastBar = iTime(_Symbol, TF, 0); }
   else errUntil = now + InpErrorWaitColddown;
  }

void CloseAll()
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--) { ulong t = PositionGetTicket(i); if(PositionSelectByTicket(t) && PositionGetInteger(POSITION_MAGIC) == InpMagicNumber) trade.PositionClose(t); }
  }

void CloseWorst()
  {
   double w = 0; ulong wt = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--) { ulong t = PositionGetTicket(i); if(PositionSelectByTicket(t) && PositionGetInteger(POSITION_MAGIC) == InpMagicNumber && PositionGetDouble(POSITION_PROFIT) < w) { w = PositionGetDouble(POSITION_PROFIT); wt = t; } }
   if(wt > 0) trade.PositionClose(wt);
  }
