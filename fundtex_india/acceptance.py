"""FundTex offline integration acceptance: one reproducible research pipeline.

Every price, premium, lot size and option scenario here is SYNTHETIC.
This suite makes NO network, broker, wallet, OAuth or order calls.
An offline PASS must NEVER be confused with production/real-market validation.
"""
from __future__ import annotations
from datetime import date,timedelta
from hashlib import sha256
import csv
import json
from pathlib import Path
from .strategy_lab import run as strategy_run
from .options_lab import evaluate as option_evaluate
from .kronos_lab import evaluate as forecast_evaluate
from .kronos_paper import assess as paper_assess
from .film_studio import create as film_create
from .chart_studio import prices as chart_prices, chart_spec, svg

def _fixture(path):
    with path.open("x",encoding="utf-8",newline="") as f:
        w=csv.writer(f)
        w.writerow(("date","symbol","open","high","low","close","volume","source"))
        for i in range(370):
            # Deterministic volatility regimes, directional reversals and down legs.
            p=140+0.07*i+6*((i%31)/31)-9*((i//55)%2)+2.7*((i%7)/7)
            o=p-0.17; hi=max(o,p)+1.2;lo=min(o,p)-1.3
            w.writerow(((date(2025,1,1)+timedelta(days=i)).isoformat(),
                        "FUNDTEST.NS",round(o,5),round(hi,5),
                        round(lo,5),round(p,5),10000+i*19,"SYNTHETIC_FIXTURE"))
    return sha256(path.read_bytes()).hexdigest()

def run(output_dir, *,render_video=False,million_paths=False):
    out=Path(output_dir).expanduser()
    if out.exists() or out.is_symlink() or not out.parent.is_dir():
        raise ValueError("Acceptance requires a NEW path under an existing approved parent; never overwrite")
    out.mkdir(mode=0o700)
    records=[]
    def check(name, passed, details):
        records.append({"component":name,"status":"PASS" if passed else "FAIL",
                        "details":details})
        if not passed:raise ValueError(name+": cross-engine invariant failed")
    try:
        path=out/"SYNTHETIC-OHLC.csv"
        fingerprint=_fixture(path)
        history=chart_prices(path,"FUNDTEST.NS")
        check("dated_complete_ohlc",history["ohlc"] and
              history["source_sha256"]==fingerprint and
              history["data_quality"]=="SYNTHETIC_FIXTURE",
              {"rows":len(history["rows"]),"source_sha256":fingerprint})
        spec=chart_spec(history)
        chart=out/"chart.svg"
        chart.write_text(svg(spec),encoding="utf-8")
        check("chart_svg",chart.stat().st_size>1000 and "<svg" in chart.read_text(encoding="utf-8"),
              {"file":"chart.svg","bytes":chart.stat().st_size})
        strategy=strategy_run(path,"FUNDTEST.NS",{
           "candidates":[{"name":"sma_cross","fast":8,"slow":40},
                         {"name":"sma_cross","fast":15,"slow":60},
                         {"name":"rsi_reversion","entry":30,"exit":70}],
           "split_fraction":0.7,"cost_bps_per_position_change":15,
           "minimum_train_sessions":120,"bootstrap_repetitions":100,"bootstrap_seed":42})
        (out/"strategy.json").write_text(json.dumps(strategy,indent=2),encoding="utf-8")
        check("chronological_strategy",strategy["source_sha256"]==fingerprint and
               strategy["test_period_untouched_during_selection"] and
               strategy["research_only"] and not strategy["trading_authority"],
              {"selected":strategy["optimized_rule"],"heldout_status":strategy["status"],
               "holdout_period":strategy["holdout_first_fill_date"]})
        prediction=forecast_evaluate(path,"FUNDTEST.NS",backend="persistence",
                lookback=128,horizon=5,origins=12,stride=5)
        (out/"forecast-baselines.json").write_text(json.dumps(prediction,indent=2),encoding="utf-8")
        check("forecast_baseline_only",prediction["source_sha256"]==fingerprint and
              prediction["scores"]["challenger"]["mae"]==prediction["scores"]["persistence"]["mae"] and
              not prediction["industry_alpha_verified"] and
              prediction["release_gate"]=="NOT_VALIDATED_FOR_LIVE_FINANCIAL_SIGNALS",
              {"outcomes":prediction["scores"]["challenger"]["n"],"real_kronos_inference":False})
        paper=paper_assess(prediction,path,"FUNDTEST.NS",permutations=100,seed=42)
        (out/"paper-cost-placebo.json").write_text(json.dumps(paper,indent=2),encoding="utf-8")
        check("no_trade_paper_costs",paper["source_sha256"]==fingerprint and
              paper["broker_orders"]==0 and not paper["trade_execution"] and
              paper["pretrained_contamination_unknown"],
              {"windows":paper["windows"],"hypothetical_exposures":paper["model_long_windows"]})
        option={"underlying":"NIFTY","spot":25000,"lot_size":75,
                "valuation_date":"2026-10-23","expiry_date":"2026-10-29",
                "data_quality":"SYNTHETIC_FIXTURE","require_defined_risk":True,
                "max_risk_inr":12000,"annualized_volatility":0.2,
                "paths":1000000 if million_paths else 10000,"seed":42,
                "legs":[{"kind":"put","side":"sell","strike":25000,"premium":150,"lots":1},
                        {"kind":"put","side":"buy","strike":24800,"premium":90,"lots":1}]}
        options=option_evaluate(option)
        # Avoid storing 121 huge payoff and Monte Carlo path vectors in summary.
        (out/"options-defined-risk.json").write_text(json.dumps(options,indent=2),encoding="utf-8")
        check("defined_risk_scenario",options["data_quality"]=="SYNTHETIC_FIXTURE" and
              options["scenario_simulation"]["paths"]==option["paths"] and
              not options["trading_authority"] and
              not options["observed_options_chain"] and
              not options["geometry"]["loss_unbounded_in_model"],
              {"paths":option["paths"],"max_model_loss_inr":options["geometry"]["max_model_loss_inr"],
               "lot_size_user_supplied_not_verified":True})
        film=film_create(path,"FUNDTEST.NS",out/"film",seconds=6,fps=6,make_mp4=render_video)
        board=json.loads((out/"film/storyboard.json").read_text(encoding="utf-8"))
        check("chart_film",film["source_sha256"]==fingerprint and
              "SYNTHETIC" in film["source_quality"] and
              board["source_sha256"]==fingerprint and
              (not render_video or Path(film["video"]).stat().st_size>10000),
              {"frames":film["frames"],"actual_mp4":render_video,
               "video_file":"film/analysis.mp4" if render_video else None})
        result={"engine":"FUNDTEX_END_TO_END_OFFLINE_RESEARCH_ACCEPTANCE_V1",
          "status":"PASS_OFFLINE_SYNTHETIC_COMPONENTS_ONLY",
          "checked_components":len(records),"checks":records,
          "source_sha256":fingerprint,
          "real_market_data_verified":False,"broker_session_authenticated":False,
          "broker_gateway_production_ready":False,"real_kronos_model_executed":False,
          "derivatives_chain_verified":False,"licensed_exchange_feed_verified":False,
          "real_orders_executed":0,"research_only":True,
          "release_decision":"BLOCKED_UNTIL_LIVE_BROKER_AUTH_OAUTH_AND_LICENSE_GATES",
          "warnings":["Fixture contains invented OHLC and options inputs for contract testing ONLY",
                      "Passing this pipeline is not evidence of real trading accuracy, exchange licenses or profitable strategies",
                      "Historical Kronos models, OAuth token revocation and website browser UX have separate independent gates"]}
        (out/"acceptance-report.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
        return {"output_directory":str(out),"report":str(out/"acceptance-report.json"),**result}
    except Exception:
        # Preserve partial files for authorized local debugging; never claim PASS.
        (out/"FAILED_TEST_README.txt").write_text(
            "Offline synthetic acceptance failed before the final PASS report. Artifacts are incomplete. No live broker data used.\n",
            encoding="utf-8")
        raise
