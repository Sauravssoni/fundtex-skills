"""Fundtex India analyst CLI. JSON output, explicit data-quality labels, no brokerage actions."""
from __future__ import annotations
import argparse
import datetime as dt
import json
import sys
from .market import csv_prices, yahoo_prices
from .stats import report
from .simulate import simulate
from .valuation import dcf
from .news import discover
from .portfolio import evaluate_portfolio
from .godeye import walkforward
from .importers import import_googlefinance, import_nse_udiff, export_prices
from .forecast import prequential
from .eval_suite import stress_suite
from .onboarding import suggest, doctor
from .council import plan as council_plan
from .diligence import from_json as company_diligence, render_markdown as diligence_markdown
from .mission import mission as plan_mission, as_markdown as mission_markdown

def make_parser():
    parser = argparse.ArgumentParser(prog="fundtex", description="Fundtex Financial Intelligence | India analyst toolkit")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("mission", help="Plan portable specialist-agent research, never execute or spawn agents")
    p.add_argument("--task", required=True, help="Short, non-sensitive research objective (never echoed)")
    p.add_argument("--agent", choices=("generic","claude","codex","gemini","cursor","copilot","opencode"),default="generic")
    p.add_argument("--mode", choices=("FAST","DEEP","INSTITUTIONAL"),default="FAST")
    p.add_argument("--abilities", default="terminal,python",help="Comma-separated host capabilities (terminal,python,web,subagents,filesystem)")
    p.add_argument("--max-workers",type=int,default=5)
    p.add_argument("--approved",action="store_true",help="User already authorized supported web and worker tasks")
    p.add_argument("--format",choices=("json","markdown"),default="markdown")
    p = sub.add_parser("diligence", help="Source-aware Indian company forensic financial packet from approved JSON")
    p.add_argument("--inputs", required=True, help="Financial statement figures from user-approved filing")
    p.add_argument("--format", choices=("json","markdown"),default="json")
    p = sub.add_parser("council", help="Offline bounded multi-agent task plan; does not spawn or execute workers")
    p.add_argument("--scope", default="India equities", help="Short, non-sensitive research domain; not echoed")
    p.add_argument("--mode", choices=("QUICK","DEEP","QUANT"),default="DEEP")
    p.add_argument("--max-workers",type=int,default=5)
    p.add_argument("--parallel",action="store_true",help="Recommend parallel workers where authorized, not spawn them")
    p = sub.add_parser("doctor", help="Offline install-health audit; never reads private records")
    p.add_argument("--repo-root",default=None,help="Fresh checkout path for version drift comparison; no personal data scanned")
    p = sub.add_parser("onboard", help="Suggest 3 first research prompts from explicit task context only")
    p.add_argument("--context", default="", help="An optional short user-authorized description; never crawls chat history")
    for name in ("analyze", "simulate", "brief"):
        p = sub.add_parser(name)
        src = p.add_mutually_exclusive_group(required=True)
        src.add_argument("--csv", help="Timestamped date/close CSV supplied by analyst")
        src.add_argument("--live", action="store_true", help="Best-effort unofficial Yahoo daily chart (NOT exchange-licensed live data)")
        p.add_argument("--symbol", required=True, help="e.g. INFY.NS or 500209.BO")
        p.add_argument("--risk-free", type=float, default=0.06, help="Annual risk-free rate as decimal")
        if name == "simulate":
            p.add_argument("--paths", type=int, default=10000)
            p.add_argument("--horizon", type=int, default=1)
            p.add_argument("--seed", type=int, default=42)
            p.add_argument("--position-inr", type=float, default=100000)
        if name == "brief":
            p.add_argument("--with-news", action="store_true", help="Fetch UNVERIFIED headline leads; verify source before relying")
    p = sub.add_parser("evaluate")
    p.add_argument("--scenarios", type=int, default=36, help="A multiple of six synthetic adverse regime scenarios")
    p.add_argument("--sessions", type=int, default=540)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--window", type=int, default=120)
    p = sub.add_parser("forecast")
    p.add_argument("--csv", required=True)
    p.add_argument("--symbol", required=True)
    p.add_argument("--window", type=int, default=252)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--margin", type=float, default=0.10)
    p = sub.add_parser("import")
    p.add_argument("--source-type", required=True, choices=("googlefinance","nse-udiff"))
    p.add_argument("--files", required=True, nargs="+", help="Local archived CSV or NSE UDiFF ZIP files")
    p.add_argument("--symbol", required=True)
    p.add_argument("--out", required=True, help="New output CSV (never overwritten)")
    p = sub.add_parser("godeye")
    p.add_argument("--csv",required=True)
    p.add_argument("--symbol",required=True)
    p.add_argument("--min-train",type=int,default=120)
    p.add_argument("--train-lookback",type=int,default=60)
    p.add_argument("--cost-bps",type=float,default=12)
    p = sub.add_parser("news")
    p.add_argument("--query", required=True)
    p.add_argument("--limit", type=int, default=10)
    p = sub.add_parser("portfolio")
    p.add_argument("--prices", required=True, help="Multisymbol sourced date,symbol,close CSV")
    p.add_argument("--holdings", required=True, help="symbol,weight,sector CSV; weights sum to 1")
    p = sub.add_parser("value")
    p.add_argument("--inputs", required=True, help="JSON of explicitly stated DCF assumptions")
    return parser

