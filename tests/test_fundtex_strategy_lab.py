import csv
import tempfile
import unittest
from datetime import date,timedelta
from pathlib import Path
from fundtex_india.strategy_lab import run

class StrategyResearchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.csv=Path(self.tmp.name)/"prices.csv"
        self.rows=[]
        start=date(2024,1,1)
        price=100.
        for i in range(380):
            # Fictional alternating bull/bear regimes, no claim of actual profit.
            price*=1+(0.006 if (i//55)%2==0 else -0.004)
            o=price*0.999
            c=price
            self.rows.append((start+timedelta(days=i),o,max(o,c)*1.002,min(o,c)*.998,c,10000+i))
        self.write()
        self.spec={"candidates":[{"name":"sma_cross","fast":10,"slow":50},{"name":"sma_cross","fast":20,"slow":80}],
                   "split_fraction":.7,"cost_bps_per_position_change":15}
    def write(self):
        with self.csv.open("w",newline="") as fh:
            w=csv.writer(fh);w.writerow(["date","symbol","open","high","low","close","volume","source"])
            for d,o,h,l,c,v in self.rows:
                w.writerow([d.isoformat(),"TEST.NS",o,h,l,c,v,"SYNTHETIC_FIXTURE"])
    def test_train_only_selection_and_heldout_reproducibility(self):
        a=run(self.csv,"TEST.NS",self.spec)
        b=run(self.csv,"TEST.NS",self.spec)
        self.assertEqual(a,b)
        self.assertTrue(a["test_period_untouched_during_selection"])
        self.assertEqual(a["data_quality"],"SYNTHETIC_FIXTURE")
        self.assertGreater(a["holdout"]["sessions"],40)
        self.assertEqual(a["selected_from_trials"],2)
        self.assertFalse(a["trading_authority"])
    def test_no_fake_line_fill(self):
        with self.csv.open("w") as fh:
            fh.write("date,symbol,close\n")
            for day,_,_,_,c,_ in self.rows:
                fh.write(f"{day.isoformat()},TEST.NS,{c}\n")
        with self.assertRaisesRegex(ValueError,"Genuine open"):run(self.csv,"TEST.NS",self.spec)
    def test_invalid_search_or_negative_cost(self):
        self.spec["candidates"]=[{"name":"python","code":"__import__('os').system('foo')"}]
        with self.assertRaises(ValueError):run(self.csv,"TEST.NS",self.spec)
        self.spec["candidates"]=[{"name":"sma_cross","fast":10,"slow":50}]
        self.spec["cost_bps_per_position_change"]=-1
        with self.assertRaises(ValueError):run(self.csv,"TEST.NS",self.spec)
    def test_no_strategy_can_use_future_prices_for_training(self):
        one=run(self.csv,"TEST.NS",self.spec)
        cut=int(len(self.rows)*.7)
        for i in range(cut,len(self.rows)):
            d,o,h,l,c,v=self.rows[i]
            self.rows[i]=(d,o*1.1,h*1.1,l*1.1,c*1.1,v)
        self.write()
        two=run(self.csv,"TEST.NS",self.spec)
        self.assertEqual(one["optimized_rule"],two["optimized_rule"])
        self.assertEqual(one["candidate_train_scores"],two["candidate_train_scores"])
        self.assertNotEqual(one["holdout"]["net_total_return"],two["holdout"]["net_total_return"])
if __name__=="__main__":
    unittest.main()
