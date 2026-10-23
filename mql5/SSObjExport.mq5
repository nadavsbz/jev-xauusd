//+------------------------------------------------------------------+
//| SSObjExport: loads Strong_Support with iCustom and, on every new |
//| H1 bar, writes every chart object it has drawn (name, type, times |
//| and prices) to a CSV in the common files folder. Strong_Support   |
//| draws its levels as objects, not buffers, so a buffer export only |
//| gave zeros (docs/BD_PERSIST_PLAN.md). Research only: never trades.|
//+------------------------------------------------------------------+
#property strict
#property tester_indicator "Strong_Support.ex5"
input string OutFile = "ss_objects.csv";
int h = INVALID_HANDLE, f = INVALID_HANDLE;
datetime last = 0;

int OnInit()
  {
   h = iCustom(_Symbol, _Period, "Strong_Support");
   if(h == INVALID_HANDLE) return INIT_FAILED;
   ChartIndicatorAdd(0, 0, h);                       // draw it on the visual tester chart
   f = FileOpen(OutFile, FILE_WRITE|FILE_CSV|FILE_COMMON|FILE_ANSI, ',');
   if(f == INVALID_HANDLE) return INIT_FAILED;
   FileWrite(f, "bar_time", "name", "type", "time1", "price1", "time2", "price2", "color");
   return INIT_SUCCEEDED;
  }

void OnDeinit(const int r) { if(f != INVALID_HANDLE) FileClose(f); }

void OnTick()
  {
   datetime b = iTime(_Symbol, PERIOD_H1, 0);
   if(b == last) return;
   last = b;
   double tmp[1]; CopyBuffer(h, 0, 0, 1, tmp);     // keep the indicator calculating
   int n = ObjectsTotal(0, -1, -1);
   for(int i = 0; i < n; i++)
     {
      string nm = ObjectName(0, i, -1, -1);
      FileWrite(f, TimeToString(b), nm, (int)ObjectGetInteger(0, nm, OBJPROP_TYPE),
                TimeToString((datetime)ObjectGetInteger(0, nm, OBJPROP_TIME, 0)), DoubleToString(ObjectGetDouble(0, nm, OBJPROP_PRICE, 0), 2),
                TimeToString((datetime)ObjectGetInteger(0, nm, OBJPROP_TIME, 1)), DoubleToString(ObjectGetDouble(0, nm, OBJPROP_PRICE, 1), 2),
                (long)ObjectGetInteger(0, nm, OBJPROP_COLOR));
     }
  }
