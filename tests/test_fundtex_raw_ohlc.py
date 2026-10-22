"""Public unadjusted real OHLC adapter contract: never adjusted-close pseudo-candles."""
import json
import unittest
from datetime import date,timedelta
from unittest.mock import patch
from fundtex_india.market import yahoo_ohlcv_prices

class PublicUnadjustedOHLC(unittest.TestCase):
    def payload(self):
        import calendar
        timestamps=[calendar.timegm((date(2025,3,1)+timedelta(days=i)).timetuple())+36000 for i in range(35)]
        data={"timestamp":timestamps,"meta":{"symbol":"INFY.NS"},
              "indicators":{"quote":[{"open":[100+i for i in range(35)],
                                    "high":[102+i for i in range(35)],
                                    "low":[99+i for i in range(35)],
                                    "close":[101+i for i in range(35)],
                                    "volume":[10000+i for i in range(35)]}],
                            "adjclose":[{"adjclose":[5000+i for i in range(35)]}]}}
        return {"chart":{"result":[data],"error":None}}
    def test_ohlc_uses_raw_quotes_not_mixed_adjusted_close(self):
        raw=json.dumps(self.payload()).encode()
        with patch("fundtex_india.market.fetch_bytes",return_value=raw) as fetch:
            r=yahoo_ohlcv_prices("INFY.NS",range_="2y")
        self.assertEqual(r["rows"][0]["close"],101.0)
        self.assertEqual(r["rows"][0]["open"],100.0)
        self.assertNotEqual(r["rows"][0]["close"],5000.0)
        self.assertEqual(r["adjustment_basis"],"RAW_UNADJUSTED_QUOTES_ONLY")
        self.assertEqual(r["quality"],"UNOFFICIAL_UNADJUSTED_OHLC_NOT_EXCHANGE_VERIFIED")
        self.assertEqual(r["omitted_incomplete_provider_candles"],0)
        self.assertEqual(fetch.call_count,1)
    def test_ticker_mismatch_refused(self):
        data=self.payload()
        data["chart"]["result"][0]["meta"]["symbol"]="OTHER.NS"
        with patch("fundtex_india.market.fetch_bytes",return_value=json.dumps(data).encode()):
            with self.assertRaisesRegex(ValueError,"different ticker"):
                yahoo_ohlcv_prices("INFY.NS")
    def test_impossible_candle_refused(self):
        data=self.payload()
        data["chart"]["result"][0]["indicators"]["quote"][0]["high"][0]=80
        with patch("fundtex_india.market.fetch_bytes",return_value=json.dumps(data).encode()):
            with self.assertRaisesRegex(ValueError,"constraints"):
                yahoo_ohlcv_prices("INFY.NS")
    def test_unavailable_candle_omitted_but_not_fabricated(self):
        data=self.payload()
        data["chart"]["result"][0]["indicators"]["quote"][0]["open"][0]=None
        with patch("fundtex_india.market.fetch_bytes",return_value=json.dumps(data).encode()):
            r=yahoo_ohlcv_prices("INFY.NS")
        self.assertEqual(len(r["rows"]),34)
        self.assertEqual(r["omitted_incomplete_provider_candles"],1)
    def test_boolean_or_nan_candle_refused(self):
        data=self.payload()
        data["chart"]["result"][0]["indicators"]["quote"][0]["open"][0]=True
        with patch("fundtex_india.market.fetch_bytes",return_value=json.dumps(data).encode()):
            with self.assertRaises(ValueError):
                yahoo_ohlcv_prices("INFY.NS")
if __name__=="__main__":
    unittest.main()
