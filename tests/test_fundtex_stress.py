"""Deterministic and bounded adverse market-regime contract tests."""
import json
import subprocess
import sys
import unittest
from pathlib import Path
from fundtex_india.eval_suite import make_scenario,stress_suite,REGIMES
ROOT=Path(__file__).resolve().parents[1]

class StressTest(unittest.TestCase):
    def test_generated_scenarios_deterministic(self):
        for mode in REGIMES:
            a=make_scenario(mode,sessions=400,seed=7)
            self.assertEqual(a,make_scenario(mode,sessions=400,seed=7))
            self.assertEqual(len(a),400)
            self.assertTrue(all(r["close"]>0 for r in a))

    def test_eval_does_not_claim_market_data_or_alpha(self):
        result=stress_suite(scenarios=6,sessions=400,seed=32)
        self.assertEqual(result,stress_suite(scenarios=6,sessions=400,seed=32))
        self.assertEqual(result["source"],"SYNTHETIC_GENERATOR_NOT_MARKET_DATA")
        self.assertEqual(result["total_synthetic_observations"],2400)
        self.assertEqual(result["total_prequential_forecast_scores"],6*(400-120-1))
        self.assertEqual(sum(v["scenarios"] for v in result["by_regime"].values()),6)
        self.assertEqual(result["research_gates_passed"]+result["research_gates_failed"],6)

    def test_bad_settings_fail_closed(self):
        with self.assertRaises(ValueError): stress_suite(scenarios=7)
        with self.assertRaises(ValueError): stress_suite(scenarios=6,sessions=300)

    def test_cli_eval(self):
        p=subprocess.run([sys.executable,"-m","fundtex_india.cli","evaluate","--scenarios","6","--sessions","400","--seed","7"],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout)["parameters"]["scenarios"],6)

if __name__=="__main__":
    unittest.main()
