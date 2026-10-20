//+------------------------------------------------------------------+
//| JevObjDump: lists the chart objects (the EA panel) in the tester  |
//| and, optionally, switches a button state at a given time, so we   |
//| can check whether Black Dragon reads its PAUSE button.            |
//| Read-only research tool: it never trades.                         |
//+------------------------------------------------------------------+
#property indicator_chart_window
#property indicator_plots 0
input string   PressName = "";        // object name to switch (empty: only list)
input datetime PressFrom = 0;         // switch ON from this time
input datetime PressTo   = 0;         // switch OFF again from this time
datetime last_dump = 0;
int OnInit() { return(INIT_SUCCEEDED); }
int OnCalculate(const int rates_total, const int prev_calculated, const datetime &time[], const double &open[],
                const double &high[], const double &low[], const double &close[], const long &tick_volume[],
                const long &volume[], const int &spread[])
{
   datetime now = TimeCurrent();
   if(PressName != "" && ObjectFind(0, PressName) >= 0)
   {
      bool want = (now >= PressFrom && now < PressTo);
      if((bool)ObjectGetInteger(0, PressName, OBJPROP_STATE) != want)
      {
         ObjectSetInteger(0, PressName, OBJPROP_STATE, want);
         int h = FileOpen("jev_press_log.csv", FILE_WRITE|FILE_READ|FILE_CSV|FILE_COMMON|FILE_SHARE_READ, ';');
         if(h != INVALID_HANDLE) { FileSeek(h, 0, SEEK_END); FileWrite(h, TimeToString(now), PressName, want); FileClose(h); }
      }
   }
   if(now - last_dump >= 6 * 3600)
   {
      last_dump = now;
      int h = FileOpen("jev_objdump.csv", FILE_WRITE|FILE_READ|FILE_CSV|FILE_COMMON|FILE_SHARE_READ, ';');
      if(h != INVALID_HANDLE)
      {
         FileSeek(h, 0, SEEK_END);
         for(int i = 0; i < ObjectsTotal(0); i++)
         {
            string n = ObjectName(0, i);
            FileWrite(h, TimeToString(now), n, ObjectGetInteger(0, n, OBJPROP_TYPE),
                      ObjectGetInteger(0, n, OBJPROP_STATE), ObjectGetString(0, n, OBJPROP_TEXT));
         }
         FileClose(h);
      }
   }
   return(rates_total);
}
