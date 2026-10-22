import csv
import tempfile
import unittest
from pathlib import Path
from fundtex_india.options_builder import propose
class SpreadBuilderTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.path=Path(self.t.name)/"chain.csv"
        self.rows=[
            ["NIFTY","2026-10-29","put",24600,60,65,75,"2026-10-23"],
            ["NIFTY","2026-10-29","put",24800,100,108,75,"2026-10-23"],
            ["NIFTY","2026-10-29","put",25000,150,158,75,"2026-10-23"],
            ["NIFTY","2026-10-29","call",25000,170,175,75,"2026-10-23"],
            ["NIFTY","2026-10-29","call",25200,105,115,75,"2026-10-23"],
            ["NIFTY","2026-10-29","call",25400,70,82,75,"2026-10-23"],
        ]
        self.write()
        self.cfg={"underlying":"NIFTY","spot":25000,"lot_size":75,"valuation_date":"2026-10-23",
                  "expiry_date":"2026-10-29","structure":"bull_put_credit",
                  "min_width":150,"max_width":400,"max_risk_inr":35000,"top_n":5}
    def write(self):
        with self.path.open("w",newline="") as h:
            w=csv.writer(h);w.writerow(["symbol","expiry","kind","strike","bid","ask","lot_size","as_of"]);w.writerows(self.rows)
    def test_put_credit_scanner_uses_conservative_bid_ask(self):
        r=propose(self.path,self.cfg)
        self.assertTrue(r["eligible_candidates"])
        self.assertEqual(r["quote_data_quality"],"USER_SUPPLIED_OPTIONS_CHAIN_UNVERIFIED")
        self.assertFalse(r["licensed_quote_verified"])
        self.assertFalse(r["trading_authority"])
        a=r["eligible_candidates"][0]
        self.assertGreater(a["short_strike"],a["long_strike"])
        self.assertGreater(a["max_model_loss_inr"],0)
    def test_call_credit_and_risk_budget(self):
        self.cfg["structure"]="bear_call_credit"
        self.assertTrue(propose(self.path,self.cfg)["eligible_candidates"])
        self.cfg["max_risk_inr"]=100
        self.assertEqual(propose(self.path,self.cfg)["eligible_candidates"],[])
    def test_cli_and_mcp_share_same_result(self):
        import json,os,subprocess,sys
        from unittest.mock import patch
        from fundtex_india import mcp_server
        cfg_path=Path(self.t.name)/"spread.json"
        cfg_path.write_text(json.dumps(self.cfg))
        from pathlib import Path as P
        home=P(__file__).resolve().parents[1]
        x=subprocess.run([sys.executable,"-m","fundtex_india.cli","options-build",
                          "--chain",str(self.path),"--inputs",str(cfg_path)],
                         cwd=home,text=True,capture_output=True,timeout=12)
        self.assertEqual(x.returncode,0,x.stderr)
        out=json.loads(x.stdout)
        self.assertFalse(out["trading_authority"])
        with patch.dict(os.environ,{"FUNDTEX_APPROVED_DATA_DIR":self.t.name}):
            mcp=mcp_server.tools_logic()["option_builder"]("chain.csv","spread.json")
        self.assertEqual(out,mcp)
    def test_quote_date_and_market_ba_rejected(self):
        self.rows[0][-1]="2026-10-12";self.write()
        with self.assertRaisesRegex(ValueError,"stale"):propose(self.path,self.cfg)
        self.rows[0][-1]="2026-10-23";self.rows[0][4]=90;self.rows[0][5]=80;self.write()
        with self.assertRaisesRegex(ValueError,"bid/ask"):propose(self.path,self.cfg)
    def test_lot_mismatch_and_duplicate_contract(self):
        self.rows[0][6]=100;self.write()
        with self.assertRaisesRegex(ValueError,"lot-size"):propose(self.path,self.cfg)
        self.rows[0][6]=75;self.rows.append(self.rows[0][:]);self.write()
        with self.assertRaisesRegex(ValueError,"Duplicate"):propose(self.path,self.cfg)
if __name__=="__main__":
    unittest.main()
