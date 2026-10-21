"""Offline contract tests; never require a broker or paid market-data credentials."""
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path
from fundtex_india.market import csv_prices, validate_rows, validate_symbol
from fundtex_india.stats import report, drawdown, pct_changes
from fundtex_india.simulate import simulate
from fundtex_india.valuation import dcf

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "india_prices.csv"

class FundtexIndiaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = csv_prices(str(FIXTURE), "RELIANCE.NS")

    def test_fixture_explicitly_unverified(self):
        self.assertEqual(self.data["quality"], "USER_SUPPLIED_UNVERIFIED")
        self.assertEqual(len(self.data["rows"]), 200)

    def test_symbol_safety(self):
        self.assertEqual(validate_symbol(" infy.ns "), "INFY.NS")
        for bad in ("AAPL", "../../x", "INFY.NS/../etc", "RELIANCE.NS?period=5y"):
            with self.assertRaises(ValueError): validate_symbol(bad)

    def test_duplicate_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_rows([{"date":"2025-01-01","close":2}, {"date":"2025-01-01","close":3}])

    def test_nonfinite_close_rejected(self):
        with self.assertRaises(ValueError):
            validate_rows([{"date":"2025-01-01","close":"nan"}, {"date":"2025-01-02","close":3}])

    def test_stats_has_expected_ranges(self):
        result = report(self.data["rows"])
        self.assertEqual(result["observations"],200)
        self.assertTrue(result["annualized_volatility"] > 0)
        self.assertLessEqual(result["maximum_drawdown"], 0)
        self.assertLessEqual(result["historical_expected_shortfall95_one_day_return"],result["historical_var95_one_day_return"])
        self.assertTrue(0 <= result["rsi14"] <= 100)

    def test_drawdown_exact(self):
        self.assertAlmostEqual(drawdown([10, 15, 12, 20, 10]), -0.5)
        self.assertEqual(pct_changes([100,110]), [0.1])

    def test_simulation_seed_reproducible(self):
        x = simulate(self.data["rows"],paths=1000,seed=7)
        y = simulate(self.data["rows"],paths=1000,seed=7)
        self.assertEqual(x,y)
        self.assertEqual(x["paths"],1000)
        self.assertTrue(0 <= x["loss_probability"] <= 1)
        self.assertLessEqual(x["return_p05"],x["return_p50"])
        self.assertLessEqual(x["return_p50"],x["return_p95"])

    def test_simulation_rejects_invalid_config(self):
        with self.assertRaises(ValueError): simulate(self.data["rows"],paths=3)
        with self.assertRaises(ValueError): simulate(self.data["rows"],paths=1000,horizon=0)
        with self.assertRaises(ValueError): simulate(self.data["rows"],paths=1000,position_inr=-50)

    def test_valuation_sensitivity(self):
        cfg = json.loads((ROOT/"examples"/"valuation.json").read_text())
        x = dcf(cfg)
        self.assertTrue(math.isfinite(x["scenario_value_inr_per_share"]))
        self.assertEqual(len(x["sensitivity"]),5)
        self.assertEqual(x["quality"],"USER_HYPOTHESIS_NOT_OBSERVED_MARKET_FACT")

    def test_valuation_rejects_bad_discount(self):
        cfg = json.loads((ROOT/"examples"/"valuation.json").read_text())
        cfg["terminal_growth"] = cfg["wacc"]
        with self.assertRaises(ValueError): dcf(cfg)

    def test_cli_read_only_json(self):
        p = subprocess.run([sys.executable,"-m","fundtex_india.cli","analyze","--csv",str(FIXTURE),
                            "--symbol","RELIANCE.NS"],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr)
        response=json.loads(p.stdout)
        self.assertTrue(response["research_only"])
        self.assertEqual(response["analysis"]["observations"],200)

    def test_cli_missing_source_does_not_make_up_quote(self):
        p = subprocess.run([sys.executable,"-m","fundtex_india.cli","analyze","--csv","/tmp/not-a-fundtex-file.csv",
                            "--symbol","RELIANCE.NS"],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(p.returncode,2)
        self.assertTrue(json.loads(p.stderr)["no_fallback_quote"])

if __name__ == "__main__":
    unittest.main()
