"""CLI and opt-in MCP routing contracts for options, strategy and discovery."""
from __future__ import annotations
from pathlib import Path
from datetime import date,timedelta
from unittest.mock import patch
import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from fundtex_india import mcp_server
from fundtex_india.integrations import catalog

ROOT=Path(__file__).resolve().parents[1]

class StrategyCliAndMCP(unittest.TestCase):
    def _cli(self,*args):
        r=subprocess.run([sys.executable,"-m","fundtex_india.cli",*map(str,args)],
                         cwd=ROOT,capture_output=True,text=True,timeout=20)
        self.assertEqual(r.returncode,0,r.stderr)
        return json.loads(r.stdout)
    def test_integrations_presence_is_not_account_authorization(self):
        with patch.dict(os.environ,{"FUNDTEX_FYERS_APP_ID":"mock_id","FUNDTEX_FYERS_ACCESS_TOKEN":"mock_private"},clear=False):
            d=self._cli("integrations")
            self.assertFalse(d["accounts_connected_verified"])
            self.assertFalse(d["orders_enabled"])
            self.assertTrue(d["broker_local_credential_presence_not_authentication"]["fyers"])
            self.assertNotIn("mock_private",json.dumps(d))
            self.assertTrue(all(not r["connection_verified"] for r in d["connectors"]))
    def test_options_synthetic_example_never_live_market(self):
        report=self._cli("options-sim","--inputs",ROOT/"examples/options_put_credit_SYNTHETIC.json")
        self.assertEqual(report["data_quality"],"SYNTHETIC_FIXTURE")
        self.assertFalse(report["observed_options_chain"])
        self.assertFalse(report["trading_authority"])
        self.assertEqual(report["scenario_simulation"]["paths"],10000)
    def test_mcp_refuses_unauthorized_and_symlink_escape(self):
        with patch.dict(os.environ,{"FUNDTEX_APPROVED_DATA_DIR":""}):
            with self.assertRaises(ValueError):mcp_server.tools_logic()["options"]("options.json")
        with tempfile.TemporaryDirectory() as root:
            (Path(root)/"options.json").write_text((ROOT/"examples/options_put_credit_SYNTHETIC.json").read_text())
            with patch.dict(os.environ,{"FUNDTEX_APPROVED_DATA_DIR":root}):
                r=mcp_server.tools_logic()["options"]("options.json")
                self.assertFalse(r["trading_authority"])
                with self.assertRaises((ValueError,FileNotFoundError)):
                    mcp_server.tools_logic()["options"]("../outside.json")
                self.assertIn("strategy",mcp_server.tools_logic())
    def test_mcp_strategy_approved_local_only(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);csv_path=p/"prices.csv";cfg=p/"rules.json"
            cfg.write_text((ROOT/"examples/strategy_rules_SYNTHETIC.json").read_text())
            initial=date(2024,1,1);price=100.0
            with csv_path.open("w",newline="") as f:
                w=csv.writer(f);w.writerow(["date","symbol","open","high","low","close","volume","source"])
                for i in range(380):
                    price*=1+(.005 if (i//40)%2==0 else -.003)
                    w.writerow([(initial+timedelta(days=i)).isoformat(),"TEST.NS",
                                price*.999,price*1.002,price*.998,price,20000,"SYNTHETIC_FIXTURE"])
            with patch.dict(os.environ,{"FUNDTEX_APPROVED_DATA_DIR":td}):
                r=mcp_server.tools_logic()["strategy"]("prices.csv","rules.json","TEST.NS")
                self.assertTrue(r["test_period_untouched_during_selection"])
                self.assertFalse(r["trading_authority"])
                q=self._cli("strategy-build","--csv",csv_path,"--symbol","TEST.NS","--inputs",cfg)
                self.assertEqual(r["holdout"],q["holdout"])

if __name__=="__main__":
    unittest.main()
