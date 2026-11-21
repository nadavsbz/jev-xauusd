"""Builds DragonClone_v16.mq5 = v15 + an add-rate throttle (GPT t284 rule 1, 17.11.2026, after the live BD ladder of 17.11:
lots x1.5 every ~$3, 0.26 -> 1.97 in 3 hours). With ThrottleAdds = 0 (default) it trades exactly like v15 (= v7 with flags off).
  ThrottleAdds    after this many grid ADDS (the basket's first order is not an add) filled within ThrottleWinMin minutes,
                  no new level on that side for ThrottleCoolMin minutes from the last of them; after that, one add at a time,
                  each followed by a new ThrottleCoolMin pause. Resets when the side's basket is back to one order (a new basket).
                  No forced close, no TP change, no hedge.
Usage: python research/bd1/make_v16.py   (then compile in C:\\MT5_JEV_TEST with MetaEditor from PowerShell)"""
src = open("mql5/DragonClone_v15.mq5", encoding="utf-8").read()
def rep(a, b):
    global src
    assert src.count(a) == 1, a[:70]; src = src.replace(a, b)

rep("input int    LevelStopK = 0;", """input int    ThrottleAdds = 0;         // v16 (GPT t284, 17.11.2026): adds filled within ThrottleWinMin that start a pause (0 = off)
input int    ThrottleWinMin = 60;      // v16: ...rolling window, minutes
input int    ThrottleCoolMin = 180;    // v16: ...pause after the last of them, minutes; afterwards one add per pause
input int    LevelStopK = 0;""")
rep("double DDMult()   // v11", """datetime thrT[2][64]; int thrN[2] = {0, 0}; datetime thrCool[2] = {0, 0}; bool thrReg[2] = {false, false};
bool ThrOk(int side, int n)   // v16: may this side add a level now?
  {
   if(ThrottleAdds <= 0) return true;
   if(n <= 1) { thrN[side] = 0; thrCool[side] = 0; thrReg[side] = false; }   // a new basket
   return TimeCurrent() >= thrCool[side];
  }
void ThrOnAdd(int side)   // v16: an add was filled
  {
   if(ThrottleAdds <= 0) return;
   datetime t = TimeCurrent();
   if(thrReg[side]) { thrCool[side] = t + ThrottleCoolMin * 60; return; }
   if(thrN[side] < 64) thrT[side][thrN[side]++] = t;
   int c = 0;
   for(int i = 0; i < thrN[side]; i++) if(thrT[side][i] > t - ThrottleWinMin * 60) c++;
   if(c >= ThrottleAdds) { thrReg[side] = true; thrCool[side] = t + ThrottleCoolMin * 60; }
  }
double DDMult()   // v11""")
rep("            if(!V5AddOk(side, b)) continue;", "            if(!ThrOk(side, b.n)) continue;   // v16\n            if(!V5AddOk(side, b)) continue;")
rep("            if(ok && trade.ResultRetcode() == TRADE_RETCODE_DONE && trade.ResultDeal() > 0) lastAddBar[side] = barNow;",
    "            if(ok && trade.ResultRetcode() == TRADE_RETCODE_DONE && trade.ResultDeal() > 0) { lastAddBar[side] = barNow; ThrOnAdd(side); }")
open("mql5/DragonClone_v16.mq5", "w", encoding="utf-8").write(src.replace("DragonClone_v15", "DragonClone_v16"))

s = open("research/bd1/sets/dcv15_2d.set", "rb").read().decode("utf-16")
nl = "\r\n" if "\r\n" in s else "\n"
i = s.index("LevelStopK=")
s = s[:i] + nl.join(["ThrottleAdds=0", "ThrottleWinMin=60", "ThrottleCoolMin=180"]) + nl + s[i:]
open("research/bd1/sets/dcv16_2d.set", "wb").write(s.encode("utf-16"))
print("v16")
