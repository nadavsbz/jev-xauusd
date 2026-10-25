"""Builds the crash-day variants DragonClone_v4*.mq5 from the frozen v3 (docs/BD_V4_PLAN.md).
Every variant = v3 + one mechanism behind its own inputs; with the default inputs it trades exactly like v3.
Hooks: V4Lot (lot of an add), V4AddOk (allow an add), V4Dist (grid distance), V4OnOverlap, V4Reset (basket gone), V4EntryOk (new basket)."""
import re

SRC = "mql5/DragonClone_v3.mq5"

IDENT = {
 "lot": "double V4Lot(int side, Bsk &b, double lot) { return lot; }",
 "add": "bool V4AddOk(int side, Bsk &b, double lot) { return true; }",
 "dist": "double V4Dist(int lvl) { return DistFor(lvl); }",
 "ov": "void V4OnOverlap(int side, Bsk &b) { }",
 "reset": "void V4Reset(int side) { }",
 "entry": "bool V4EntryOk() { return true; }",
}

VARIANTS = {
 "v4a": ("lot step-down after Overlap (user idea, 30.7.2026)",
  ["input int    LotAfterOverlap = 0;     // v4a: after an Overlap close cap the next lots: 1 = the closed oldest lot, 2 = the closed newest lot, 3 = closed newest / Martin_"],
  "double ovNewV[2], ovOldV[2]; int ovCnt[2];",
  {"lot": """double V4Lot(int side, Bsk &b, double lot)
  {
   if(LotAfterOverlap <= 0 || ovCnt[side] == 0) return lot;
   double cap = LotAfterOverlap == 1 ? ovOldV[side] : LotAfterOverlap == 2 ? ovNewV[side] : ovNewV[side] / Martin_;
   cap = MathMax(NormalizeDouble(cap, 2), SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN));
   return MathMin(lot, cap);
  }""",
   "ov": "void V4OnOverlap(int side, Bsk &b) { ovNewV[side] = b.newestV; ovOldV[side] = b.oldestV; ovCnt[side]++; }",
   "reset": "void V4Reset(int side) { ovNewV[side] = 0; ovOldV[side] = 0; ovCnt[side] = 0; }"}),
 "v4b": ("exposure cap: side lots per 100k equity",
  ["input double ExpoLotsPer100k = 0;     // v4b: no add that takes the side above this many lots per 100,000 of equity (0 = off)"],
  "", {"add": """bool V4AddOk(int side, Bsk &b, double lot)
  {
   if(ExpoLotsPer100k <= 0) return true;
   return b.vol + lot <= ExpoLotsPer100k * AccountInfoDouble(ACCOUNT_EQUITY) / 100000.0;
  }"""}),
 "v4c": ("news-time pause (14:30 server = 8:30 New York)",
  ["input int    NewsPauseFrom = 0;       // v4c: server time HHMM where the pause starts on weekdays (0 = off)",
   "input int    NewsPauseMin = 0;        // v4c: pause length in minutes: no new baskets and no adds"],
  "", {"add": "bool V4AddOk(int side, Bsk &b, double lot) { return !InNewsPause(); }",
       "entry": "bool V4EntryOk() { return !InNewsPause(); }",
       "extra": """bool InNewsPause()
  {
   if(NewsPauseFrom <= 0 || NewsPauseMin <= 0) return false;
   MqlDateTime t; TimeToStruct(TimeCurrent(), t);
   if(t.day_of_week == 0 || t.day_of_week == 6) return false;
   int m = t.hour * 60 + t.min, s = (NewsPauseFrom / 100) * 60 + NewsPauseFrom % 100;
   return m >= s && m < s + NewsPauseMin;
  }"""}),
 "v4d": ("ATR-scaled grid distance",
  ["input double AtrDistMult = 0;         // v4d: grid distance = max(BD distance, this x ATR(M15)) (0 = off)",
   "input int    AtrPeriod = 14;"],
  "int hAtr = INVALID_HANDLE;",
  {"dist": """double V4Dist(int lvl)
  {
   double bd = DistFor(lvl);
   if(AtrDistMult <= 0) return bd;
   if(hAtr == INVALID_HANDLE) hAtr = iATR(_Symbol, PERIOD_M15, AtrPeriod);
   double a = B(hAtr, 1);
   return a > 0 ? MathMax(bd, AtrDistMult * a) : bd;
  }"""}),
 "v4e": ("stop adding after N Overlap closes in a basket",
  ["input int    MaxOverlaps = 0;         // v4e: after this many Overlap closes in a basket, no more adds until it closes (0 = off)"],
  "int ovCnt[2];",
  {"add": "bool V4AddOk(int side, Bsk &b, double lot) { return MaxOverlaps <= 0 || ovCnt[side] < MaxOverlaps; }",
   "ov": "void V4OnOverlap(int side, Bsk &b) { ovCnt[side]++; }",
   "reset": "void V4Reset(int side) { ovCnt[side] = 0; }"}),
}
# combinations: inputs, globals and hooks of two variants together (hooks must not overlap)
def combo(name, *parts):
    ins, gl, fn, ds = [], [], {}, []
    for p in parts:
        d, i, g, f = VARIANTS[p]; ins += i; gl.append(g); ds.append(d)
        for k, v in f.items():
            assert k not in fn, (name, k); fn[k] = v
    VARIANTS[name] = (" + ".join(ds), ins, chr(10).join(x for x in gl if x), fn)
