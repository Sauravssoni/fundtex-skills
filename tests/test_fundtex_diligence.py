"""Realistic professional diligence arithmetic checks using fictional data only."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

from fundtex_india.diligence import analyze, from_json, render_markdown

ROOT=Path(__file__).resolve().parents[1]


class FinancialDiligenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.company=from_json(ROOT/"examples/india_company_diligence_SYNTHETIC.json")
        cls.bank=from_json(ROOT/"examples/india_bank_diligence_SYNTHETIC.json")

    def test_manufacturing_financials_and_fraud_questions(self):
        d=self.company
        self.assertEqual(d["data_quality"],"SYNTHETIC_FIXTURE")
        self.assertAlmostEqual(d["derived_metrics"]["revenue_growth_yoy"],.25)
        self.assertEqual(d["derived_metrics"]["free_cash_flow"],-68.)
        self.assertEqual(d["derived_metrics"]["net_debt"],650.)
        self.assertAlmostEqual(d["derived_metrics"]["net_debt_to_ebitda"],650./140.,places=6)
        self.assertGreaterEqual(len(d["forensic_questions"]),3)
        self.assertIsNone(d["investment_recommendation"])
        self.assertIn("DEMONSTRATION",render_markdown(d).upper())

    def test_lender_sector_specific_metrics(self):
        d=self.bank
        self.assertEqual(d["classification"],"bank_or_nbfc")
        self.assertAlmostEqual(d["derived_metrics"]["gross_npa_pct_change_pp"],-.4)
        self.assertAlmostEqual(d["derived_metrics"]["credit_cost_pct_change_pp"],.3)
        self.assertNotIn("net_debt_to_ebitda",d["derived_metrics"])

    def test_source_requires_https_and_no_claim_of_authentication(self):
        raw=json.loads((ROOT/"examples/india_company_diligence_SYNTHETIC.json").read_text())
        raw["data_quality"]="USER_SUPPLIED_UNVERIFIED"
        raw["sources"]=[{"title":"Test primary filing","published_at":"2026-10-01","url":"https://example.invalid/primary"}]
        r=analyze(raw)
        self.assertFalse(r["sources"][0]["independently_verified"])
        raw["sources"][0]["url"]="http://example.invalid/bad"
        with self.assertRaises(ValueError):
            analyze(raw)

    def test_invalid_financial_figures_fail_closed(self):
        raw=json.loads((ROOT/"examples/india_company_diligence_SYNTHETIC.json").read_text())
        raw["current"]["revenue"]="NaN"
        with self.assertRaises(ValueError):
            analyze(raw)
        raw["current"]["revenue"]=True
        with self.assertRaises(ValueError):
            analyze(raw)
        raw["current"]["revenue"]=20
        raw["current"]["unknown_future_metric"]=30
        with self.assertRaises(ValueError):
            analyze(raw)

    def test_cli_json_markdown_diligence(self):
        path=str(ROOT/"examples/india_company_diligence_SYNTHETIC.json")
        for fmt in ("json","markdown"):
            p=subprocess.run([sys.executable,"-m","fundtex_india.cli","diligence",
                              "--inputs",path,"--format",fmt],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertIn("ILLUSTRATIVE",p.stdout)
            if fmt=="json":
                self.assertEqual(json.loads(p.stdout)["type"],"INDIA_FUNDAMENTAL_DILIGENCE")
            else:
                self.assertIn("Financial checks",p.stdout)

if __name__=="__main__":
    unittest.main()
