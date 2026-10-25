"""Builds the smart-cut variants DragonClone_v5*.mq5 from the frozen v3 (docs/BD_V5_PLAN.md).
v3 cuts a basket only through G_BasketStopPct (a fixed loss). Each v5 file adds one cut/hold rule behind its own inputs;
with default inputs it trades exactly like v3. Losses are measured in % of BALANCE (not equity, which falls with the loss).
Hooks: V5Guard (per side, every tick, after Scan; returns true when it closed something) and V5AddOk (allow an add)."""
SRC = "mql5/DragonClone_v3.mq5"

COMMON = """double LossPct(Bsk &b) { return b.profit < 0 ? -b.profit / AccountInfoDouble(ACCOUNT_BALANCE) * 100 : 0; }

void CloseOldest(int side, double volTarget)   // close the oldest positions of the side until volTarget lots are closed
  {
   double done = 0;
   while(done < volTarget - 1e-9)
     {
      ulong best = 0; datetime bt = D'2100.01.01'; double bv = 0;
      for(int i = PositionsTotal() - 1; i >= 0; i--)
        {
         ulong t = PositionGetTicket(i);
         if(!PositionSelectByTicket(t) || PositionGetInteger(POSITION_MAGIC) != Magic || PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
         int s = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 0 : 1;
         datetime ot = (datetime)PositionGetInteger(POSITION_TIME);
         if(s == side && ot < bt) { bt = ot; best = t; bv = PositionGetDouble(POSITION_VOLUME); }
        }
      if(best == 0 || !trade.PositionClose(best) || trade.ResultRetcode() != TRADE_RETCODE_DONE) break;
      done += bv;
     }
  }
"""

VARIANTS = {
 "v5a": ("rescue on correction (user idea 21.10.2026)",
  ["input double R_Arm = 0;               // v5a: arm when the basket loss reaches this % of balance (0 = off)",
   "input double R_Exit = 3;              // v5a: once armed, close the whole basket when the loss recovers to this %"],
  "bool rArmed[2];",
  """bool V5Guard(int side, Bsk &b)
  {
   if(R_Arm <= 0) return false;
   double l = LossPct(b);
   if(l >= R_Arm) rArmed[side] = true;
   if(rArmed[side] && l <= R_Exit) { CloseSide(side); rArmed[side] = false; return true; }
   return false;
  }
void V5Reset(int side) { rArmed[side] = false; }""", None),
 "v5b": ("partial cut: close the oldest positions at a loss level",
  ["input double P_At = 0;                // v5b: at this loss % of balance close the oldest positions (0 = off)",
   "input double P_Frac = 0.5;            // v5b: share of the side's volume to close, once per basket"],
  "bool pDone[2];",
  """bool V5Guard(int side, Bsk &b)
  {
   if(P_At <= 0 || pDone[side] || LossPct(b) < P_At) return false;
   pDone[side] = true; CloseOldest(side, P_Frac * b.vol); return true;
  }
void V5Reset(int side) { pDone[side] = false; }""", None),
 "v5c": ("freeze: no adds beyond a loss level",
  ["input double F_Freeze = 0;            // v5c: no new levels while the basket loss is above this % of balance (0 = off)"],
  "", "bool V5Guard(int side, Bsk &b) { return false; }\nvoid V5Reset(int side) { }",
  "bool V5AddOk(int side, Bsk &b) { return F_Freeze <= 0 || LossPct(b) < F_Freeze; }"),
 "v5d": ("time cut: an old basket in loss is closed",
  ["input double T_Hours = 0;             // v5d: basket age in hours (oldest open order) (0 = off)",
   "input double T_Loss = 5;              // v5d: ...and loss at least this % of balance -> close the basket"],
  "", """bool V5Guard(int side, Bsk &b)
  {
   if(T_Hours <= 0 || TimeCurrent() - b.oldestT < T_Hours * 3600 || LossPct(b) < T_Loss) return false;
   CloseSide(side); return true;
  }
void V5Reset(int side) { }""", None),
}

def sub1(s, a, b):
    assert s.count(a) == 1, a
    return s.replace(a, b)

def build(name, desc, inputs, globs, guard, addok):
    s = open(SRC, encoding="utf-8").read()
    s = s.replace("//| FROZEN v3", f"//| DragonClone_{name}: frozen v3 + {desc}. Default inputs = v3.\n//| was FROZEN v3", 1)
    s = sub1(s, "input bool   OverlapAtCount = true;", "input bool   OverlapAtCount = true;\ninput string qw9 = \"//--- " + name + " (ours) ---//\";\n" + "\n".join(inputs))
    s = sub1(s, "datetime lastBar = 0, crashUntil = 0, lastAddBar[2] = {0, 0};", "datetime lastBar = 0, crashUntil = 0, lastAddBar[2] = {0, 0};\n" + globs)
    add = addok or "bool V5AddOk(int side, Bsk &b) { return true; }"
    s = sub1(s, "void OnTick()", "// ---- " + name + " hooks ----\n" + COMMON + "\n" + guard + "\n" + add + "\n\nvoid OnTick()")
    s = sub1(s, "if(b.n == 0) { trailOn[side] = false; hiWater[side] = 0; continue; }", "if(b.n == 0) { trailOn[side] = false; hiWater[side] = 0; V5Reset(side); continue; }")
    s = sub1(s, "AccountInfoDouble(ACCOUNT_EQUITY)) { CloseSide(side); continue; }", "AccountInfoDouble(ACCOUNT_EQUITY)) { CloseSide(side); continue; }\n      if(V5Guard(side, b)) continue;")
    s = sub1(s, "double lot = LotFromOldest ? OldestLot(b.oldestV, b.n) : LotFromNewest ? NextLot(b.newestV) : LotFor(lvl);",
             "double lot = LotFromOldest ? OldestLot(b.oldestV, b.n) : LotFromNewest ? NextLot(b.newestV) : LotFor(lvl);\n            if(!V5AddOk(side, b)) continue;")
    open(f"mql5/DragonClone_{name}.mq5", "w", encoding="utf-8").write(s)

if __name__ == "__main__":
    for n, v in VARIANTS.items(): build(n, *v); print(n)
