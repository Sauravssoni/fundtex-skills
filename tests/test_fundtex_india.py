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
from fundtex_india.portfolio import evaluate_portfolio
from fundtex_india.godeye import walkforward, signal

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
        self.assertAlmostEqual(pct_changes([100,110])[0], 0.1)

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


class FundtexPortfolioTest(unittest.TestCase):
    def test_portfolio_covariance_and_concentration(self):
        result=evaluate_portfolio(ROOT/"examples"/"portfolio_prices.csv",ROOT/"examples"/"holdings.csv")
        self.assertEqual(result["common_price_dates"], 200)
        self.assertAlmostEqual(result["hhi"],0.38)
        self.assertAlmostEqual(sum(result["variance_risk_contribution_fraction"].values()),1.0,places=6)
        self.assertEqual(result["sectors"]["Banking"],0.2)
        self.assertGreater(result["portfolio_annualized_volatility"],0)
        self.assertEqual(result["data_quality"],"USER_SUPPLIED_UNVERIFIED")

    def test_missing_symbols_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"Missing asset"):
            evaluate_portfolio(ROOT/"examples"/"india_prices.csv",ROOT/"examples"/"holdings.csv")

    def test_cli_portfolio_json(self):
        p=subprocess.run([sys.executable,"-m","fundtex_india.cli","portfolio","--prices",str(ROOT/"examples"/"portfolio_prices.csv"),
            "--holdings",str(ROOT/"examples"/"holdings.csv")],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr)
        result=json.loads(p.stdout)
        self.assertTrue(result["research_only"])
        self.assertEqual(len(result["weights"]),3)


class GodEyeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=csv_prices(str(FIXTURE),"RELIANCE.NS")["rows"]

    def test_god_eye_walkforward_deterministic(self):
        a=walkforward(self.rows)
        self.assertEqual(a,walkforward(self.rows))
        self.assertEqual(a["out_of_sample_days"],len(self.rows)-121)
        self.assertIn(a["latest_hypothesis"],("ABSTAIN_CASH","LONG_RESEARCH_ONLY"))
        self.assertFalse(a["assurance"]["independent_live_validation"])

    def test_no_lookahead_in_decisions(self):
        original=walkforward(self.rows)
        modified=[dict(row) for row in self.rows]
        modified[-1]["close"]=float(modified[-1]["close"])*1.15
        amended=walkforward(modified)
        # At least the model-selection score at day T-1 cannot use the
        # day-T closing price; only the realized return changes.
        self.assertEqual(original["active_days"],amended["active_days"])

    def test_god_eye_invalid_parameters(self):
        with self.assertRaises(ValueError):
            walkforward(self.rows,cost_bps=-1)
        with self.assertRaises(ValueError):
            walkforward(self.rows,min_train=120,lookback=100)

    def test_god_eye_cli_json(self):
        p=subprocess.run([sys.executable,"-m","fundtex_india.cli","godeye","--csv",str(FIXTURE),
                          "--symbol","RELIANCE.NS"],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr)
        j=json.loads(p.stdout)
        self.assertEqual(j["symbol"],"RELIANCE.NS")
        self.assertEqual(j["data_quality"],"USER_SUPPLIED_UNVERIFIED")

if __name__ == "__main__":
    unittest.main()
