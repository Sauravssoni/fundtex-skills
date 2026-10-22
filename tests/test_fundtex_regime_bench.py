"""Adversarial market-regime bench tests."""
import unittest
from fundtex_india.regime_bench import simulate_regimes,REGIMES

class RegimeBenchTests(unittest.TestCase):
    def test_seeded_multi_regime_falsification(self):
        a=simulate_regimes(scenarios_per_regime=2,seed=17,sessions=540)
        b=simulate_regimes(scenarios_per_regime=2,seed=17,sessions=540)
        self.assertEqual(a,b)
        self.assertEqual(a["total_independent_synthetic_histories"],10)
        self.assertEqual(a["total_training_rule_evaluations"],30)
        self.assertFalse(a["trading_authority"])
        self.assertEqual(a["market_data_provenance"],"SYNTHETIC_FIXTURE_ONLY")
        self.assertEqual(set(a["regimes"]),set(REGIMES))
    def test_invalid_bounds(self):
        for overrides in ({"scenarios_per_regime":0},{"sessions":50},
                          {"cost_bps":float("nan")},{"seed":True}):
            with self.subTest(overrides=overrides),self.assertRaises(ValueError):
                simulate_regimes(**overrides)

if __name__=="__main__":
    unittest.main()
