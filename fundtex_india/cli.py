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
from .regulatory import catalog as source_catalog, fetch as regulatory_fetch, from_file as regulatory_file
from .amfi import from_file as amfi_file
from .pilot import from_file as pilot_file
from .chart_studio import prices as studio_prices, chart_spec as studio_spec, annotations_from_file, svg as studio_svg, write_new
from .interactive_studio import document as studio_html, screenshot as studio_screenshot, local_serve
from .pack_studio import build_pack
from .workbook_studio import write_xlsx
from .memo_studio import memo as studio_memo, pdf as studio_pdf
from .graphics_studio import pie as graphic_pie, bars as graphic_bars, heatmap as graphic_heatmap, histogram as graphic_histogram, waterfall as graphic_waterfall
from .broker_quotes import availability as broker_availability, quote as authenticated_quote
from .research_auto import run as automatic_research
from .broker_onboarding import guide as broker_connection_guide
from .institutional import investment_committee, lunar_placebo
from .activity import emit as agent_activity_emit, view as agent_activity_view
from .reconcile import reconcile as reconcile_prices
from .options_lab import evaluate as options_payoff
from .options_builder import propose as propose_option_spreads
from .dhan_option_chain import (read_only_fetch as dhan_read_only_option_chain,
    capture_to_files as capture_dhan_option_chain)
from .strategy_lab import run as backtest_strategy
from .integrations import catalog as integration_catalog
from .launchpad import create as create_launchpad
from .regime_bench import simulate_regimes as adversarial_regime_bench

