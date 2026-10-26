//+------------------------------------------------------------------+
//| CalendarExport: research helper, never trades. On a live chart   |
//| (the strategy tester has no economic calendar) it writes the MT5 |
//| calendar events of one currency to Common\Files, then closes the |
//| terminal. Times are the trade server clock, the same clock the   |
//| tester uses, so DragonClone_v7 (NewsFile) can pause around them. |
//|  <OutName>_all.csv : time,importance,event,actual,forecast,prev  |
//|  <OutName>_high.txt: one unix time per line, HIGH importance     |
//|  <OutName>_med.txt : one unix time per line, MODERATE and HIGH   |
//+------------------------------------------------------------------+
#property strict
input string   Currency = "USD";
input datetime From = D'2021.12.01';
input string   OutName = "news_usd";
input bool     CloseWhenDone = true;

int tries = 0;

int OnInit() { EventSetTimer(5); return INIT_SUCCEEDED; }   // the calendar loads after the connection
void OnDeinit(const int reason) { EventKillTimer(); }

string Val(long v) { return v == LONG_MIN ? "" : DoubleToString(v / 1e6, 3); }

void OnTimer()
  {
   MqlCalendarValue v[];
   int n = CalendarValueHistory(v, From, TimeTradeServer() + 86400 * 30, NULL, Currency);
   if(n <= 0 && ++tries < 24) { PrintFormat("calendar not ready (%d), err %d", n, GetLastError()); return; }
   EventKillTimer();
   int fa = FileOpen(OutName + "_all.csv", FILE_WRITE | FILE_CSV | FILE_COMMON | FILE_ANSI, ',');
   int fh = FileOpen(OutName + "_high.txt", FILE_WRITE | FILE_TXT | FILE_COMMON | FILE_ANSI);
   int fm = FileOpen(OutName + "_med.txt", FILE_WRITE | FILE_TXT | FILE_COMMON | FILE_ANSI);
   FileWrite(fa, "time", "importance", "event", "actual", "forecast", "prev");
   long lastH = 0, lastM = 0; int nh = 0, nm = 0;
   for(int i = 0; i < n; i++)   // CalendarValueHistory returns the values sorted by time
     {
      MqlCalendarEvent e;
      if(!CalendarEventById(v[i].event_id, e)) continue;
      FileWrite(fa, (long)v[i].time, (int)e.importance, e.name, Val(v[i].actual_value), Val(v[i].forecast_value), Val(v[i].prev_value));
      long t = (long)v[i].time;
      if(e.importance == CALENDAR_IMPORTANCE_HIGH && t != lastH) { FileWriteString(fh, IntegerToString(t) + "\r\n"); lastH = t; nh++; }
      if(e.importance >= CALENDAR_IMPORTANCE_MODERATE && t != lastM) { FileWriteString(fm, IntegerToString(t) + "\r\n"); lastM = t; nm++; }
     }
   FileClose(fa); FileClose(fh); FileClose(fm);
   PrintFormat("CalendarExport %s: %d values, %d high times, %d moderate+ times; server-GMT offset %d s",
               Currency, n, nh, nm, (int)(TimeTradeServer() - TimeGMT()));
   if(CloseWhenDone) TerminalClose(0);
  }
