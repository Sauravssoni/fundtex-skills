"""Dhan v2 read-only quote normalization and conservative spread builder gates."""
import csv
from datetime import datetime,timezone,timedelta
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from fundtex_india.dhan_option_chain import (normalize, read_only_fetch,
                                               capture_to_files,verify_config)
from fundtex_india.options_builder import propose

STAMP=datetime(2026,10,23,6,10,tzinfo=timezone.utc)
CONFIG={"underlying":"NIFTY","underlying_scrip":13,"underlying_seg":"IDX_I",
        "expiry":"2026-10-29","lot_size":65,"max_strikes":4}

def mock_payload():
    oc={}
    for idx,strike in enumerate((24600,24800,25000,25200)):
        oc[f"{strike:.6f}"]={
         "ce":{"security_id":42000+idx*2,"top_bid_price":float(500-idx*90),
               "top_ask_price":float(510-idx*90),
               "top_bid_quantity":260,"top_ask_quantity":260,
               "volume":120000,"oi":400000},
         "pe":{"security_id":42001+idx*2,"top_bid_price":float(40+idx*45),
               "top_ask_price":float(45+idx*45),
               "top_bid_quantity":260,"top_ask_quantity":260,
               "volume":120000,"oi":400000}
        }
    return {"data":{"last_price":25000,"oc":oc},"status":"success"}