def make_parser():
    parser = argparse.ArgumentParser(prog="fundtex", description="Fundtex Financial Intelligence | India analyst toolkit")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("research",help="One command: fetch approved India historical prices, optional authenticated broker LTP, charts + ZIP report")
    p.add_argument("--symbol",required=True)
    p.add_argument("--source",choices=("public","public-ohlc","fyers","csv"),default="public",help="public: unofficial adjusted close; public-ohlc: unofficial raw unadjusted candles; fyers: authorized OHLCV; csv: approved local")
    p.add_argument("--csv",default=None,help="Explicitly approved price CSV if --source csv")
    p.add_argument("--period",choices=("1mo","3mo","6mo","1y","2y","5y"),default="1y")
    p.add_argument("--quote",choices=("auto","off","fyers","kite","dhan"),default="auto",help="Read-only optional authenticated broker snapshot, NEVER an order")
    p.add_argument("--max-age-days",type=int,default=7)
    p.add_argument("--out",required=True,help="NEW output directory and ZIP, never overwritten")
    p = sub.add_parser("connect",help="Step-by-step official broker authorization guide; never accepts tokens in chat")
    p.add_argument("--provider",choices=("choose","zerodha-mcp","fyers","kite","dhan"),default="choose")
    p.add_argument("--open",action="store_true",help="Open selected official broker page after user approval")
    p.add_argument("--verify",default=None,metavar="SYMBOL",help="Read-only authenticated quote verification, if configured")
    p = sub.add_parser("broker-status",help="Configured Indian broker quote sources; never prints tokens")
    p = sub.add_parser("quote",help="Current authenticated broker quote snapshot, never trading")
    p.add_argument("--symbol",required=True);p.add_argument("--provider",choices=("fyers","kite","dhan"),required=True)
    p = sub.add_parser("chart", help="Audited SVG or standalone interactive HTML price chart")
    p.add_argument("--csv",required=True);p.add_argument("--symbol",required=True)
    p.add_argument("--out",required=True);p.add_argument("--format",choices=("html","svg"),default="html")
    p.add_argument("--annotations",default=None)
    p = sub.add_parser("chart-screenshot",help="PNG screenshot of local chart via installed Playwright Chromium")
    p.add_argument("--html",required=True);p.add_argument("--out",required=True)
    p = sub.add_parser("chart-serve",help="127.0.0.1 viewer refreshing ONE approved local CSV (not live exchange)")
    p.add_argument("--csv",required=True);p.add_argument("--symbol",required=True);p.add_argument("--port",type=int,default=8734)
    for name in ("workbook","report"):
        p=sub.add_parser(name);p.add_argument("--csv",required=True);p.add_argument("--symbol",required=True);p.add_argument("--out",required=True)
    p=sub.add_parser("analyst-pack",help="Charts, exports, research memo, optional PNG/XLSX/PDF")
    p.add_argument("--csv",required=True);p.add_argument("--symbol",required=True);p.add_argument("--out",required=True)
    p.add_argument("--annotations",default=None);p.add_argument("--holdings",default=None);p.add_argument("--portfolio-prices",default=None)
    p=sub.add_parser("visual",help="Illustrative pie/bar/heatmap/histogram/waterfall from approved JSON")
    p.add_argument("--inputs",required=True);p.add_argument("--kind",required=True,choices=("pie","bar","heatmap","histogram","waterfall"));p.add_argument("--out",required=True)
    p = sub.add_parser("activity-log", help="Append one true, sanitized agent lifecycle event (host instrumentation required)")
    p.add_argument("--events", required=True, help="Approved local JSONL trace file")
    p.add_argument("--agent", required=True, help="True agent name declared by the hosting runtime")
    p.add_argument("--event", required=True, help="Short action ID")
    p.add_argument("--status", required=True, choices=("start","progress","done","error","blocked"))
    p.add_argument("--detail", default="")
    p = sub.add_parser("activity-view", help="Optional 127.0.0.1-only agent activity dashboard")
    p.add_argument("--events", required=True)
    p.add_argument("--port", type=int, default=8736)
    p.add_argument("--open", action="store_true", help="Open local browser only when approved")
    p = sub.add_parser("reconcile", help="Compare two independently sourced dated closing-price CSVs before analyst use")
    p.add_argument("--primary", required=True)
    p.add_argument("--secondary", required=True)
    p.add_argument("--symbol", required=True)
    p.add_argument("--tolerance-bps", type=float, default=25.0)
    p.add_argument("--min-overlap", type=int, default=12)
    p = sub.add_parser("investment-committee", help="Human-review investment committee math from documented, user-approved JSON")
    p.add_argument("--inputs", required=True, help="JSON with issuer, filing references, financials and scenarios")
    p = sub.add_parser("lunar-study", help="Exploratory phase hypothesis falsification, NOT a trading predictor")
    p.add_argument("--csv", required=True)
    p.add_argument("--symbol", required=True)
    p.add_argument("--permutations", type=int, default=1000)
    p.add_argument("--seed", type=int, default=42)
    p = sub.add_parser("launchpad", help="Optional offline welcome page in browser, only on explicit request")
    p.add_argument("--out", required=True, help="A NEW local HTML file in an existing approved directory")
    p.add_argument("--open", action="store_true", help="Open the page in a browser (explicitly opt in)")
    p = sub.add_parser("regime-bench", help="Adversarial synthetic market regimes, train-only strategy search, independent holdout")
    p.add_argument("--scenarios-per-regime", type=int, default=20)
    p.add_argument("--sessions", type=int, default=540)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--cost-bps", type=float, default=15)
    sub.add_parser("integrations", help="Real capabilities, available MCP/provider routes, no fake connections")
    p = sub.add_parser("dhan-chain-capture", help="Authorized read-only Dhan option snapshot or saved response -> audited local CSV, no orders")
    p.add_argument("--inputs", required=True, help="User-approved JSON: exact Dhan underlying scrip/segment, expiry and verified lot size")
    p.add_argument("--out", required=True, help="NEW local output CSV and metadata receipt (never overwrite)")
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--live", action="store_true", help="EXPLICIT authorized Dhan data-only POST; credentials stay in local env")
    mode.add_argument("--saved-json", help="Approved captured Dhan response, never automatically certified authenticated")
    p.add_argument("--captured-utc", help="MANDATORY for saved JSON: user-attested original snapshot capture time, UTC ISO timestamp")
    p = sub.add_parser("options-build", help="Generate conservative defined-risk vertical candidates from APPROVED option bid/ask CSV")
    p.add_argument("--chain", required=True)
    p.add_argument("--inputs", required=True, help="Validated underlying, dates, width, lot-size and risk budget JSON")
    p = sub.add_parser("options-sim", help="Defined-risk hedged options expiry payoff and optional scenario simulation (no orders)")
    p.add_argument("--inputs", required=True, help="Approved local JSON, explicit 2026 fees, strikes and exact lot size")
    p = sub.add_parser("strategy-build", help="No-code training-only strategy selection and next-open historical test")
    p.add_argument("--csv", required=True, help="Real approved OHLC price file; no close-to-open fabrication")
    p.add_argument("--symbol", required=True, help="Exchange ticker, checked against approved price CSV")
    p.add_argument("--inputs", required=True, help="JSON array of bounded rule candidates and experiment settings")
    sub.add_parser("sources", help="Approved official Indian data/source registry and licence gates")
    p = sub.add_parser("regulatory", help="Official RBI/SEBI RSS metadata discovery, no full-document verification")
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument("--feed", choices=("sebi","rbi-releases","rbi-notifications"),help="Explicit opt-in official HTTPS RSS request")
    source.add_argument("--file",help="Previously approved local RSS/Atom XML")
    p.add_argument("--max-items",type=int,default=15)
    p = sub.add_parser("amfi", help="Read user-approved AMFI-format NAV file (not a live stock price)")
    p.add_argument("--file",required=True)
    p.add_argument("--query",default="",help="Scheme name / AMC / code filter")
    p.add_argument("--as-of",default=None,help="YYYY-MM-DD snapshot evaluation date")
    p.add_argument("--max-results",type=int,default=15)
    p = sub.add_parser("pilot", help="Human-scored baseline vs Fundtex workflow speed/quality pilot")
    p.add_argument("--inputs",required=True,help="Approved de-identified JSON of measured tasks")
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
    if args.command == "research":
        return automatic_research(args.symbol,args.out,source=args.source,csv_file=args.csv,
                                  period=args.period,quote_provider=args.quote,max_age_days=args.max_age_days)
    if args.command == "quote":
        return authenticated_quote(args.symbol,args.provider)
    if args.command == "connect":
        return broker_connection_guide(args.provider,open_official=args.open,verify_symbol=args.verify)
    if args.command == "broker-status":
        return broker_availability()
    if args.command == "chart":
        spec=studio_spec(studio_prices(args.csv,args.symbol),annotations_from_file(args.annotations))
        dest=write_new(args.out,studio_svg(spec) if args.format=="svg" else studio_html(spec))
        return {"file":dest,"chart_type":spec["price_type"],"quality":spec["data_quality"],"exchange_live":False}
    if args.command == "chart-screenshot":
        return {"file":studio_screenshot(args.html,args.out),"source_kind":"LOCAL_HTML"}
    if args.command == "chart-serve":
        local_serve(args.csv,args.symbol,port=args.port)
        return {"status":"Viewer stopped"}
    if args.command == "analyst-pack":
        return build_pack(args.csv,args.symbol,args.out,annotations=args.annotations,holdings=args.holdings,portfolio_prices=args.portfolio_prices)
    if args.command in ("workbook","report"):
        spec=studio_spec(studio_prices(args.csv,args.symbol))
        if args.command=="workbook":return {"file":write_xlsx(spec,args.out)}
        return {"file":studio_pdf(spec,args.out) if args.out.lower().endswith(".pdf") else write_new(args.out,studio_memo(spec))}
    if args.command == "visual":
        values=json.loads(open(args.inputs,encoding="utf-8").read())
        engine={"pie":graphic_pie,"bar":graphic_bars,"heatmap":graphic_heatmap,"histogram":graphic_histogram,"waterfall":graphic_waterfall}[args.kind]
        return {"file":write_new(args.out,engine(values)),"kind":args.kind}
    if args.command == "activity-log":
        return agent_activity_emit(args.events, agent=args.agent, event=args.event,
                                   status=args.status, detail=args.detail)
    if args.command == "activity-view":
        return agent_activity_view(args.events, port=args.port, open_browser=args.open)
    if args.command == "reconcile":
        return reconcile_prices(args.primary,args.secondary,args.symbol,
                                tolerance_bps=args.tolerance_bps,min_overlap=args.min_overlap)
    if args.command == "investment-committee":
        with open(args.inputs, encoding="utf-8") as handle:
            return investment_committee(json.load(handle))
    if args.command == "lunar-study":
        data = csv_prices(args.csv, args.symbol)
        rows = data["rows"]
        returns = [{"date": b["date"], "return": float(b["close"]) / float(a["close"]) - 1.0}
                   for a, b in zip(rows, rows[1:])]
        result = lunar_placebo(returns, seed=args.seed, permutations=args.permutations)
        result.update({"symbol": data["symbol"], "data_source": data["source"],
                       "source_sha256": data.get("sha256"), "data_quality": data["quality"],
                       "research_only": True})
        return result
    if args.command == "launchpad":
        health = doctor()
        return create_launchpad(args.out,open_browser=args.open,
                                installed_skills=health.get("autonomous_first_run_ready",False),
                                source_status="NOT_AUTHENTICATED; broker login not checked")
    if args.command == "regime-bench":
        return adversarial_regime_bench(scenarios_per_regime=args.scenarios_per_regime,
                                      sessions=args.sessions, seed=args.seed, cost_bps=args.cost_bps)
    if args.command == "integrations":
        return integration_catalog()
    if args.command == "dhan-chain-capture":
        from datetime import datetime, timezone
        from pathlib import Path
        import json
        with open(args.inputs, encoding="utf-8") as handle:
            config=json.load(handle)
        if args.live:
            if args.captured_utc:raise ValueError("Live capture records actual local fetch time, do not override")
            payload=dhan_read_only_option_chain(config)
            when=datetime.now(timezone.utc)
            authenticated=True
        else:
            if not args.captured_utc:
                raise ValueError("Saved JSON requires an explicitly attested original UTC capture timestamp; cannot infer freshness")
            when=datetime.fromisoformat(args.captured_utc.replace("Z","+00:00"))
            src=Path(args.saved_json)
            if not src.is_file() or src.stat().st_size>2_000_000:
                raise ValueError("Saved broker JSON absent or exceeds 2MB")
            with src.open(encoding="utf-8") as handle:payload=json.load(handle)
            authenticated=False
        return capture_dhan_option_chain(config,out_csv=args.out,payload=payload,
                                         captured_utc=when,authenticated_fetch=authenticated)
    if args.command == "options-build":
        with open(args.inputs, encoding="utf-8") as handle:
            return propose_option_spreads(args.chain,json.load(handle))
    if args.command == "options-sim":
        with open(args.inputs, encoding="utf-8") as handle:
            return options_payoff(json.load(handle))
    if args.command == "strategy-build":
        with open(args.inputs, encoding="utf-8") as handle:
            return backtest_strategy(args.csv,args.symbol,json.load(handle))
    if args.command == "sources":
        return source_catalog()
    if args.command == "regulatory":
        return regulatory_fetch(args.feed,max_items=args.max_items) if args.feed else regulatory_file(args.file,max_items=args.max_items)
    if args.command == "amfi":
        return amfi_file(args.file,query=args.query,max_results=args.max_results,as_of=args.as_of)
    if args.command == "pilot":
        return pilot_file(args.inputs)
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
    except (ValueError, KeyError, OSError, TypeError, UnicodeError, json.JSONDecodeError) as exc:
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