combo("v4cd", "v4c", "v4d")

def sub1(s, a, b):
    assert s.count(a) == 1, a
    return s.replace(a, b)

def build(name, desc, inputs, globs, funcs):
    s = open(SRC, encoding="utf-8").read()
    s = re.sub(r"//\| FROZEN v3.*?\n(//\|.*?\n){3}", "", s, count=1)
    s = s.replace("//| DragonClone: a rebuild", f"//| DragonClone_{name}: frozen v3 + {desc}. Default inputs = v3.\n//| DragonClone: a rebuild", 1)
    s = sub1(s, "input bool   OverlapAtCount = true;", "input bool   OverlapAtCount = true;\ninput string qw8 = \"//--- " + name + " (ours) ---//\";\n" + "\n".join(inputs))
    s = sub1(s, "datetime lastBar = 0, crashUntil = 0, lastAddBar[2] = {0, 0};", "datetime lastBar = 0, crashUntil = 0, lastAddBar[2] = {0, 0};\n" + globs)
    f = dict(IDENT, **funcs)
    block = "// ---- " + name + " hooks ----\n" + "\n\n".join(f[k] for k in ["lot", "add", "dist", "ov", "reset", "entry"]) + "\n" + (f.get("extra", "") + "\n" if "extra" in f else "") + "\n"
    if "extra" in f:   # helpers must come before the hooks that call them
        block = "// ---- " + name + " hooks ----\n" + f["extra"] + "\n\n" + "\n\n".join(f[k] for k in ["lot", "add", "dist", "ov", "reset", "entry"]) + "\n\n"
    s = sub1(s, "void OnTick()", block + "void OnTick()")
    s = sub1(s, "if(b.n == 0) { trailOn[side] = false; hiWater[side] = 0; continue; }", "if(b.n == 0) { trailOn[side] = false; hiWater[side] = 0; V4Reset(side); continue; }")
    s = sub1(s, "if(OverlapResetsTrail) ClearTrail(side);", "if(OverlapResetsTrail) ClearTrail(side);\n            V4OnOverlap(side, b);")
    s = sub1(s, "double d = DistFor(lvl);", "double d = V4Dist(lvl);")
    s = sub1(s, "double lot = LotFromOldest ? OldestLot(b.oldestV, b.n) : LotFromNewest ? NextLot(b.newestV) : LotFor(lvl);",
             "double lot = LotFromOldest ? OldestLot(b.oldestV, b.n) : LotFromNewest ? NextLot(b.newestV) : LotFor(lvl);\n            lot = V4Lot(side, b, lot);\n            if(!V4AddOk(side, b, lot)) continue;")
    s = sub1(s, "if(!NewCycle_ || crash) return;", "if(!NewCycle_ || crash) return;\n   if(!V4EntryOk()) return;")
    open(f"mql5/DragonClone_{name}.mq5", "w", encoding="utf-8").write(s)

if __name__ == "__main__":
    for n, v in VARIANTS.items(): build(n, *v); print(n)
