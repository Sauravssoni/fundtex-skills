"""Zero-network tests for institutional arithmetic and falsifiable lunar-cycle placebo."""
import unittest
from datetime import date, timedelta
from fundtex_india.institutional import investment_committee, lunar_placebo

class FundtexInstitutional(unittest.TestCase):
    def setUp(self):
        self.input = {"issuer":{"symbol":"INFY.NS","units":"INR_CRORE","per_share_currency":"INR","as_of":"2025-03-31","period":"FY25"},
            "financials":{"revenue":1000,"ebitda":250,"net_income":100,"cash_from_operations":70,"capital_expenditure":20,"total_debt":180,"cash_and_equivalents":40},
            "references":[{"url":"https://example.org/1","published":"2025-04-01"},{"url":"https://example.org/2","published":"2025-04-02"}],
            "scenarios":[{"name":"bear","probability":0.4,"value_per_share":60,"assumptions":"downside"},
                         {"name":"bull","probability":0.6,"value_per_share":160,"assumptions":"upside"}]}
    def test_arithmetic_and_verdict(self):
        r = investment_committee(self.input)
        self.assertEqual(r["ratios"]["free_cash_flow"], 50.0)
        self.assertEqual(r["ratios"]["net_debt"], 140.0)
        self.assertEqual(r["scenario_model"]["hypothetical_probability_weighted_value_per_share"],120.0)
        self.assertEqual(r["verdict"],"HUMAN_VERIFICATION_REQUIRED")
        self.assertEqual(r["risk_flags"], [])  # CFO/NI = 0.70; below-0.5 warning must NOT fire
    def test_synthetic_case_never_claims_real_fundamentals(self):
        self.input["provenance"]="SYNTHETIC_FIXTURE_FOR_ARITHMETIC_ONLY"
        self.assertEqual(investment_committee(self.input)["input_assurance"], "SYNTHETIC_FIXTURE")
    def test_share_currency_is_not_accounting_unit(self):
        self.input["issuer"].pop("per_share_currency")
        with self.assertRaisesRegex(ValueError,"per_share_currency"): investment_committee(self.input)
    def test_probability_reject(self):
        self.input["scenarios"][0]["probability"]=0.3
        with self.assertRaisesRegex(ValueError, "sum to one"): investment_committee(self.input)
    def test_actual_weak_cash_conversion_detected(self):
        self.input["financials"]["cash_from_operations"] = 40
        r = investment_committee(self.input)
        self.assertEqual(r["ratios"]["free_cash_flow"], 20.0)
        self.assertTrue(any("CFO/NI" in x for x in r["risk_flags"]))

    def test_future_and_nan_reject(self):
        self.input["financials"]["revenue"]=float("nan")
        with self.assertRaisesRegex(ValueError,"finite"): investment_committee(self.input)
        self.input["financials"]["revenue"]=1000
        self.input["issuer"]["as_of"]="2099-01-01"
        with self.assertRaisesRegex(ValueError,"future"): investment_committee(self.input)
    def test_placebo_is_reproducible_not_trading(self):
        start=date(2020,1,1)
        rows=[{"date":(start+timedelta(days=i)).isoformat(),"return":(i%9-4)/1000} for i in range(250)]
        a=lunar_placebo(rows,seed=7,permutations=100)
        self.assertEqual(a,lunar_placebo(rows,seed=7,permutations=100))
        self.assertEqual(a["verdict"],"EXPLORATORY_ONLY_NOT_A_TRADING_SIGNAL")
    def test_placebo_duplicate_reject(self):
        start=date(2020,1,1)
        rows=[{"date":(start+timedelta(days=i)).isoformat(),"return":0.01} for i in range(170)]
        rows[40]["date"]=rows[39]["date"]
        with self.assertRaisesRegex(ValueError,"Unique"): lunar_placebo(rows)

if __name__=="__main__":
    unittest.main()