class DhanChainResearchTests(unittest.TestCase):
    def test_strict_snapshot_normalization_without_network(self):
        result=normalize(mock_payload(),dict(CONFIG),captured_utc=STAMP)
        rows=list(csv.DictReader(result["csv"].splitlines()))
        self.assertEqual(len(rows),8)
        self.assertEqual(result["receipt"]["quoted_contracts_accepted"],8)
        self.assertEqual({r["snapshot_id"] for r in rows},{rows[0]["snapshot_id"]})
        self.assertEqual({r["lot_size"] for r in rows},{"65"})
        self.assertTrue(all(float(r["bid"])<=float(r["ask"]) for r in rows))
        self.assertFalse(result["receipt"]["provider_authentication_verified"])
        self.assertFalse(result["receipt"]["trading_authority"])
        self.assertIn("USER_DECLARED",rows[0]["source"])
    def test_authentication_marker_cannot_be_forged_inside_saved_json(self):
        payload=mock_payload()
        payload["_fundtex_capture_origin"]="authenticated"
        doc=normalize(payload,CONFIG,captured_utc=STAMP)
        self.assertFalse(doc["receipt"]["provider_authentication_verified"])
    def test_invalid_crossed_and_missing_bid_are_rejected_or_omitted(self):
        payload=mock_payload()
        payload["data"]["oc"]["24600.000000"]["pe"]["top_ask_price"]=0
        r=normalize(payload,CONFIG,captured_utc=STAMP)
        self.assertEqual(r["receipt"]["quoted_contracts_accepted"],7)
        payload["data"]["oc"]["24600.000000"]["pe"]["top_ask_price"]=12
        payload["data"]["oc"]["24600.000000"]["pe"]["top_bid_price"]=13
        with self.assertRaisesRegex(ValueError,"Crossed"):normalize(payload,CONFIG,captured_utc=STAMP)
    def test_config_and_stale_dates_fail_closed(self):
        with self.assertRaises(ValueError):
            verify_config({**CONFIG,"underlying_scrip":"13"})
        with self.assertRaisesRegex(ValueError,"Expired"):
            normalize(mock_payload(),CONFIG,captured_utc=datetime(2026,11,1,tzinfo=timezone.utc))
        with self.assertRaisesRegex(ValueError,"timezone"):
            normalize(mock_payload(),CONFIG,captured_utc=datetime(2026,10,23))
    def test_no_credentials_means_no_network(self):
        with patch.dict(os.environ,{"FUNDTEX_DHAN_CLIENT_ID":"","FUNDTEX_DHAN_ACCESS_TOKEN":""}):
            with self.assertRaisesRegex(ValueError,"NOT_CONFIGURED"):
                read_only_fetch(CONFIG,transport=lambda r: (_ for _ in ()).throw(AssertionError("network")))
    def test_only_read_only_authorized_endpoint_and_no_leaked_token(self):
        with patch.dict(os.environ,{"FUNDTEX_DHAN_CLIENT_ID":"100000001","FUNDTEX_DHAN_ACCESS_TOKEN":"super-private-token"}):
            observed=[]
            def fake(req):
                observed.append({"method":req.get_method(),"url":req.full_url,
                                 "body":json.loads(req.data.decode())})
                return mock_payload()
            payload=read_only_fetch(CONFIG,transport=fake)
        self.assertEqual(payload["status"],"success")
        self.assertEqual(observed[0]["method"],"POST")
        self.assertEqual(observed[0]["url"],"https://api.dhan.co/v2/optionchain")
        self.assertEqual(observed[0]["body"]["UnderlyingScrip"],13)
        self.assertNotIn("super-private-token",json.dumps(observed))
    def test_same_snapshot_spread_liquidity_and_age(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            cap=capture_to_files(CONFIG,out_csv=folder/"chain.csv",
                    payload=mock_payload(),captured_utc=STAMP)
            self.assertTrue((folder/"chain.receipt.json").is_file())
            self.assertFalse(cap["provider_authentication_verified"])
            spread={"underlying":"NIFTY","spot":25000,"lot_size":65,
                   "valuation_date":"2026-10-23","expiry_date":"2026-10-29",
                   "structure":"bull_put_credit","min_width":150,"max_width":400,
                   "max_risk_inr":40000,"analysis_at_utc":(STAMP+timedelta(seconds=30)).isoformat(),
                   "max_snapshot_age_seconds":180,"max_quote_spread_bps":2000,
                   "min_top_quantity":65,"min_day_volume":1000,"min_open_interest":1000}
            result=propose(folder/"chain.csv",spread)
            self.assertTrue(result["eligible_candidates"])
            self.assertEqual(len(result["source_provenance"]),1)
            self.assertTrue(result["single_snapshot_id"])
            self.assertFalse(result["trading_authority"])
            self.assertEqual(result["captured_quote_timestamps_count"],8)
            with self.assertRaisesRegex(ValueError,"overwritten"):
                capture_to_files(CONFIG,out_csv=folder/"chain.csv",payload=mock_payload(),captured_utc=STAMP)
            spread["analysis_at_utc"]=(STAMP+timedelta(seconds=181)).isoformat()
            with self.assertRaisesRegex(ValueError,"too old"):propose(folder/"chain.csv",spread)
            del spread["analysis_at_utc"]
            with self.assertRaisesRegex(ValueError,"analysis_at_utc"):propose(folder/"chain.csv",spread)
    def test_illiquid_and_mixed_snapshot_fail_or_filter(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            chain=folder/"quotes.csv"
            capture_to_files(CONFIG,out_csv=chain,payload=mock_payload(),captured_utc=STAMP)
            cfg={"underlying":"NIFTY","spot":25000,"lot_size":65,
                 "valuation_date":"2026-10-23","expiry_date":"2026-10-29",
                 "structure":"bull_put_credit","min_width":100,"max_width":400,
                 "max_risk_inr":40000,"analysis_at_utc":STAMP.isoformat(),
                 "min_day_volume":200000}
            with self.assertRaisesRegex(ValueError,"Insufficient"):
                propose(chain,cfg)
            cfg["min_day_volume"]=0
            with chain.open(newline="") as f:
                rows=list(csv.DictReader(f))
                header=list(rows[0])
            rows[-1]["snapshot_id"]="different-snapshot"
            with chain.open("w",newline="") as f:
                writer=csv.DictWriter(f,fieldnames=header);writer.writeheader();writer.writerows(rows)
            with self.assertRaisesRegex(ValueError,"Mixed"):propose(chain,cfg)
    def test_saved_cli_requires_timestamp_and_can_convert_approved_file(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/"config.json").write_text(json.dumps(CONFIG))
            (p/"source.json").write_text(json.dumps(mock_payload()))
            root=Path(__file__).resolve().parents[1]
            cmd=[sys.executable,"-m","fundtex_india.cli","dhan-chain-capture",
                 "--inputs",str(p/"config.json"),"--saved-json",str(p/"source.json"),
                 "--out",str(p/"snapshot.csv")]
            bad=subprocess.run(cmd,cwd=root,text=True,capture_output=True,timeout=10)
            self.assertNotEqual(bad.returncode,0)
            self.assertFalse((p/"snapshot.csv").exists())
            ok=subprocess.run(cmd+["--captured-utc",STAMP.isoformat()],
                            cwd=root,text=True,capture_output=True,timeout=10)
            self.assertEqual(ok.returncode,0,ok.stderr)
            doc=json.loads(ok.stdout)
            self.assertTrue((p/"snapshot.csv").exists())
            self.assertFalse(doc["provider_authentication_verified"])

if __name__=="__main__":
    unittest.main()
