"""Fundtex v1.0.2 extra fact/research proof: no ML marketing from keyword flags."""
import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from fundtex_india import research_extensions
from fundtex_india.research_auto import run

ROOT=Path(__file__).resolve().parents[1]

def mocked_public(symbol,*,range_,interval):
    last=dt.datetime.now(dt.timezone.utc).date()
    rows=[{"date":(last-dt.timedelta(days=290-i)).isoformat(),
           "close":1500+11*i+((i%5)-2)*6,"volume":100000+i} for i in range(291)]
    return {"rows":rows,"source":"https://query1.finance.yahoo.com/v8/finance/chart/"+symbol,"quality":"UNOFFICIAL_BEST_EFFORT_DELAYED"}

def mocked_news(query,limit=12):
    return {"query":query,"quality":"DISCOVERY_ONLY_NOT_EXCHANGE_FILINGS",
            "items":[{"headline":"Infosys quarterly results guidance and growth","publisher":"TEST ONLY",
                      "url":"https://example.test/news","published_raw":"Thu, 22 Oct 2026 07:00:00 GMT",
                      "quality":"UNVERIFIED_HEADLINE_DISCOVERY"}]}

class ResearchExtensionTests(unittest.TestCase):
    def test_headlines_are_never_verified_sentiment(self):
        d=research_extensions._metadata_sentiment(mocked_news("INFY"))
        self.assertEqual(d["total_headlines"],1)
        self.assertEqual(d["articles_opened_and_verified"],0)
        self.assertIsNone(d["predictive_score"])
        self.assertEqual(d["sentiment_signal"],"NOT_VALIDATED_UNSUITABLE_FOR_TRADING")
        self.assertTrue(d["events"][0]["headline_topic_flags"])

    def test_end_to_end_quant_and_headlines(self):
        with tempfile.TemporaryDirectory() as t:
            r=run("INFY.NS",str(Path(t)/"pack"),source="public",quote_provider="off",
                  fetch_public=mocked_public,include_news=True,fetch_news=mocked_news)
            root=Path(t)/"pack"
            for name in ("risk-diagnostics.json","forecast-validation.json",
                         "walkforward-reality-check.json","headline-topic-monitor.json",
                         "news-leads-unverified.json","manifest.json"):
                self.assertTrue((root/name).is_file(),name)
            manifest=json.loads((root/"manifest.json").read_text())
            self.assertFalse(manifest["live_exchange_streaming"])
            forecast=json.loads((root/"forecast-validation.json").read_text())
            self.assertFalse(forecast["gates"]["authorized_for_live_trades"])
            self.assertFalse(forecast["gates"]["license_corporate_actions_and_pit_certified"])
            self.assertNotIn("market data verified", (root/"START_HERE.md").read_text().lower())

    def test_local_csv_never_triggers_news_by_default(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/"local"
            r=run("RELIANCE.NS",str(out),source="csv",
                  csv_file=str(ROOT/"examples/india_prices.csv"),quote_provider="off",
                  fetch_news=lambda *a,**k: (_ for _ in ()).throw(AssertionError("Unexpected external query")),
                  add_zip=False)
            self.assertEqual(r["historical_source_quality"],"SYNTHETIC_FIXTURE")
            self.assertIn("disabled",r["research_extensions"]["unavailable"]["news-leads-unverified.json"])

    def test_news_failure_records_omission_without_fake_sentiment(self):
        def failed(*args,**kwargs): raise OSError("offline")
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/"offline-news"
            r=run("INFY.NS",str(out),quote_provider="off",
                  fetch_public=mocked_public,include_news=True,fetch_news=failed,add_zip=False)
            self.assertFalse((out/"headline-topic-monitor.json").exists())
            self.assertIn("News discovery unavailable",r["research_extensions"]["unavailable"]["news-leads-unverified.json"])

if __name__=="__main__":unittest.main()
