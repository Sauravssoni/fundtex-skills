"""Kronos paper-only falsification: no broker call, cross-source guard, next-open causality."""
import csv,json
from datetime import date,timedelta
from pathlib import Path
import subprocess,sys,tempfile,unittest
from fundtex_india.kronos_lab import evaluate
from fundtex_india.kronos_paper import assess

class PaperTests(unittest.TestCase):
 def setUp(self):
    self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
    self.p=Path(self.tmp.name)/"history.csv"
    with self.p.open("w",newline="") as f:
        w=csv.writer(f);w.writerow(("date","symbol","open","high","low","close","volume","source"))
        for i in range(220):
            close=100+0.13*i+(i%7)*0.15
            w.writerow(((date(2026,1,1)+timedelta(days=i)).isoformat(),"DEMO.NS",
                      close-0.2,close+0.8,close-0.7,close,1000+i,"SYNTHETIC_FIXTURE"))
    self.report=evaluate(self.p,"DEMO.NS",backend=lambda past,dt:[past[-1]["close"]*1.01]*len(dt),
              lookback=120,horizon=3,origins=8,stride=3)
 def test_no_order_retro_signal_and_cost_effect(self):
    a=assess(self.report,self.p,"DEMO.NS",threshold_bps=0,permutations=250)
    self.assertEqual(a["broker_orders"],0)
    self.assertFalse(a["trade_execution"])
    self.assertTrue(all(x["signal"]=="HYPOTHETICAL_LONG" for x in a["decision_windows"]))
    self.assertEqual(a["windows"],8)
    self.assertEqual(a["cost_scenarios"][0]["assumed_roundtrip_cost_bps"],0)
    self.assertLess(a["cost_scenarios"][2]["kronos_long_cash"]["compounded_window_return"],
                    a["cost_scenarios"][0]["kronos_long_cash"]["compounded_window_return"])
    self.assertEqual(a["source_quality"],"SYNTHETIC_FIXTURE")
    self.assertTrue(a["pretrained_contamination_unknown"])
 def test_hold_cash_when_threshold_higher_than_forecast(self):
    a=assess(self.report,self.p,"DEMO.NS",threshold_bps=300,permutations=10)
    self.assertEqual(a["model_long_windows"],0)
    self.assertEqual(a["cost_scenarios"][2]["kronos_long_cash"]["compounded_window_return"],0)
 def test_input_changed_after_predictions_refused(self):
    with self.p.open("a") as f:f.write("2026-09-01,DEMO.NS,1,1,1,1,1,SYNTHETIC_FIXTURE\n")
    with self.assertRaisesRegex(ValueError,"Source SHA"):
        assess(self.report,self.p,"DEMO.NS")
 def test_duplicate_or_overlapping_windows_never_paper_traded(self):
    r=dict(self.report);r["cutoff_diagnostics"]=[dict(x) for x in self.report["cutoff_diagnostics"]]
    r["cutoff_diagnostics"][1]["first_outcome"]=r["cutoff_diagnostics"][0]["first_outcome"]
    with self.assertRaisesRegex(ValueError,"Overlapping|noncausal"):
        assess(r,self.p,"DEMO.NS")
 def test_agent_cli_report_matches_source_and_never_sends_order(self):
    file=Path(self.tmp.name)/"report.json"
    file.write_text(json.dumps(self.report))
    root=Path(__file__).resolve().parents[1]
    cmd=[sys.executable,"-m","fundtex_india.cli","kronos-paper",
         "--report",str(file),"--csv",str(self.p),"--symbol","DEMO.NS",
         "--permutations","100"]
    p=subprocess.run(cmd,cwd=root,capture_output=True,text=True,timeout=20)
    self.assertEqual(p.returncode,0,p.stderr)
    j=json.loads(p.stdout)
    self.assertEqual(j["broker_orders"],0)
    self.assertEqual(j["shuffle_null"]["permutations"],100)
    self.assertIn("NOT_EXECUTABLE",j["conclusion"])

if __name__=="__main__":unittest.main()
