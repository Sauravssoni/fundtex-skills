"""Fundtex Agent Desk: mocked adapter contracts, genuine source labels and output smoke checks."""
from datetime import date,datetime,timedelta,timezone
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fundtex_india import broker_quotes
from fundtex_india import research_auto

ROOT=Path(__file__).resolve().parents[1]

def pretend_public(symbol,*,range_,interval):
    today=datetime.now(timezone.utc).date()
    rows=[{"date":(today-timedelta(days=110-i)).isoformat(),
           "close":float(100+i*0.4),"volume":10000+i} for i in range(111)]
    return {"symbol":symbol,"rows":rows,"source":"https://query1.finance.yahoo.com/v8/finance/chart/"+symbol,
            "quality":"UNOFFICIAL_BEST_EFFORT_DELAYED","observed_as_of":rows[-1]["date"]}

class AgentDeskTests(unittest.TestCase):
    def test_yahoo_live_history_mock_reports_not_broker_live(self):
        with tempfile.TemporaryDirectory() as temp, patch("fundtex_india.research_auto.broker_status",return_value={"kite":False,"dhan":False}):
            target=Path(temp)/"live-report"
            d=research_auto.run("INFY.NS",target,fetch_public=pretend_public)
            self.assertTrue((target/"manifest.json").exists())
            self.assertTrue((target/"interactive-chart.html").exists())
            self.assertTrue((target/"source-evidence.json").exists())
            self.assertTrue(target.with_suffix(".zip").is_file())
            self.assertFalse((target/"authenticated-quote-snapshot.json").exists())
            self.assertEqual(d["historical_source_quality"],"UNOFFICIAL_BEST_EFFORT_DELAYED")
            self.assertEqual(d["broker_quote"]["status"],"NO_CONFIGURED_BROKER")
            self.assertFalse(d["live_exchange_streaming"])
            source=json.loads((target/"source-evidence.json").read_text())
            self.assertEqual(source["age_days"],0)
            self.assertIn("yahoo.com",source["history_source_uri"])
            with self.assertRaises(ValueError): research_auto.run("INFY.NS",target,fetch_public=pretend_public)

    def test_user_fixture_remains_fictional(self):
        with tempfile.TemporaryDirectory() as temp:
            d=research_auto.run("RELIANCE.NS",str(Path(temp)/"sample"),source="csv",
                               csv_file=str(ROOT/"examples/india_prices.csv"),
                               quote_provider="off",add_zip=False)
            self.assertEqual(d["historical_source_quality"],"SYNTHETIC_FIXTURE")
            self.assertEqual(d["broker_quote"]["status"],"NOT_REQUESTED")
            self.assertIn("SYNTHETIC_FIXTURE",(Path(temp)/"sample"/"START_HERE.md").read_text())

    def test_public_network_failure_does_not_create_fake_report(self):
        with tempfile.TemporaryDirectory() as temp:
            def fail(*args,**kwargs):raise ValueError("network inaccessible")
            dest=Path(temp)/"report"
            with self.assertRaisesRegex(ValueError,"network inaccessible"):
                research_auto.run("INFY.NS",dest,fetch_public=fail)
            self.assertFalse(dest.exists())

    def test_stale_feed_fails_without_old_quote_claim(self):
        def stale(symbol,*,range_,interval):
            r=pretend_public(symbol,range_=range_,interval=interval)
            r["rows"]=[dict(x,date=(date.fromisoformat(x["date"])-timedelta(days=90)).isoformat()) for x in r["rows"]]
            return r
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/"report"
            with self.assertRaisesRegex(ValueError,"stale"):
                research_auto.run("INFY.NS",dest,fetch_public=stale)
            self.assertFalse(dest.exists())

    def test_explicit_broker_requires_valid_reply(self):
        with tempfile.TemporaryDirectory() as temp:
            def missing(*args):raise ValueError("Kite credentials not configured")
            with self.assertRaisesRegex(ValueError,"credentials"):
                research_auto.run("INFY.NS",Path(temp)/"report",quote_provider="kite",
                                  fetch_public=pretend_public,fetch_quote=missing)
            self.assertFalse((Path(temp)/"report").exists())

    def test_broker_success_is_independent_snapshot(self):
        def q(symbol,provider):
            return {"symbol":symbol,"provider":provider,"last_price_inr":1234.5,
                    "quality":"AUTHENTICATED_BROKER_SNAPSHOT_NOT_WEBSOCKET",
                    "retrieved_at_utc":datetime.now(timezone.utc).isoformat(),
                    "publisher_trade_timestamp":None}
        with tempfile.TemporaryDirectory() as temp:
            d=research_auto.run("INFY.NS",Path(temp)/"report",fetch_public=pretend_public,
                                quote_provider="kite",fetch_quote=q,add_zip=False)
            snap=json.loads((Path(temp)/"report"/"authenticated-quote-snapshot.json").read_text())
            self.assertEqual(snap["last_price_inr"],1234.5)
            self.assertTrue(d["broker_quote"]["live_authenticated"])
            self.assertFalse(d["live_exchange_streaming"])

    def test_broker_official_response_contracts_and_token_safety(self):
        with self.assertRaises(ValueError):
            broker_quotes.quote("INFY.NS","nonsense")
        with self.assertRaises(ValueError):
            broker_quotes._request("https://example.org/pirate",{})
        kite={"status":"success","data":{"NSE:INFY":{"last_price":1431.75}}}
        dhan={"status":"success","data":{"NSE_EQ":{"1594":{"last_price":1532.5}}}}
        self.assertEqual(broker_quotes.parse_kite(kite,"INFY.NS")["last_price_inr"],1431.75)
        self.assertEqual(broker_quotes.parse_dhan(dhan,"INFY.NS","1594")["last_price_inr"],1532.5)
        with self.assertRaises(ValueError):
            broker_quotes.parse_kite({"status":"success","data":{}},"INFY.NS")
        with self.assertRaises(ValueError):
            broker_quotes.parse_dhan({"status":"failed","data":{}},"INFY.NS","1594")
        env={"FUNDTEX_KITE_API_KEY":"MOCK_A_KEY",
             "FUNDTEX_KITE_ACCESS_TOKEN":"MOCK_A_TOKEN",
             "FUNDTEX_DHAN_CLIENT_ID":"MOCK_CLIENT",
             "FUNDTEX_DHAN_ACCESS_TOKEN":"MOCK_DHAN_TOKEN",
             "FUNDTEX_DHAN_SYMBOL_MAP":'{"INFY.NS":"1594"}'}
        with patch.dict(os.environ,env),patch("fundtex_india.broker_quotes._request") as request:
            request.return_value=kite
            out=broker_quotes.quote("INFY.NS","kite")
            self.assertNotIn("MOCK_A_TOKEN",json.dumps(out))
            self.assertIn("Authorization",request.call_args[0][1])
            request.return_value=dhan
            out=broker_quotes.quote("INFY.NS","dhan")
            self.assertNotIn("MOCK_DHAN_TOKEN",json.dumps(out))
            self.assertIn("NSE_EQ",request.call_args.kwargs["body"].decode())

    def test_dhan_invalid_instrument_fails_before_network(self):
        env={"FUNDTEX_DHAN_CLIENT_ID":"FAKE_ID","FUNDTEX_DHAN_ACCESS_TOKEN":"FAKE_TOKEN",
             "FUNDTEX_DHAN_SYMBOL_MAP":'{"INFY.NS":"NOT_AN_ID"}'}
        with patch.dict(os.environ,env),patch("fundtex_india.broker_quotes._request") as rq:
            with self.assertRaisesRegex(ValueError,"security id"):
                broker_quotes.quote("INFY.NS","dhan")
            rq.assert_not_called()

if __name__=="__main__":unittest.main()
