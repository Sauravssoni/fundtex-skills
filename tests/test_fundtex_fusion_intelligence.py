"""Source integrity, India full-session ORB, fusion and no-order integration tests."""
import csv
from datetime import datetime,timedelta,timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zoneinfo import ZoneInfo
from fundtex_india.fusion_intelligence import from_file,fuse
from fundtex_india.intraday_replay import replay

ROOT=Path(__file__).resolve().parents[1]
IST=ZoneInfo("Asia/Kolkata")
class FusionTest(unittest.TestCase):
 def setUp(self):
    self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
    self.path=Path(self.tmp.name)
    self.events=self.path/"events.json"
    self.asof="2026-10-27T16:00:00+05:30"
    self.items=[{
       "source":"WORLD_MONITOR_AUTHORIZED_MCP","headline":"Shipping lane advisory dated by provider",
       "category":"shipping","published_at":"2026-10-27T05:00:00Z",
       "observed_at":"2026-10-27T06:00:00Z",
       "source_url":"https://worldmonitor.app","event_id":"wm-1","symbols":[],
       "regions":["India","Middle East"]},
       {"source":"NSE_PRIMARY","headline":"Verified illustrative exchange filing",
        "category":"company","published_at":"2026-10-26T06:00:00Z",
        "observed_at":"2026-10-26T06:01:00Z",
        "symbols":["INFY.NS"],"event_id":"filing-1"}]
    self.events.write_text(json.dumps(self.items+[self.items[0]]))
    self.intraday=self.path/"bars.csv"
    with self.intraday.open("w",newline="") as fh:
      w=csv.writer(fh);w.writerow(("timestamp","symbol","open","high","low","close","volume"))
      for date_s in ("2026-10-20","2026-10-21","2026-10-22"):
       base=datetime.fromisoformat(date_s+"T09:15:00").replace(tzinfo=IST)
       for i in range(75):
        price=100+i*.1 if i>=3 else 100
        if i==3:price=101.2
        w.writerow(((base+timedelta(minutes=5*i)).isoformat(),"INFY.NS",
                    price,price+0.4,price-0.4,price+0.1,3000+i))
 def test_events_deduplicated_with_provenance_and_no_fake_market_feed(self):
    o=from_file(self.events,as_of=self.asof)
    self.assertEqual(o["event_count"],2)
    self.assertEqual(o["deduplicated"],1)
    self.assertEqual(o["primary_events"],1)
    self.assertFalse(o["exchange_live_price_verified"])
    self.assertFalse(o["broker_access_performed"])
    self.assertTrue(all(not e["trade_signal"] for e in o["events"]))
    self.assertTrue(all(not e["causality_verified"] for e in o["events"]))
    r=fuse(evidence=o,symbol="INFY.NS")
    self.assertEqual(r["exact_symbol_mentions"],1)
    self.assertEqual(r["decision"],"ABSTAIN_UNVERIFIED_EDGE")
    self.assertEqual(r["provider_count"],2)
 def test_fail_closed_on_time_travel_secrets_unapproved_providers(self):
    for update,needle in [
      ({"source":"UNKNOWN_UNPAID_TOOL"},"allowlisted"),
      ({"published_at":"2026-11-01T00:00:00Z"},"Future"),
      ({"observed_at":"2026-10-26T00:00:00Z"},"time-inconsistent"),
      ({"source_url":"http://example.com/private?token=password"},"HTTPS"),
      ({"unexpected_account_id":"secret"},"Unsupported")]:
      data=[{**self.items[0],**update}]
      self.events.write_text(json.dumps(data))
      with self.assertRaisesRegex(ValueError,needle):from_file(self.events,as_of=self.asof)
 def test_full_session_and_paper_bootstrap_no_order(self):
    out=replay(self.intraday,"INFY.NS",bootstrap_paths=1000,seed=7)
    self.assertEqual(out["engine"],"FUNDTEX_INTRADAY_REPLAY_V1")
    self.assertEqual(out["evaluation"]["sample_sessions"],3)
    self.assertFalse(out["trading_enabled"])
    self.assertFalse(out["bootstrap"]["future_win_probability_calibrated"])
    self.assertEqual(out["bootstrap"]["paths"],1000)
    self.assertEqual(out,replay(self.intraday,"INFY.NS",bootstrap_paths=1000,seed=7))
    self.assertTrue(all("paper_net_pnl_inr" in t for t in out["trades"]))
 def test_missing_bar_excluded_and_no_optimistic_backfill(self):
    rows=list(csv.DictReader(self.intraday.open(newline="")))
    with self.intraday.open("w",newline="") as f:
      w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader()
      w.writerows([row for i,row in enumerate(rows) if i!=30])
    out=replay(self.intraday,"INFY.NS",bootstrap_paths=1000)
    self.assertEqual(out["sample_quality"]["incomplete_or_offgrid_excluded"],1)
    self.assertEqual(out["evaluation"]["sample_sessions"],2)
 def test_foreign_symbol_and_excess_risk_rejected(self):
    with self.assertRaisesRegex(ValueError,"mixes instruments"):
      replay(self.intraday,"TCS.NS",bootstrap_paths=1000)
    with self.assertRaisesRegex(ValueError,"5%"):
      replay(self.intraday,"INFY.NS",capital_inr=10000,max_loss_inr=2000,bootstrap_paths=1000)
 def test_fusion_cli_integrates_both_without_external_calls(self):
    self.events.write_text(json.dumps(self.items))
    cmd=[sys.executable,"-m","fundtex_india.cli","fusion-desk","--events",str(self.events),
       "--as-of",self.asof,"--symbol","INFY.NS","--intraday",str(self.intraday),"--paths","1000"]
    r=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=30)
    self.assertEqual(r.returncode,0,r.stderr[-800:])
    result=json.loads(r.stdout)
    self.assertEqual(result["engine"],"FUNDTEX_GOD_EYE_FUSION_V1")
    self.assertEqual(result["replay"]["evaluation"]["sample_sessions"],3)
    self.assertFalse(result["broker_order_authority"])
    self.assertFalse(result["replay"]["trading_enabled"])
    self.assertNotIn("token",r.stdout.casefold())
 def test_never_reuse_historical_fusion_as_live_connection(self):
    e=from_file(self.events,as_of=self.asof)
    with self.assertRaisesRegex(ValueError,"FundTex"):
        fuse(evidence=e,tradereplay={"broker_order_authority":True})
    with self.assertRaisesRegex(ValueError,"verified structure"):
        fuse(evidence={"fake":True})
if __name__=="__main__":unittest.main()