def execute(args):
    if args.command == "mission":
        return plan_mission(args.task,agent=args.agent,mode=args.mode,
                            abilities=[x.strip() for x in args.abilities.split(",") if x.strip()],
                            max_workers=args.max_workers,confirmed_permission=args.approved)
    if args.command == "diligence":
        return company_diligence(args.inputs)
    if args.command == "council":
        return council_plan(scope=args.scope,max_workers=args.max_workers,parallel=args.parallel,mode=args.mode)
    if args.command == "doctor":
        return doctor(repo_root=args.repo_root)
    if args.command == "onboard":
        return suggest(args.context)
    if args.command == "evaluate":
        return stress_suite(scenarios=args.scenarios,sessions=args.sessions,seed=args.seed,window=args.window)
    if args.command == "forecast":
        data=csv_prices(args.csv,args.symbol)
        out=prequential(data["rows"],window=args.window,seed=args.seed,probability_margin=args.margin)
        out["data_source"]=data["source"]
        out["input_sha256"]=data["sha256"]
        out["symbol"]=data["symbol"]
        out["data_quality"]=data["quality"]
        out["source_note"]=data["note"]
        out["research_only"]=True
        return out
    if args.command == "import":
        if args.source_type == "googlefinance":
            if len(args.files) != 1:
                raise ValueError("Google Finance importer accepts one CSV file")
            parsed=import_googlefinance(args.files[0],args.symbol)
        else:
            parsed=import_nse_udiff(args.files,args.symbol)
        return export_prices(parsed,args.out)
    if args.command == "news":
        return discover(args.query, args.limit)
    if args.command == "godeye":
        data=csv_prices(args.csv,args.symbol)
        out=walkforward(data["rows"],min_train=args.min_train,lookback=args.train_lookback,cost_bps=args.cost_bps)
        out["data_source"]=data["source"]
        out["input_sha256"]=data["sha256"]
        out["symbol"]=data["symbol"]
        return out
    if args.command == "portfolio":
        return evaluate_portfolio(args.prices, args.holdings)
    if args.command == "value":
        with open(args.inputs, encoding="utf-8") as handle:
            return dcf(json.load(handle))
    data = yahoo_prices(args.symbol) if args.live else csv_prices(args.csv, args.symbol)
    base = {"product": "Fundtex Financial Intelligence | Syntheon Technology",
            "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "symbol":data["symbol"], "market":"India",
            "data_quality":data["quality"], "data_source":data["source"],
            "data_last_observation":data["observed_as_of"], "data_note":data["note"],
            "source_sha256": data.get("sha256"),
            "research_only": True}
    if args.command in ("analyze","brief"):
        base["analysis"] = report(data["rows"], annual_risk_free=args.risk_free)
        if args.command == "brief" and args.with_news:
            base["headline_leads"] = discover(args.symbol.replace(".NS","").replace(".BO",""))
    elif args.command == "simulate":
        base["simulation"] = simulate(data["rows"], paths=args.paths, horizon=args.horizon,
                                      seed=args.seed, position_inr=args.position_inr)
    return base

def main(argv=None):
    args = make_parser().parse_args(argv)
    try:
        result = execute(args)
    except (ValueError, KeyError, OSError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status":"ERROR","message":str(exc),"no_fallback_quote":True}), file=sys.stderr)
        return 2
    if args.command == "diligence" and args.format == "markdown":
        print(diligence_markdown(result))
    elif args.command == "mission" and args.format == "markdown":
        print(mission_markdown(result))
    else:
        print(json.dumps(result, indent=2, allow_nan=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
