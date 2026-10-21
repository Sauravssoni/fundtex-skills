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

def make_parser():
    parser = argparse.ArgumentParser(prog="fundtex", description="Fundtex Financial Intelligence | India analyst toolkit")
    sub = parser.add_subparsers(dest="command", required=True)
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
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
