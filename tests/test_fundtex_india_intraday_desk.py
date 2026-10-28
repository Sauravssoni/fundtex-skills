"""FundTex India daytrade agent/source/causality gates (all synthetic)."""
from datetime import date,timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
import csv,json,subprocess,sys,unittest
from fundtex_india.intraday_desk import load_sessions,opening_range,paper_plan,replay,run_csv,_run_path

class IntradayDeskTests(unittest.TestCase):
 def setUp(self):
    self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup)
    self.csv=Path(self.temp.name)/"synthetic_nse_5m.csv"
    self.rows=[];d=date(2026,8,3)
    while len(set(x[0][:10] for x in self.rows))<31:
       if d.weekday()<5:
          # Bar timestamp means start of closed 5min bar; all 75 slots observed.
          for slot in range(75):
             minutes=9*60+15+slot*5
             hh,mm=divmod(minutes,60)
             op=100+(slot%6)*0.02
             cl=op+0.10
             hi=max(op,cl)+.30
             lo=min(op,cl)-.35
             if slot==3:op,hi,lo,cl=100.7,103.,100.6,102.
             if slot==4:op,hi,lo,cl=102.2,103.,101.9,102.7
             self.rows.append([f"{d.isoformat()}T{hh:02d}:{mm:02d}:00+05:30","DEMO.NS",op,hi,lo,cl,1000+slot])
       d+=timedelta(days=1)
    self._write()
 def _write(self):
    with self.csv.open("w",newline="") as fh:
       writer=csv.writer(fh);writer.writerow(("timestamp","symbol","open","high","low","close","volume"));writer.writerows(self.rows)
 def _load(self):return load_sessions(self.csv,"DEMO.NS")
 def test_exact_nse_grid_and_close_only_breakout(self):
    d=self._load();self.assertEqual(len(d["sessions"]),31)
    signal=opening_range(next(iter(d["sessions"].values())))
    self.assertEqual(signal["status"],"TRIGGERED")
    self.assertEqual(signal["first_completed_trigger_slot"],3)
    self.assertTrue(signal["entry_is_next_candle_open_not_trigger_close"])
    self.assertFalse(d["official_holiday_calendar_verified"])
 def test_no_unclosed_bar_entry_or_future_target_data(self):
    d=self._load();target=list(d["sessions"])[25]
    incomplete=paper_plan(d,session_date=target,as_of_slot=4)
    self.assertEqual(incomplete["state"],"NEXT_BAR_NOT_YET_CLOSED")
    plan=paper_plan(d,session_date=target,as_of_slot=5)
    self.assertEqual(plan["historical_entry_slot"],4)
    first=replay(d,plan,paths=150,seed=12)
    # Future bars on target day and all later sessions must not affect past-only replay.
    for session in list(d["sessions"])[25:]:
       for bar in d["sessions"][session][8:]:
          bar["open"]*=1.2;bar["high"]*=1.2;bar["low"]*=1.2;bar["close"]*=1.2
    second=replay(d,plan,paths=150,seed=12)
    self.assertEqual(first["mean_net_pnl_inr"],second["mean_net_pnl_inr"])
    self.assertEqual(first["source_sessions_used"],25)
    self.assertFalse(first["future_sessions_sampled"])
 def test_risk_gate_and_zero_broker_permission(self):
    d=self._load();day=list(d["sessions"])[25]
    blocked=paper_plan(d,session_date=day,quantity=1000,risk_budget=5)
    self.assertEqual(blocked["state"],"BLOCK_PAPER_RISK")
    with self.assertRaisesRegex(ValueError,"paper risk verdict"):
       replay(d,blocked,paths=100)
    allowed=paper_plan(d,session_date=day,quantity=1,risk_budget=1000)
    self.assertEqual(allowed["state"],"PAPER_ELIGIBLE")
    out=replay(d,allowed,paths=100,seed=19)
    self.assertEqual(out["real_orders"],0)
    self.assertFalse(out["broker_order_permissions_required"])
 def test_conservative_stop_and_real_gap_losses_can_exceed_stop(self):
    plan={"entry":100,"stop":95,"target":105,"quantity":1,
          "fees_per_side_rate_assumed":0,"slippage_per_side_rate_assumed":0}
    both=_run_path([{"open":100,"high":106,"low":94,"close":103}],plan,start_slot=0)
    self.assertEqual(both["exit_case"],"both_hit_stop_first")
    self.assertEqual(both["net_pnl_inr"],-5)
    gap=_run_path([{"open":92,"high":103,"low":91,"close":102}],plan,start_slot=0)
    self.assertEqual(gap["exit_case"],"gap_stop")
    self.assertEqual(gap["net_pnl_inr"],-8)
 def test_reject_invalid_feed_and_unknown_instruments(self):
    self.rows[12][3]=0.2;self._write()
    with self.assertRaisesRegex(ValueError,"Impossible OHLC"):
       self._load()
    self.rows[12][3]=100.5;self._write()
    with self.assertRaisesRegex(ValueError,"Mixed symbols"):
       load_sessions(self.csv,"OTHER.NS")
    self.rows.pop();self._write()
    with self.assertRaisesRegex(ValueError,"Incomplete"):
       self._load()
 def test_deterministic_and_bounded_replays(self):
    data=self._load();plan=paper_plan(data,session_date=list(data["sessions"])[23])
    a=replay(data,plan,paths=500,seed=42);b=replay(data,plan,paths=500,seed=42)
    self.assertEqual(a,b)
    for kwargs in ({"paths":99},{"paths":1_000_001},{"paths":True},{"window":9}):
       with self.assertRaises(ValueError):replay(data,plan,**kwargs)
    self.assertEqual(sum(a["exit_cases"].values()),500)
    self.assertEqual(a["model_quality"],"RESAMPLED_HISTORICAL_BARS_NOT_PROBABILISTIC_FORECAST")
 def test_cli_outputs_json_no_orders(self):
    import os
    root=Path(__file__).resolve().parents[1]
    d=self._load();day=list(d["sessions"])[25]
    cmd=[sys.executable,"-m","fundtex_india.cli","india-daytrade","--csv",str(self.csv),
         "--symbol","DEMO.NS","--session-date",day,"--paths","250"]
    p=subprocess.run(cmd,cwd=root,capture_output=True,text=True,timeout=30,env={**os.environ,"PYTHONPATH":str(root)})
    self.assertEqual(p.returncode,0,p.stderr)
    o=json.loads(p.stdout)
    self.assertEqual(o["replay"]["paths"],250)
    self.assertFalse(o["orders_enabled"])
    self.assertEqual(o["real_trades"],0)
    self.assertEqual(o["plan"]["plan"]["quantity"],1)

if __name__=="__main__":unittest.main()
