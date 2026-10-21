"""Source-gated professional analyst pack, all outputs no-overwrite and labelled."""
from __future__ import annotations
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from .chart_studio import prices, chart_spec, annotations_from_file, svg, write_new
from .interactive_studio import document, screenshot, local_serve
from .graphics_studio import pie, bars, histogram, heatmap, waterfall
from .memo_studio import memo, pdf
from .workbook_studio import write_xlsx
from .portfolio import evaluate_portfolio

def build_pack(csv_path,symbol,out,*,annotations=None,holdings=None,portfolio_prices=None):
    folder=Path(out)
    if folder.exists():raise ValueError("Pack output already exists; choose new directory")
    data=prices(csv_path,symbol);spec=chart_spec(data,annotations_from_file(annotations))
    folder.mkdir(parents=True)
    created=[];omitted={}
    def save(name,contents):
        write_new(folder/name,contents)
        created.append(name)
    save("price-chart.svg",svg(spec))
    save("interactive-chart.html",document(spec))
    save("chart-spec.json",json.dumps(spec,indent=2))
    save("analyst-memo.md",memo(spec))
    close=[r["close"] for r in spec["rows"]]
    daily=[b/a-1 for a,b in zip(close,close[1:])]
    save("daily-return-histogram.svg",histogram(daily))
    for name,header,rows in (
        ("price-history.csv",["date","open","high","low","close","volume"],
         [[r["date"],r.get("open"),r.get("high"),r.get("low"),r["close"],r.get("volume")] for r in spec["rows"]]),
        ("historical-signals.csv",["date","reference_price","historical_observation","predictive"],
         [[s["date"],s["price"],s["signal"],"NO"] for s in spec["indicators"]["events"]]),
    ):
        p=folder/name
        with p.open("x",newline="",encoding="utf-8") as fh:
            wr=csv.writer(fh);wr.writerow(header);wr.writerows(rows)
        created.append(name)
    if holdings and portfolio_prices:
        result=evaluate_portfolio(portfolio_prices,holdings)
        save("sector-allocation.svg",pie(result["sectors"]))
        save("sector-exposure.svg",bars(result["weights"],title="Portfolio weights"))
        save("correlation-heatmap.svg",heatmap(result["daily_return_correlations"]))
        save("portfolio-risk.json",json.dumps(result,indent=2,allow_nan=False))
    elif holdings:
        with open(holdings,newline="",encoding="utf-8-sig") as fh:
            rd=csv.DictReader(fh);sectors={}
            for r in rd:
                val=float(r["weight"])
                if not math.isfinite(val) or val<0:raise ValueError("Invalid sector weight")
                sectors[r.get("sector") or "Unclassified"]=sectors.get(r.get("sector") or "Unclassified",0)+val
        if abs(sum(sectors.values())-1)>.0001:
            raise ValueError("Holdings weights must sum to one")
        save("sector-allocation.svg",pie(sectors))
        save("sector-exposure.svg",bars(sectors,title="Illustrative sector weights"))
    try:
        screenshot(folder/"interactive-chart.html",folder/"chart-screenshot.png")
        created.append("chart-screenshot.png")
    except Exception as exc:
        omitted["chart-screenshot.png"]=f"Optional browser unavailable: {type(exc).__name__}: {str(exc)[:110]}"
    try:
        write_xlsx(spec,folder/"analyst-workbook.xlsx")
        created.append("analyst-workbook.xlsx")
    except Exception as exc:
        omitted["analyst-workbook.xlsx"]=f"Optional spreadsheet engine unavailable: {type(exc).__name__}: {str(exc)[:110]}"
    try:
        pdf(spec,folder/"analyst-memo.pdf")
        created.append("analyst-memo.pdf")
    except Exception as exc:
        omitted["analyst-memo.pdf"]=f"Optional PDF engine unavailable: {type(exc).__name__}: {str(exc)[:110]}"
    manifest={
        "product":"Fundtex Analyst Studio v0.9",
        "symbol":spec["symbol"],"last_observation":spec["last_observation"],
        "data_quality":spec["data_quality"],"source_sha256":spec["source_sha256"],
        "generated_utc":datetime.now(timezone.utc).isoformat(),
        "created_files":created,"omitted_optional_outputs":omitted,
        "live_exchange_quotes":False,"trading_authority":False,
        "signal_status":"HISTORICAL OBSERVATION ONLY"
    }
    save("manifest.json",json.dumps(manifest,indent=2))
    return manifest
