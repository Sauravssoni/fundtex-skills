"""Optional explicit million-path numerical stress test (no investment-skill claim)."""
import os
import time
import unittest
from pathlib import Path
from fundtex_india.market import csv_prices
from fundtex_india.simulate import simulate
from fundtex_india.options_lab import evaluate as option_evaluate
import json

class MillionPathTest(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("RUN_MILLION_TEST")=="1","RUN_MILLION_TEST=1 for one-million-path stress run")
    def test_one_million_seeded_paths(self):
        rows=csv_prices(str(Path(__file__).resolve().parents[1]/"examples"/"india_prices.csv"),"RELIANCE.NS")["rows"]
        start=time.perf_counter()
        result=simulate(rows, paths=1_000_000, horizon=1, seed=42)
        elapsed=time.perf_counter()-start
        print(f"Fundtex 1,000,000 synthetic draws in {elapsed:.2f}s; p05={result['return_p05']:.6f}; p95={result['return_p95']:.6f}")
        self.assertEqual(result["paths"],1_000_000)
        self.assertGreaterEqual(result["expected_shortfall95_loss_inr"],result["var95_loss_inr"])
        self.assertTrue(0 <= result["loss_probability"] <= 1)

    @unittest.skipUnless(os.environ.get("RUN_MILLION_TEST")=="1",
                         "RUN_MILLION_TEST=1 for one-million-options-path stress run")
    def test_one_million_options_payoff_paths(self):
        example=Path(__file__).resolve().parents[1]/"examples"/"options_put_credit_SYNTHETIC.json"
        params=json.loads(example.read_text())
        params["paths"]=1_000_000
        start=time.perf_counter()
        outcome=option_evaluate(params)
        elapsed=time.perf_counter()-start
        q=outcome["scenario_simulation"]
        self.assertEqual(q["paths"],1_000_000)
        self.assertFalse(outcome["trading_authority"])
        self.assertFalse(outcome["observed_options_chain"])
        self.assertEqual(outcome["data_quality"],"SYNTHETIC_FIXTURE")
        lo,hi=q["monte_carlo_sampling_only_95pct_interval"]["positive_pnl_frequency_wilson"]
        self.assertLessEqual(lo,q["probability_positive_model_pnl"])
        self.assertGreaterEqual(hi,q["probability_positive_model_pnl"])
        self.assertGreaterEqual(q["mean_model_pnl_inr"],-outcome["geometry"]["max_model_loss_inr"])
        self.assertLessEqual(q["mean_model_pnl_inr"],outcome["geometry"]["max_model_profit_inr"])
        print(f"Fundtex option payoff: 1,000,000 fictional paths in {elapsed:.2f}s; mean={q['mean_model_pnl_inr']} INR; calibrated_alpha=NO")

