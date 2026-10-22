"""Synthetic offline evidence-reconciliation tests; never real market data."""
import tempfile
import unittest
from datetime import date,timedelta
from pathlib import Path
from fundtex_india.reconcile import reconcile

class ReconcileTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.p=Path(self.t.name)/"feed-a.csv"
        self.q=Path(self.t.name)/"feed-b.csv"
        self._write(self.p,[100+i*0.2 for i in range(35)])
        self._write(self.q,[100+i*0.2 for i in range(35)])
    def _write(self,path,values):
        start=date(2025,1,1)
        path.write_text("date,symbol,close,source\n"+"".join(
            f"{(start+timedelta(days=i)).isoformat()},TEST.NS,{v},SYNTHETIC_FIXTURE\n" for i,v in enumerate(values)),encoding="utf-8")
    def test_agreement_is_not_certification(self):
        r=reconcile(self.p,self.q,"TEST.NS")
        self.assertEqual(r["status"],"NUMERICAL_AGREEMENT_ONLY")
        self.assertFalse(r["source_certified"])
        self.assertEqual(r["matched_dates"],35)
        self.assertEqual(r["max_symmetric_difference_bps"],0)
        self.assertEqual(r["primary"]["quality"],"SYNTHETIC_FIXTURE")
    def test_mismatch_is_flagged_not_hidden(self):
        values=[100+i*0.2 for i in range(35)]
        values[12]*=1.20
        self._write(self.q,values)
        r=reconcile(self.p,self.q,"TEST.NS")
        self.assertEqual(r["status"],"REVIEW_SOURCE_DISAGREEMENTS")
        self.assertEqual(r["mismatch_count"],1)
        self.assertGreater(r["max_symmetric_difference_bps"],25)
    def test_identical_file_rejected(self):
        with self.assertRaisesRegex(ValueError,"identical bytes"):reconcile(self.p,self.q,"TEST.NS")
    def test_no_forward_date_and_parameter_validation(self):
        with self.assertRaises(ValueError):reconcile(self.p,self.q,"TEST.NS",tolerance_bps=float("nan"))
        with self.assertRaises(ValueError):reconcile(self.p,self.p,"TEST.NS")
if __name__=="__main__":
    unittest.main()
