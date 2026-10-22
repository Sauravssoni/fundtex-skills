"""Pure-math options laboratory: synthetic premiums, no orders/data feed."""
import unittest
from fundtex_india.options_lab import evaluate
class OptionPayoffTests(unittest.TestCase):
    def setUp(self):
        self.base={"underlying":"NIFTY","spot":25000,"lot_size":75,
                   "valuation_date":"2026-10-23","expiry_date":"2026-10-29",
                   "legs":[{"kind":"put","side":"sell","strike":25000,"premium":150,"lots":1},
                           {"kind":"put","side":"buy","strike":24800,"premium":90,"lots":1}],
                   "annualized_volatility":0.20,"paths":1000,"seed":7}
    def test_credit_spread_gross_geometry_and_dated_stt(self):
        result=evaluate(self.base)
        fee=result["opening_total_cost_inr"]
        self.assertGreater(fee,0)
        self.assertEqual(result["opening_net_premium_credit_after_entry_fees_inr"] if "opening_net_premium_credit_after_entry_fees_inr" in result else result["net_initial_cash_flow_after_entry_fees_inr"],4500-round(fee,2))
        self.assertAlmostEqual(result["geometry"]["max_model_loss_inr"],10500+fee,delta=.01)
        self.assertAlmostEqual(result["geometry"]["max_model_profit_inr"],4500-fee,delta=.01)
        self.assertEqual(result["geometry"]["loss_unbounded_in_model"],False)
        self.assertTrue(24800 < result["geometry"]["break_even_underlying_prices"][0] < 25000)
        self.assertFalse(result["scenario_simulation"]["calibrated_probability_of_profit"])
        self.assertFalse(result["trading_authority"])
    def test_unhedged_short_call_fails_closed(self):
        self.base["legs"]=[{"kind":"call","side":"sell","strike":25000,"premium":200,"lots":1}]
        with self.assertRaisesRegex(ValueError,"unbounded"):evaluate(self.base)
        self.base["require_defined_risk"]=False
        r=evaluate(self.base)
        self.assertTrue(r["geometry"]["loss_unbounded_in_model"])
    def test_risk_budget_does_not_hide_expiry_costs(self):
        self.base["max_risk_inr"]=10000
        with self.assertRaisesRegex(ValueError,"risk budget"):evaluate(self.base)
    def test_reject_missing_lot_and_bad_inputs(self):
        self.base["lot_size"]=0
        with self.assertRaises(ValueError):evaluate(self.base)
        self.base["lot_size"]=75
        self.base["legs"][0]["premium"]=float("nan")
        with self.assertRaises(ValueError):evaluate(self.base)
    def test_scenario_uncertainty_is_conditional_only(self):
        report=evaluate(self.base)["scenario_simulation"]
        confidence=report["monte_carlo_sampling_only_95pct_interval"]
        p=report["probability_positive_model_pnl"]
        self.assertLessEqual(confidence["positive_pnl_frequency_wilson"][0],p)
        self.assertGreaterEqual(confidence["positive_pnl_frequency_wilson"][1],p)
        self.assertTrue(confidence["does_not_account_for_model_misspecification"])
        self.base["paths"]=1000001
        with self.assertRaises(ValueError):
            evaluate(self.base)

    def test_deterministic_scenario(self):
        one=evaluate(self.base)["scenario_simulation"]
        two=evaluate(self.base)["scenario_simulation"]
        self.assertEqual(one,two)
    def test_greeks_are_explicitly_theoretical(self):
        report=evaluate(self.base)
        g=report["illustrative_greeks"]
        self.assertIn("NOT_MARKET_GREEKS",g["status"])
        self.assertGreater(g["aggregate"]["delta_inr_per_underlying_point"],0)
        self.assertEqual(g["assumptions"]["annual_dividend_yield"],0.0)
    def test_greeks_zero_time_return_unavailable(self):
        self.base["expiry_date"]=self.base["valuation_date"]
        report=evaluate(self.base)
        self.assertEqual(report["illustrative_greeks"]["status"],"NOT_COMPUTABLE_ZERO_TIME_OR_VOLATILITY")
    def test_zero_volatility_and_no_fake_live_quote(self):
        self.base["annualized_volatility"]=0
        result=evaluate(self.base)
        self.assertFalse(result["observed_options_chain"])
        self.assertEqual(result["lot_size_user_verified"],False)
        self.assertEqual(result["scenario_simulation"]["p05_model_pnl_inr"],result["scenario_simulation"]["p95_model_pnl_inr"])
if __name__=="__main__":
    unittest.main()
