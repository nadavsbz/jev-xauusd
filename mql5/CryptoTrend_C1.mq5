//+------------------------------------------------------------------+
//| CryptoTrend_C1 - candidate C1 of docs/STABLE_SYSTEM_PLAN.md       |
//| Donchian ensemble trend on H6 bars, several crypto symbols.       |
//| Mirrors research/stable/intraday_trend.py (BAR=6, TARGET=0.20):   |
//|  per symbol and lookback N in {10,20,30,60,90,150,250}: enter at  |
//|  the N-bar closing high (low for shorts), exit at the N/2-bar     |
//|  opposite closing extreme; state = mean over the 7 lookbacks.     |
//|  Two components: long-only and long-short. Asset weight = state x |
//|  AssetVol / 60-bar realized vol (cap 3) / n symbols. Each         |
//|  component is scaled to TargetVol by its own trailing vol (one    |
//|  quarter of bars, cap 3, lagged). Target = 0.5 L + 0.5 LS, as a   |
//|  fraction of equity in notional. Everything is recomputed from    |
//|  closed bars at every new H6 bar (restart-safe, no stored state). |
//| No grid, no martingale, no averaging down.                        |
//+------------------------------------------------------------------+
#property strict
#include <Trade\Trade.mqh>

input string Symbols    = "BTCUSD,ETHUSD,XRPUSD,SOLUSD";
input double TargetVol  = 0.20;   // annual vol target of each component
input double AssetVol   = 0.10;   // per-asset vol unit
input double MaxGross   = 3.0;    // hard cap: total notional / equity
input double RebalPct   = 0.15;   // trade only when |target - current| > this x |target| (and >= one lot step)
input int    History    = 1600;   // H6 bars replayed each rebalance (>= 250 + 365 + 60)
input int    MinBars    = 320;    // a symbol trades only with at least this many closed H6 bars (250 lookback + 60 vol + margin)
input int    DelayBars  = 0;      // 0: trade at the first tick after the signal bar closes; 1: one H6 bar later (research LAG=2)
input long   Magic      = 61001;

CTrade trade;
string sy[]; int ns = 0;
datetime lastBar = 0;
const int LB[7] = {10, 20, 30, 60, 90, 150, 250};
const double PER_YEAR = 365.0 * 24.0 / 6.0;

int OnInit()
  {
   ns = StringSplit(Symbols, ',', sy);
   for(int i = 0; i < ns; i++) { StringTrimLeft(sy[i]); StringTrimRight(sy[i]); SymbolSelect(sy[i], true); }
   trade.SetExpertMagicNumber(Magic);
   return(ns > 0 ? INIT_SUCCEEDED : INIT_PARAMETERS_INCORRECT);
  }

// state series of one symbol: closes c[0..n-1] oldest first -> st[] mean state per bar
void States(const double &c[], int n, bool longOnly, double &st[])
  {
   ArrayResize(st, n); ArrayInitialize(st, 0);
   for(int k = 0; k < 7; k++)
     {
      int N = LB[k], H = N / 2; double q = 0;
      for(int i = 0; i < n; i++)
        {
         if(i >= N - 1)
           {
            double hi = c[i], lo = c[i], xl = c[i], xh = c[i];
            for(int j = i - N + 1; j <= i; j++) { hi = MathMax(hi, c[j]); lo = MathMin(lo, c[j]); }
            for(int j = i - H + 1; j <= i; j++) { xl = MathMin(xl, c[j]); xh = MathMax(xh, c[j]); }
            if(q == 0) q = (c[i] >= hi) ? 1 : ((!longOnly && c[i] <= lo) ? -1 : 0);
            else if(q > 0 && c[i] <= xl) q = 0;
            else if(q < 0 && c[i] >= xh) q = 0;
           }
         st[i] += q / 7.0;
        }
     }
  }

double StdLast(const double &x[], int end, int len)   // std of x[end-len+1..end]
  {
   if(end - len + 1 < 1) return 0;
   double s = 0, s2 = 0;
   for(int i = end - len + 1; i <= end; i++) { s += x[i]; s2 += x[i] * x[i]; }
   double m = s / len; return MathSqrt(MathMax(0, s2 / len - m * m) * len / (len - 1));
  }

