//+------------------------------------------------------------------+
//| SignalExport: research helper, never trades. Dumps the MQL5      |
//| signals base visible to this terminal (SignalBase*) to           |
//| Common\Files\signals_base.csv. Run as a startup script.          |
//+------------------------------------------------------------------+
#property script_show_inputs false

void OnStart()
{
   int n = 0;
   for(int k = 0; k < 300 && (n = SignalBaseTotal()) <= 0; k++) Sleep(1000);
   PrintFormat("signals in base: %d", n);
   int f = FileOpen("signals_base.csv", FILE_WRITE | FILE_CSV | FILE_ANSI | FILE_COMMON, ',');
   if(f == INVALID_HANDLE) { Print("open failed ", GetLastError()); return; }
   FileWrite(f, "id", "name", "author", "broker", "server", "currency", "trade_mode", "leverage", "date_published", "date_started",
             "date_updated", "trades", "subscribers", "gain", "max_dd", "roi", "pips", "balance", "equity", "price", "rating");
   for(int i = 0; i < n; i++)
   {
      if(!SignalBaseSelect(i)) continue;
      string nm = SignalBaseGetString(SIGNAL_BASE_NAME); StringReplace(nm, ",", " "); StringReplace(nm, "\"", " ");
      string au = SignalBaseGetString(SIGNAL_BASE_AUTHOR_LOGIN); StringReplace(au, ",", " ");
      string br = SignalBaseGetString(SIGNAL_BASE_BROKER); StringReplace(br, ",", " ");
      FileWrite(f, SignalBaseGetInteger(SIGNAL_BASE_ID), nm, au, br, SignalBaseGetString(SIGNAL_BASE_BROKER_SERVER),
                SignalBaseGetString(SIGNAL_BASE_CURRENCY), SignalBaseGetInteger(SIGNAL_BASE_TRADE_MODE), SignalBaseGetInteger(SIGNAL_BASE_LEVERAGE),
                SignalBaseGetInteger(SIGNAL_BASE_DATE_PUBLISHED), SignalBaseGetInteger(SIGNAL_BASE_DATE_STARTED), SignalBaseGetInteger(SIGNAL_BASE_DATE_UPDATED),
                SignalBaseGetInteger(SIGNAL_BASE_TRADES), SignalBaseGetInteger(SIGNAL_BASE_SUBSCRIBERS),
                DoubleToString(SignalBaseGetDouble(SIGNAL_BASE_GAIN), 2), DoubleToString(SignalBaseGetDouble(SIGNAL_BASE_MAX_DRAWDOWN), 2),
                DoubleToString(SignalBaseGetDouble(SIGNAL_BASE_ROI), 2), SignalBaseGetInteger(SIGNAL_BASE_PIPS),
                DoubleToString(SignalBaseGetDouble(SIGNAL_BASE_BALANCE), 2), DoubleToString(SignalBaseGetDouble(SIGNAL_BASE_EQUITY), 2),
                DoubleToString(SignalBaseGetDouble(SIGNAL_BASE_PRICE), 2), SignalBaseGetInteger(SIGNAL_BASE_RATING));
   }
   FileClose(f);
   Print("signals export done");
}
