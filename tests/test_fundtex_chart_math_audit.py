"""Independent chart math guards for Fundtex release audit."""
import unittest
from fundtex_india.chart_studio import rsi,sma,ema,indicators

class ChartMathAudit(unittest.TestCase):
    def test_flat_rsi_is_neutral_not_buy_pressure(self):
        self.assertEqual(rsi([100.0]*60)[-1],50.)
    def test_rising_falling_rsi_extremes(self):
        self.assertEqual(rsi([float(100+i) for i in range(60)])[-1],100.)
        self.assertEqual(rsi([float(100-i) for i in range(60)])[-1],0.)
    def test_simple_mean_and_warmup(self):
        r=sma([1.,2.,3.,4.,5.],3)
        self.assertEqual(r[:2],[None,None])
        self.assertEqual(r[2:],[2.,3.,4.])
    def test_ema_constant_input(self):
        self.assertEqual(ema([200.]*60,12),[200.]*60)
    def test_sma_crossover_never_before_50_sessions(self):
        rows=[{"date":f"2026-01-{(i%28)+1:02d}","close":100.+i,"volume":100}
              for i in range(60)]
        d=indicators({"rows":rows})
        self.assertTrue(all(x["not_investment_signal"] for x in d["events"]))
        self.assertIsNone(d["sma50"][48])
        self.assertIsNotNone(d["sma50"][49])

if __name__=="__main__":unittest.main()
