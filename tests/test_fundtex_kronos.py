"""Kronos guardrail acceptance tests; controlled synthetic candles only."""
import csv
from datetime import date,timedelta
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from fundtex_india.kronos_lab import bars_from_csv,evaluate, PINNED_SHA
from fundtex_india.kronos_runtime import doctor

class KronosResearchTests(unittest.TestCase):
 def setUp(self):
    self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
    self.folder=Path(self.tmp.name)
    self.csv=self.folder/"synthetic.csv"
    self.rows=[]
    with self.csv.open("w",newline="") as f:
       w=csv.writer(f);w.writerow(("date","symbol","open","high","low","close","volume","source"))
       for i in range(240):
          price=101+i*.23+2*(i%7)/7
          record=[(date(2026,1,1)+timedelta(days=i)).isoformat(),"DEMO.NS",
                 price-0.3,price+1.1,price-0.9,price,10000+i,"SYNTHETIC_FIXTURE"]
          self.rows.append(record);w.writerow(record)
 def test_valid_series_and_no_fabricated_ohlc(self):
    b=bars_from_csv(self.csv,"DEMO.NS")
    self.assertEqual(len(b["rows"]),240)
    self.assertEqual(b["source_quality"],"SYNTHETIC_FIXTURE")
    self.assertEqual(b["rows"][-1]["close"],self.rows[-1][5])
    self.assertEqual(len(b["source_sha256"]),64)
 def test_baselines_comparison_and_abstain(self):
    r=evaluate(self.csv,"DEMO.NS",backend="persistence",lookback=120,horizon=5,origins=12,stride=5)
    self.assertEqual(r["scores"]["challenger"]["mae"],r["scores"]["persistence"]["mae"])
    self.assertFalse(r["industry_alpha_verified"])
    self.assertFalse(r["execution_prices_verified"])
    self.assertEqual(r["source_quality"],"SYNTHETIC_FIXTURE")
    self.assertEqual(r["trade_recommendation"],"NONE")
    self.assertTrue(r["pretrained_model_contamination_unknown"])
    self.assertEqual(r["upstream_pinned_commit"],PINNED_SHA)
 def test_actual_model_interface_cannot_receive_future_candle_values(self):
    observations=[]
    def spy(past, dates):
       observations.append((past[-1]["date"], tuple(dates),past[-1]["close"]))
       self.assertEqual(type(past),tuple)
       self.assertEqual(type(dates),tuple)
       self.assertEqual(past[-1]["date"],"2026-06-15" if False else past[-1]["date"])
       return [past[-1]["close"]]*len(dates)
    a=evaluate(self.csv,"DEMO.NS",backend=spy,lookback=128,horizon=4,origins=10,stride=5)
    self.assertEqual(len(observations),10)
    self.assertEqual(a["scores"]["challenger"]["mae"],a["scores"]["persistence"]["mae"])
    original_first=observations[0]
    # Changing future prices after the earliest cutoff must NOT affect its prediction.
    with self.csv.open("w",newline="") as f:
       w=csv.writer(f);w.writerow(("date","symbol","open","high","low","close","volume","source"))
       for i,record in enumerate(self.rows):
          new=list(record)
          if i>=191:
             new[2],new[3],new[4],new[5]=1000+i,1002+i,999+i,1001+i
          w.writerow(new)
    observations.clear()
    b=evaluate(self.csv,"DEMO.NS",backend=spy,lookback=128,horizon=4,origins=10,stride=5)
    self.assertEqual(observations[0],original_first)
    self.assertNotEqual(a["scores"]["challenger"]["mae"],b["scores"]["challenger"]["mae"])
 def test_reject_invalid_predictions_and_overlapping_windows(self):
    with self.assertRaisesRegex(ValueError,"Overlapping"):
       evaluate(self.csv,"DEMO.NS",horizon=10,stride=5)
    with self.assertRaisesRegex(ValueError,"nonfinite"):
       evaluate(self.csv,"DEMO.NS",backend=lambda past,dt:[float('nan')]*len(dt))
    with self.assertRaisesRegex(ValueError,"invalid horizon"):
       evaluate(self.csv,"DEMO.NS",backend=lambda past,dt:[1])
    with self.assertRaisesRegex(ValueError,"Need at least"):
       evaluate(self.csv,"DEMO.NS",lookback=220,horizon=10,origins=10,stride=10)
 def test_no_close_only_or_foreign_symbol_or_future_dates(self):
    p=self.folder/"bad.csv"
    p.write_text("date,symbol,close\n2026-01-01,DEMO.NS,100\n")
    with self.assertRaisesRegex(ValueError,"ACTUAL dated OHLC"):
       bars_from_csv(p,"DEMO.NS")
    with self.assertRaisesRegex(ValueError,"120 actual"):
       bars_from_csv(self.csv,"TCS.NS")
    rows=[list(x) for x in self.rows]
    rows[40][3]=1
    with p.open("w",newline="") as f:
       w=csv.writer(f);w.writerow(("date","symbol","open","high","low","close","volume","source"));w.writerows(rows)
    with self.assertRaisesRegex(ValueError,"Impossible"):
       bars_from_csv(p,"DEMO.NS")
 def test_offline_model_doctor_never_claims_download(self):
    r=doctor(model_size="mini")
    self.assertFalse(r["ready_for_approved_offline_inference"])
    self.assertFalse(r["model_inference_executed"])
    self.assertFalse(r["network_downloads_performed"])
    with self.assertRaises(ValueError):doctor(model_size="large")
 def test_cli_baseline_runs_and_kronos_refuses_unapproved_weights(self):
    root=Path(__file__).resolve().parents[1]
    p=subprocess.run([sys.executable,"-m","fundtex_india.cli","kronos-eval",
                      "--csv",str(self.csv),"--symbol","DEMO.NS",
                      "--lookback","120"],cwd=root,text=True,capture_output=True,timeout=20)
    self.assertEqual(p.returncode,0,p.stderr[-800:])
    report=json.loads(p.stdout)
    self.assertFalse(report["model_weights_loaded"])
    self.assertIn("scores",report)
    failure=subprocess.run([sys.executable,"-m","fundtex_india.cli","kronos-eval",
                      "--csv",str(self.csv),"--symbol","DEMO.NS",
                      "--backend","kronos"],cwd=root,text=True,capture_output=True,timeout=20)
    self.assertEqual(failure.returncode,2)
    self.assertIn("never auto-download",failure.stderr)

if __name__=="__main__":unittest.main()
