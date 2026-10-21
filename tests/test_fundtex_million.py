"""Optional explicit million-path numerical stress test (no investment-skill claim)."""
import os
import time
import unittest
from pathlib import Path
from fundtex_india.market import csv_prices
from fundtex_india.simulate import simulate

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
