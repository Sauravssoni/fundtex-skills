"""Authoritative Kite MCP market-data import contract; controlled fictitious fixtures."""
from datetime import date,datetime,timedelta,timezone
import csv
import json
from pathlib import Path
import tempfile
import unittest
from fundtex_india.kite_mcp_research import normalize_ltp,normalize_daily_history,export_historical_csv

ST=datetime(2026,10,23,7,0,tzinfo=timezone.utc)
def fixture(n=80):
    base=date(2026,6,1)
    dates=[base+timedelta(days=i) for i in range(n)]
    return {"data":{"candles":[[day.isoformat()+"T09:15:00+05:30",
                  100+i,102+i,99+i,101+i,10000+i] for i,day in enumerate(dates)]}}

class KiteMCPImportTests(unittest.TestCase):
    def test_quote_exact_instrument_and_no_live_timestamp_fabrication(self):
        snap={"NSE:INFY":{"last_price":123.4,"instrument_token":408065}}
        r=normalize_ltp(snap,"INFY.NS",collected_utc=ST)
        self.assertEqual(r["last_price_inr"],123.4)
        self.assertIsNone(r["publisher_trade_timestamp"])
        self.assertFalse(r["provider_market_session_authenticated_by_local_import"])
        self.assertFalse(r["can_execute_trades"])
        self.assertTrue(r["price_is_not_guaranteed_realtime"])
    def test_mcp_text_wrapper_and_no_price_for_other_instrument(self):
        data={"content":[{"type":"text","text":json.dumps({"data":{"NSE:INFY":{"last_price":123.4}}})}]}
        self.assertEqual(normalize_ltp(data,"INFY.NS",collected_utc=ST)["last_price_inr"],123.4)
        with self.assertRaisesRegex(ValueError,"exact Kite instrument"):
            normalize_ltp(data,"TCS.NS",collected_utc=ST)
        with self.assertRaisesRegex(ValueError,"positive"):
            normalize_ltp({"NSE:INFY":{"last_price":-1}},"INFY.NS",collected_utc=ST)
    def test_approved_historical_bars_research_export(self):
        r=normalize_daily_history(fixture(),"INFY.NS",instrument_token=408065,
                                  requested_from="2026-06-01",requested_through="2026-09-01")
        self.assertEqual(len(r["rows"]),80)
        self.assertEqual(r["data_quality"],"USER_APPROVED_KITE_MCP_PAYLOAD_NOT_EXCHANGE_SIGNED")
        self.assertFalse(r["trading_authority"])
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/"kite.csv"
            out=export_historical_csv(r,out_csv=target)
            self.assertEqual(out["observations"],80)
            with target.open(newline="") as fh:
                rows=list(csv.DictReader(fh))
            self.assertEqual(rows[0]["open"],"100.0")
            self.assertEqual(rows[-1]["close"],"180.0")
            self.assertTrue(target.with_suffix(".receipt.json").is_file())
            self.assertFalse(out["trading_authority"])
            with self.assertRaisesRegex(ValueError,"NEW CSV"):
                export_historical_csv(r,out_csv=target)
    def test_reject_lookahead_impossible_quotes_and_duplicate_bars(self):
        s=fixture()
        s["data"]["candles"][2][2]=20
        with self.assertRaisesRegex(ValueError,"Impossible"):
            normalize_daily_history(s,"INFY.NS",instrument_token=408065,
                                    requested_from="2026-06-01",requested_through="2026-09-01")
        s=fixture()
        s["data"]["candles"][2][0]=s["data"]["candles"][1][0]
        with self.assertRaisesRegex(ValueError,"duplicate"):
            normalize_daily_history(s,"INFY.NS",instrument_token=408065,
                                    requested_from="2026-06-01",requested_through="2026-09-01")
        with self.assertRaisesRegex(ValueError,"outside requested"):
            normalize_daily_history(fixture(),"INFY.NS",instrument_token=408065,
                                    requested_from="2026-07-01",requested_through="2026-09-01")
    def test_refuse_error_envelopes_and_instrument_tokens(self):
        with self.assertRaisesRegex(ValueError,"Provider explicitly"):
            normalize_daily_history({"status":"error","data":{"candles":[]}},"INFY.NS",instrument_token=1,
                                    requested_from="2026-06-01",requested_through="2026-09-01")
        with self.assertRaisesRegex(ValueError,"independently verified"):
            normalize_daily_history(fixture(),"INFY.NS",instrument_token=True,
                                    requested_from="2026-06-01",requested_through="2026-09-01")
        with self.assertRaisesRegex(ValueError,"40..3000"):
            normalize_daily_history(fixture(20),"INFY.NS",instrument_token=408065,
                                    requested_from="2026-06-01",requested_through="2026-09-01")
    def test_cli_requires_real_approved_output_files(self):
        import subprocess,sys
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as folder:
            data=Path(folder)/"history.json"
            data.write_text(json.dumps(fixture()),encoding="utf-8")
            dest=Path(folder)/"kite.csv"
            cmd=[sys.executable,"-m","fundtex_india.cli","kite-mcp-import",
                 "--mode","history","--file",str(data),"--symbol","INFY.NS",
                 "--instrument-token","408065","--from-date","2026-06-01",
                 "--through-date","2026-09-01","--out",str(dest)]
            p=subprocess.run(cmd,cwd=root,capture_output=True,text=True,timeout=15)
            self.assertEqual(p.returncode,0,p.stderr)
            receipt=json.loads(p.stdout)
            self.assertEqual(receipt["observations"],80)
            self.assertTrue(dest.with_suffix(".receipt.json").is_file())
            self.assertFalse(receipt["trading_authority"])
            again=subprocess.run(cmd,cwd=root,capture_output=True,text=True,timeout=15)
            self.assertNotEqual(again.returncode,0)
            self.assertIn("NEW CSV",again.stderr)
            untrusted=subprocess.run(cmd[:-2],cwd=root,capture_output=True,text=True,timeout=15)
            self.assertNotEqual(untrusted.returncode,0)

    def test_pascal_case_historical_fields(self):
        hist={"candles":[{"Date":(date(2026,6,1)+timedelta(days=i)).isoformat(),
             "Open":100+i,"High":102+i,"Low":99+i,"Close":101+i,"Volume":10000+i} for i in range(80)]}
        r=normalize_daily_history(hist,"INFY.NS",instrument_token=408065,
                                  requested_from="2026-06-01",requested_through="2026-09-01")
        self.assertEqual(r["rows"][-1]["close"],180)
    def test_do_not_parse_unrelated_personal_account_payload(self):
        with self.assertRaises(ValueError):
            normalize_daily_history({"data":{"holdings":[{"name":"secret"}]}},"INFY.NS",
                                    instrument_token=408065,requested_from="2026-06-01",
                                    requested_through="2026-09-01")
if __name__=="__main__":unittest.main()
