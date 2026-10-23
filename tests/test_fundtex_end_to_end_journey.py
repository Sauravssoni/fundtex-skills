"""Zero-order full agent path: fake candles -> model/strategy -> chart/film -> risk.

All generated fixtures are clearly synthetic and never resemble a broker login.
This is an executable release regression, NOT a live market acceptance test.
"""
from __future__ import annotations
import csv
from datetime import date,timedelta
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
class FundTexCompleteJourney(unittest.TestCase):
    def setUp(self):
        scratch=tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.folder=Path(scratch.name)
        self.history=self.folder/"synthetic_ohlc.csv"
        with self.history.open("w",encoding="utf-8",newline="") as f:
            w=csv.writer(f)
            w.writerow(("date","symbol","open","high","low","close","volume","source"))
            for i in range(310):
                close=100+0.13*i+(i%9)*.15
                w.writerow(((date(2025,10,1)+timedelta(days=i)).isoformat(),
                            "DEMO.NS",close-.2,close+.8,close-.75,close,10000+i,
                            "SYNTHETIC_FIXTURE"))
        self.digest=sha256(self.history.read_bytes()).hexdigest()
    def cli(self,*params,expected=0):
        completed=subprocess.run([sys.executable,"-m","fundtex_india.cli",*map(str,params)],
                         cwd=ROOT,capture_output=True,text=True,timeout=35)
        self.assertEqual(completed.returncode,expected,completed.stderr[-1700:])
        if expected:return completed.stderr
        return json.loads(completed.stdout)
    def test_full_research_journey_is_source_bound_and_refuses_trading(self):
        # Step 1: no-code training-only rule selection and untouched holdout.
        spec=ROOT/"examples/strategy_rules_SYNTHETIC.json"
        strategy=self.cli("strategy-build","--csv",self.history,
                          "--symbol","DEMO.NS","--inputs",spec)
        self.assertEqual(strategy["symbol"],"DEMO.NS")
        self.assertEqual(strategy["source_sha256"],self.digest)
        self.assertIn("holdout",str(strategy).lower())
        # Step 2: model benchmark using only past data, not a fictitious model.
        forecast=self.cli("kronos-eval","--csv",self.history,"--symbol","DEMO.NS",
                          "--backend","persistence","--lookback","128",
                          "--horizon","5","--origins","12","--stride","5")
        self.assertEqual(forecast["source_sha256"],self.digest)
        self.assertEqual(forecast["source_quality"],"SYNTHETIC_FIXTURE")
        self.assertFalse(forecast["model_weights_loaded"])
        self.assertFalse(forecast["broker_order_authority"])
        self.assertEqual(forecast["scores"]["challenger"]["n"],60)
        receipt=self.folder/"forecast.json"
        receipt.write_text(json.dumps(forecast),encoding="utf-8")
        # Step 3: output-bound hypothetical long/flat with explicit cost cases.
        paper=self.cli("kronos-paper","--csv",self.history,"--symbol","DEMO.NS",
                       "--report",receipt,"--permutations","100")
        self.assertEqual(paper["source_sha256"],self.digest)
        self.assertEqual(paper["broker_orders"],0)
        self.assertFalse(paper["trade_execution"])
        self.assertEqual(paper["source_quality"],"SYNTHETIC_FIXTURE")
        # Step 4: honest chart uses real rows (here labelled synthetic).
        chart=self.folder/"analysis.html"
        plotted=self.cli("chart","--csv",self.history,"--symbol","DEMO.NS",
                         "--out",chart,"--format","html")
        self.assertTrue(chart.is_file())
        self.assertFalse(plotted["exchange_live"])
        self.assertIn("SYNTHETIC",chart.read_text().upper())
        # Step 5: visual narrative receives the SAME source hash, no fabricated video.
        film=self.cli("film","--csv",self.history,"--symbol","DEMO.NS",
                      "--out",self.folder/"film","--storyboard-only",
                      "--seconds","6","--fps","6")
        self.assertIsNone(film["video"])
        self.assertEqual(film["source_sha256"],self.digest)
        board=json.loads(Path(film["storyboard"]).read_text())
        self.assertEqual(board["source_sha256"],self.digest)
        self.assertFalse(board["calibrated_prediction"])
        self.assertEqual(board["trade_recommendation"],"NONE")
        # Step 6: separately bounded hypothetical credit-spread maths;
        #         no fake derivation of option chain from spot Kronos.
        option=self.cli("options-sim","--inputs",
                        ROOT/"examples/options_put_credit_SYNTHETIC.json")
        self.assertEqual(option["data_quality"],"SYNTHETIC_FIXTURE")
        self.assertFalse(option["observed_options_chain"])
        self.assertFalse(option["trading_authority"])
        self.assertGreater(option["geometry"]["max_model_loss_inr"],0)
        # Step 7: never overwrite an existing rendered report.
        err=self.cli("chart","--csv",self.history,"--symbol","DEMO.NS",
                     "--out",chart,"--format","html",expected=2)
        self.assertTrue("exist" in err.lower() or "new" in err.lower())
        # This is not a successful broker login, option-chain proof or ML alpha.
        self.assertNotIn("PLACE_ORDER",json.dumps({"strategy":strategy,"forecast":forecast,
                       "paper":paper,"options":option},default=str).upper())
    def test_mismatched_source_cannot_be_laundered_through_paper_or_film(self):
        result=self.cli("kronos-eval","--csv",self.history,"--symbol","DEMO.NS",
                        "--lookback","120","--horizon","5","--origins","5","--stride","5")
        paperfile=self.folder/"forecast.json"
        paperfile.write_text(json.dumps(result),encoding="utf-8")
        # Deliberately mutate an observed candle after model scoring.
        with self.history.open("a",encoding="utf-8") as f:
            f.write("2026-09-01,DEMO.NS,100,101,99,100,20000,SYNTHETIC_FIXTURE\n")
        result=self.cli("kronos-paper","--csv",self.history,"--symbol","DEMO.NS",
                 "--report",paperfile,expected=2)
        self.assertIn("SHA",result)
    def test_unauthorized_broker_import_does_not_imply_real_verified_market(self):
        # A valid-looking external result file alone CANNOT authenticate a brokerage.
        from fundtex_india.kite_mcp_research import normalize_daily_history
        rows=[]
        for i in range(55):
            d=(date(2026,1,1)+timedelta(days=i)).isoformat()
            rows.append([d+"T09:15:00+05:30",101+i,103+i,100+i,102+i,11000+i])
        normalized=normalize_daily_history({"data":{"candles":rows}},"INFY.NS",
                         instrument_token=408065,requested_from="2026-01-01",
                         requested_through="2026-03-31")
        self.assertFalse(normalized["instrument_token_independently_verified"])
        self.assertFalse(normalized["trading_authority"])
        self.assertFalse(normalized["adjustments_verified"])
        self.assertEqual(normalized["data_quality"],
          "USER_APPROVED_KITE_MCP_PAYLOAD_NOT_EXCHANGE_SIGNED")

if __name__=="__main__":unittest.main()
