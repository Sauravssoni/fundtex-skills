"""FYERS v3 official read-only API contracts, including actual OHLCV preservation."""
import datetime as dt
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fundtex_india import fyers_data,broker_quotes,research_auto

def candles(symbol,*,range_,interval):
    today=dt.datetime.now(dt.timezone.utc).date()
    rows=[]
    for n in range(80):
        stamp=int(dt.datetime.combine(today-dt.timedelta(days=79-n),dt.time(9),tzinfo=dt.timezone.utc).timestamp())
        # Date from epoch +5:30 remains the intended date.
        o=200+n*.3;c=o+1
        rows.append([stamp,o,o+4,o-2,c,100_000+n])
    return fyers_data.parse_history({"s":"ok","code":200,"candles":rows},symbol)

class FyersTests(unittest.TestCase):
    def test_quotes_contract(self):
        payload={"s":"ok","code":200,"d":[{"n":"NSE:INFY-EQ","s":"ok","v":{"lp":1402.55,"tt":1752000000}}]}
        r=fyers_data.parse_quote(payload,"INFY.NS")
        self.assertEqual(r["last_price_inr"],1402.55)
        self.assertEqual(r["provider"],"fyers")
        self.assertIsNotNone(r["publisher_trade_timestamp"])
        with self.assertRaises(ValueError):
            fyers_data.parse_quote({"s":"error","d":[]},"INFY.NS")
        with self.assertRaises(ValueError):
            fyers_data.parse_quote({"s":"ok","d":[{"n":"NSE:TCS-EQ","s":"ok","v":{"lp":900}}]},"INFY.NS")
        with self.assertRaises(ValueError):
            fyers_data.parse_quote(payload,"500209.BO")
    def test_history_candles_real_ohlcv(self):
        today=dt.datetime.now(dt.timezone.utc).date()
        stamps=[int(dt.datetime.combine(today-dt.timedelta(days=19-i),dt.time(4),tzinfo=dt.timezone.utc).timestamp()) for i in range(20)]
        result=fyers_data.parse_history({"s":"ok","code":200,"candles":[[x,100,109,98,104,1000] for x in stamps]},"INFY.NS")
        self.assertEqual(len(result["rows"]),20)
        self.assertEqual(result["rows"][-1]["high"],109)
        self.assertEqual(result["quality"],"AUTHENTICATED_FYERS_HISTORY_NOT_TICK_STREAM")
        with self.assertRaises(ValueError):
            fyers_data.parse_history({"s":"ok","candles":[[stamps[0],100,95,110,104,1000]]*20},"INFY.NS")
        with self.assertRaises(ValueError):
            fyers_data.parse_history({"s":"error","candles":[]},"INFY.NS")
    def test_real_history_mode_preserves_candles_through_pack(self):
        # Synthetic mock response representing an authenticated envelope: tests adapter shape ONLY.
        with tempfile.TemporaryDirectory() as t:
            target=Path(t)/"fyers-mock"
            result=research_auto.run("INFY.NS",target,source="fyers",period="1mo",
                                     fetch_public=candles,quote_provider="off",add_zip=False)
            spec=json.loads((target/"chart-spec.json").read_text())
            self.assertEqual(spec["price_type"],"OHLC_CANDLE")
            self.assertEqual(result["historical_source_quality"],"AUTHENTICATED_FYERS_HISTORY_NOT_TICK_STREAM")
            self.assertIn("open,high,low,close", (target/"price-history.csv").read_text().replace("date,",""))
    def test_fyers_read_only_endpoints_and_env(self):
        with patch.dict(os.environ,{"FUNDTEX_FYERS_APP_ID":"TEST-100","FUNDTEX_FYERS_ACCESS_TOKEN":"FAKE-TOKEN"}),patch("fundtex_india.fyers_data._request") as req:
            req.return_value={"s":"ok","d":[{"n":"NSE:INFY-EQ","s":"ok","v":{"lp":1423.7}}]}
            output=broker_quotes.quote("INFY.NS","fyers")
            self.assertEqual(output["provider"],"fyers")
            self.assertNotIn("FAKE-TOKEN",json.dumps(output))
            self.assertIn("/data/quotes?",req.call_args.args[0])
            self.assertTrue(broker_quotes.availability()["fyers"])
            req.reset_mock()
            req.return_value={"s":"ok","code":200,"candles":[]}
            with self.assertRaises(ValueError):
                fyers_data.history("INFY.NS",range_="1mo")
            self.assertIn("/data/history?",req.call_args.args[0])
            self.assertTrue(req.call_args.args[0].startswith("https://api-t1.fyers.in/"))
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaisesRegex(ValueError,"not configured"):
                broker_quotes.quote("INFY.NS","fyers")
    def test_no_redirect_endpoint_escape(self):
        with self.assertRaises(ValueError):
            broker_quotes._request("https://api-t1.fyers.in.evil.com/data/quotes?symbols=X",{})
        with self.assertRaises(ValueError):
            broker_quotes._request("https://api-t1.fyers.in/data/order",{})

if __name__=="__main__":unittest.main()
