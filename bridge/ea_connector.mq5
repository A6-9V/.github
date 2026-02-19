//+------------------------------------------------------------------+
//|                                              JulesConnector.mq5 |
//|                                  Copyright 2024, A6-9V Org      |
//|                                             https://a6-9v.com   |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, A6-9V Org"
#property link      "https://a6-9v.com"
#property version   "1.10"
#property strict

#include <Trade\Trade.mqh>

// Input parameters
input string   InpServerUrl = "http://your-vps-ip:8000"; // Bridge Server URL
input string   InpApiKey    = "";      // API Key for Security
input int      InpMagicNum  = 123456;                    // Magic Number

// Global variables
CTrade         trade;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("Jules Connector EA initialized.");
   Print("Ensure that " + InpServerUrl + " is added to the list of allowed URLs in Options -> Expert Advisors.");

   trade.SetExpertMagicNumber(InpMagicNum);

   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("Jules Connector EA deinitialized.");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   static datetime last_send_time = 0;

   // Send data every 5 minutes
   if(TimeCurrent() - last_send_time > 300)
   {
      SendMarketData();
      last_send_time = TimeCurrent();
   }

   // Poll for signals every minute
   static datetime last_poll_time = 0;
   if(TimeCurrent() - last_poll_time > 60)
   {
      PollForSignals();
      last_poll_time = TimeCurrent();
   }
}

//+------------------------------------------------------------------+
//| Function to send market data to the bridge                       |
//+------------------------------------------------------------------+
void SendMarketData()
{
   string url = InpServerUrl + "/ea/update";
   string method = "POST";
   string headers = "Content-Type: application/json\r\n" + "X-API-KEY: " + InpApiKey + "\r\n";

   string body = StringFormat(
      "{\"symbol\":\"%s\", \"price\":%f, \"time\":\"%s\", \"indicator_value\":%f}",
      _Symbol,
      SymbolInfoDouble(_Symbol, SYMBOL_BID),
      TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS),
      iRSI(_Symbol, _Period, 14, PRICE_CLOSE)
   );

   char data[];
   char result[];
   string result_headers;

   StringToCharArray(body, data, 0, WHOLE_ARRAY, CP_UTF8);

   int res = WebRequest(method, url, headers, 5000, data, result, result_headers);

   if(res == -1)
   {
      Print("WebRequest failed, error code =", GetLastError());
   }
   else if(res != 200)
   {
      PrintFormat("Server returned error: %d. Check your API Key.", res);
   }
}

//+------------------------------------------------------------------+
//| Function to poll for trading signals from Jules                 |
//+------------------------------------------------------------------+
void PollForSignals()
{
   string url = InpServerUrl + "/ea/signal?symbol=" + _Symbol;
   string method = "GET";
   string headers = "X-API-KEY: " + InpApiKey + "\r\n";

   char result[];
   string result_headers;

   int res = WebRequest(method, url, headers, 5000, NULL, result, result_headers);

   if(res == 200)
   {
      string response = CharArrayToString(result, 0, WHOLE_ARRAY, CP_UTF8);
      if(response != "null" && response != "")
      {
         Print("Received signal: ", response);
         ExecuteSignal(response);
      }
   }
}

//+------------------------------------------------------------------+
//| Function to parse and execute signal                             |
//+------------------------------------------------------------------+
void ExecuteSignal(string json)
{
   // Basic parsing for prototype
   double volume = 0.1; // Default

   if(StringFind(json, "\"action\":\"BUY\"") >= 0)
   {
      Print("Executing BUY order for ", _Symbol);
      if(!trade.Buy(volume, _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_ASK), 0, 0, "Jules Bridge"))
      {
         Print("Buy failed: ", trade.ResultRetcodeDescription());
      }
   }
   else if(StringFind(json, "\"action\":\"SELL\"") >= 0)
   {
      Print("Executing SELL order for ", _Symbol);
      if(!trade.Sell(volume, _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_BID), 0, 0, "Jules Bridge"))
      {
         Print("Sell failed: ", trade.ResultRetcodeDescription());
      }
   }
}