// target notional fraction of equity per symbol, from closed H6 bars
bool Targets(double &tgt[])
  {
   ArrayResize(tgt, ns); ArrayInitialize(tgt, 0);
   int n = History;
   double C[]; ArrayResize(C, ns * n); ArrayInitialize(C, 0);
   int off[]; ArrayResize(off, ns); int ok = 0;
   for(int s = 0; s < ns; s++)
     {
      // closed bars only, oldest first; a symbol with a shorter history (a new coin) is aligned at the newest bar and
      // stays flat until it has MinBars (it does not block the others, as in the research where it is NaN -> 0)
      double c[]; ArraySetAsSeries(c, false);
      // Codex PR 44 P2: history still loading is not a short history - retry instead of flattening the symbol
      if(!SeriesInfoInteger(sy[s], PERIOD_H6, SERIES_SYNCHRONIZED)) return false;
      int m = CopyClose(sy[s], PERIOD_H6, 1, n, c);
      if(m < 0 || (m < n && Bars(sy[s], PERIOD_H6) - 1 > m)) return false;
      if(m < MinBars) { off[s] = n; continue; }
      off[s] = n - m; ok++;
      for(int i = 0; i < m; i++) C[s * n + off[s] + i] = c[i];
     }
   if(ok == 0) return false;
   double wL[], wS[]; ArrayResize(wL, ns * n); ArrayResize(wS, ns * n); ArrayInitialize(wL, 0); ArrayInitialize(wS, 0);
   double rL[], rS[]; ArrayResize(rL, n); ArrayResize(rS, n); ArrayInitialize(rL, 0); ArrayInitialize(rS, 0);
   for(int s = 0; s < ns; s++)
     {
      int o = off[s], m = n - o; if(m <= 0) continue;
      double c[]; ArrayResize(c, m); for(int i = 0; i < m; i++) c[i] = C[s * n + o + i];
      double stL[], stS[]; States(c, m, true, stL); States(c, m, false, stS);
      double r[]; ArrayResize(r, m); r[0] = 0; for(int i = 1; i < m; i++) r[i] = c[i - 1] > 0 ? c[i] / c[i - 1] - 1 : 0;
      for(int i = 60; i < m; i++)
        {
         double v = StdLast(r, i, 60) * MathSqrt(PER_YEAR);
         double sz = v > 0 ? MathMin(3.0, AssetVol / v) / ns : 0;
         wL[s * n + o + i] = stL[i] * sz; wS[s * n + o + i] = stS[i] * sz;
         int h = i - 1 - DelayBars;   // Codex PR 44 P1: the weight decided at close h is held over bar i
         if(h >= 0) { rL[o + i] += wL[s * n + o + h] * r[i]; rS[o + i] += wS[s * n + o + h] * r[i]; }
        }
     }
   int q = (int)(PER_YEAR / 4);
   int t = n - 1 - DelayBars;   // the weight executed now was decided at close t (with the vol known at t)
   double vL = StdLast(rL, t, q) * MathSqrt(PER_YEAR), vS = StdLast(rS, t, q) * MathSqrt(PER_YEAR);
   double kL = vL > 0 ? MathMin(3.0, TargetVol / vL) : 0, kS = vS > 0 ? MathMin(3.0, TargetVol / vS) : 0;
   double gross = 0;
   for(int s = 0; s < ns; s++) { tgt[s] = 0.5 * kL * wL[s * n + t] + 0.5 * kS * wS[s * n + t]; gross += MathAbs(tgt[s]); }
   if(gross > MaxGross) for(int s = 0; s < ns; s++) tgt[s] *= MaxGross / gross;
   return true;
  }

double NetLots(string s)
  {
   double v = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(!PositionSelectByTicket(t) || PositionGetInteger(POSITION_MAGIC) != Magic || PositionGetString(POSITION_SYMBOL) != s) continue;
      v += (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 1 : -1) * PositionGetDouble(POSITION_VOLUME);
     }
   return v;
  }

// bring the net position of s to want lots: close opposite positions first (hedging accounts), then open the rest.
// Codex PR 44 P1: every close is checked by its retcode and the rest is recomputed from the positions actually open;
// returns false when a request failed, so OnTick retries on the next tick instead of waiting six hours
bool ok_(void) { uint rc = trade.ResultRetcode(); return rc == TRADE_RETCODE_DONE || rc == TRADE_RETCODE_DONE_PARTIAL || rc == TRADE_RETCODE_PLACED; }
bool Move(string s, double want)
  {
   double step = SymbolInfoDouble(s, SYMBOL_VOLUME_STEP), vmin = SymbolInfoDouble(s, SYMBOL_VOLUME_MIN);
   double d = want - NetLots(s);
   for(int i = PositionsTotal() - 1; i >= 0 && MathAbs(d) >= step; i--)
     {
      ulong t = PositionGetTicket(i);
      if(!PositionSelectByTicket(t) || PositionGetInteger(POSITION_MAGIC) != Magic || PositionGetString(POSITION_SYMBOL) != s) continue;
      bool buy = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY;
      if((d > 0) == buy) continue;
      double v = PositionGetDouble(POSITION_VOLUME), c = MathMin(v, MathAbs(d));
      c = MathFloor(c / step + 1e-9) * step; if(c < step) continue;
      bool sent = c >= v - step / 2 ? trade.PositionClose(t) : trade.PositionClosePartial(t, c);
      if(!sent || !ok_()) return false;
      d = want - NetLots(s);
     }
   d = want - NetLots(s);
   double o = MathFloor(MathAbs(d) / step + 1e-9) * step;
   if(o < vmin) return true;
   bool sent = d > 0 ? trade.Buy(o, s) : trade.Sell(o, s);
   return sent && ok_();
  }

void OnTick()
  {
   datetime b = iTime(sy[0], PERIOD_H6, 0);
   if(b == 0 || b == lastBar) return;
   double tgt[]; if(!Targets(tgt)) return;   // history not ready: retry on the next tick
   double eq = AccountInfoDouble(ACCOUNT_EQUITY); bool all = true;
   for(int s = 0; s < ns; s++)
     {
      double px = SymbolInfoDouble(sy[s], SYMBOL_BID), cs = SymbolInfoDouble(sy[s], SYMBOL_TRADE_CONTRACT_SIZE);
      if(px <= 0 || cs <= 0) continue;
      double want = tgt[s] * eq / (px * cs), have = NetLots(sy[s]), step = SymbolInfoDouble(sy[s], SYMBOL_VOLUME_STEP);
      if(MathAbs(want - have) < step) continue;
      if(want != 0 && MathAbs(want - have) < RebalPct * MathAbs(want) && (want > 0) == (have > 0) && have != 0) continue;
      if(!Move(sy[s], want)) all = false;
     }
   if(all) lastBar = b;   // a failed request is retried on the next tick
  }
//+------------------------------------------------------------------+
