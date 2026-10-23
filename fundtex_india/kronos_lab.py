"""FundTex Kronos challenger lab: strict financial history and honest out-of-sample scoring.

Official upstream: shiyu-coder/Kronos, pinned 67b630e67f6a18c9e9be918d9b4337c960db1e9a.
This module makes ZERO trades or network calls. Actual Kronos forecasts require
a separate explicitly approved, pinned local source and local safetensors.
Model pretraining contamination cannot be excluded without training cutoffs.
"""
from __future__ import annotations
from datetime import date,datetime,timezone
from hashlib import sha256
import csv
import json
import math
from pathlib import Path
import statistics
from .market import validate_symbol

UPSTREAM="https://github.com/shiyu-coder/Kronos"
PINNED_SHA="67b630e67f6a18c9e9be918d9b4337c960db1e9a"
SUPPORTED={"mini":("NeoQuasar/Kronos-mini","NeoQuasar/Kronos-Tokenizer-2k",2048),
           "small":("NeoQuasar/Kronos-small","NeoQuasar/Kronos-Tokenizer-base",512),
           "base":("NeoQuasar/Kronos-base","NeoQuasar/Kronos-Tokenizer-base",512)}
FIELDS=("date","open","high","low","close","volume")
def bars_from_csv(path,symbol):
    sym=validate_symbol(symbol)
    f=Path(path).expanduser()
    if not f.is_file() or f.is_symlink() or f.stat().st_size>5_000_000:
        raise ValueError("Approved OHLC CSV must be a normal file <=5 MB")
    with f.open(encoding="utf-8-sig",newline="") as stream:
        r=csv.DictReader(stream)
        if not r.fieldnames or not set(FIELDS[:5]).issubset(set(r.fieldnames)):
            raise ValueError("Kronos requires ACTUAL dated OHLC (not close-only or reconstructed prices)")
        if "symbol" not in r.fieldnames:
            raise ValueError("Explicit symbol identity required; no filename-derived ticker")
        out=[];prev=None
        for record in r:
            if record.get("symbol","").upper().strip()!=sym:continue
            timestamp=record["date"]
            if not isinstance(timestamp,str) or len(timestamp)!=10:
                raise ValueError("Daily observed exchange date YYYY-MM-DD required")
            when=date.fromisoformat(timestamp)
            if prev is not None and when<=prev:raise ValueError("Date order/duplicates unsafe")
            prev=when
            values=[]
            for field in ("open","high","low","close"):
                raw=record.get(field)
                try:v=float(raw)
                except (ValueError,TypeError):raise ValueError("Malformed real OHLC: "+field) from None
                if not math.isfinite(v) or v<=0:raise ValueError("Invalid OHLC: "+field)
                values.append(v)
            o,h,l,c=values
            if not l<=min(o,c)<=max(o,c)<=h:
                raise ValueError("Impossible observed OHLC candle")
            raw_volume=record.get("volume")
            vol=None if raw_volume in (None,"") else float(raw_volume)
            if vol is not None and (not math.isfinite(vol) or vol<0):
                raise ValueError("Invalid volume")
            out.append({"date":timestamp,"open":o,"high":h,"low":l,"close":c,"volume":vol})
            if len(out)>3000:raise ValueError("Maximum 3000 approved daily bars")
    if len(out)<120:raise ValueError("At least 120 actual daily OHLC bars required")
    if out[-1]["date"]>datetime.now(timezone.utc).date().isoformat():
        raise ValueError("Future date not observed")
    # Detect source flags from the entire CSV without falsely asserting identity/auth.
    source_quality="USER_SUPPLIED_UNVERIFIED"
    with f.open(encoding="utf-8-sig",newline="") as stream:
        scan=csv.DictReader(stream)
        source_tags=set()
        for r in scan:
            if r.get("symbol","").upper().strip()==sym:
                tag=(r.get("source") or "").strip()
                if tag:source_tags.add(tag[:100])
    if source_tags=={"SYNTHETIC_FIXTURE"}:source_quality="SYNTHETIC_FIXTURE"
    elif source_tags=={"APPROVED_KITE_MCP_HISTORY"}:
        source_quality="USER_APPROVED_KITE_MCP_HISTORY_NOT_EXCHANGE_SIGNED"
    return {"symbol":sym,"rows":out,"source_sha256":sha256(f.read_bytes()).hexdigest(),
            "source_quality":source_quality,"start":out[0]["date"],"end":out[-1]["date"],
            "adjustments_verified":False,"training_data_overlap_unknown":True}
def _predict_baseline(history,destination,model):
    closes=[r["close"] for r in history]
    last=closes[-1]
    if model=="persistence":return [last]*len(destination)
    if model=="drift":
        # Lagged 10 observed trading-session returns; clip leverage-prone regime extrapolation.
        lag=min(10,len(closes)-1)
        growth=(last/closes[-lag-1])**(1/lag)-1
        growth=min(.03,max(-.03,growth))
        return [last*(1+growth)**(k+1) for k in range(len(destination))]
    raise ValueError("Unknown baseline")
def _forecast(backend,history,dest):
    if isinstance(backend,str):
        return _predict_baseline(history,dest,backend)
    if not callable(backend):
        raise ValueError("Backend must be a vetted forecasting callable or named baseline")
    # Copy past-only inputs to protect the evaluator from model mutations and leakage.
    past=tuple(dict(r) for r in history)
    future_dates=tuple(r["date"] for r in dest)
    answer=backend(past,future_dates)
    if not isinstance(answer,(tuple,list)) or len(answer)!=len(dest):
        raise ValueError("Model returned invalid horizon")
    try:values=[float(x) for x in answer]
    except (ValueError,TypeError):raise ValueError("Model returned invalid numeric predictions") from None
    if any(not math.isfinite(x) or x<=0 for x in values):
        raise ValueError("Model returned nonfinite/nonpositive close")
    return values
def _metrics(predicted,actual,last_closes):
    errors=[a-p for a,p in zip(actual,predicted)]
    mae=statistics.mean(abs(x) for x in errors)
    rmse=math.sqrt(statistics.mean(x*x for x in errors))
    directions=[int(p>b)==int(a>b) for p,a,b in zip(predicted,actual,last_closes)]
    return {"mae":mae,"rmse":rmse,"directional_accuracy":statistics.mean(directions),
            "n":len(actual)}
def evaluate(csv_path,symbol,*,backend="persistence",lookback=128,horizon=5,origins=12,stride=5,seed=42):
    if any(isinstance(x,bool) or not isinstance(x,int) for x in (lookback,horizon,origins,stride,seed)):
        raise ValueError("Integer research parameters required")
    if not 64<=lookback<=512 or not 1<=horizon<=20 or not 3<=origins<=60 or not 1<=stride<=40:
        raise ValueError("Research limits: lookback 64..512, horizon 1..20, origins 3..60, stride 1..40")
    record=bars_from_csv(csv_path,symbol);rows=record["rows"];length=len(rows)
    # Chronological non-overlapping evaluation windows and explicit embargo:
    # stride must be >= horizon; otherwise a later forecast would be trained on
    # outcomes of an earlier evaluation window. Disallow overlapping test labels.
    if stride<horizon:raise ValueError("Overlapping evaluation labels prohibited: stride must >= horizon")
    required=lookback+horizon+(origins-1)*stride
    if length<required:raise ValueError(f"Need at least {required} actual bars for these independent cutoffs")
    # Use only the latest origins, never choose cutoffs with hindsight.
    first=length-horizon-(origins-1)*stride
    cutoffs=[first+i*stride for i in range(origins)]
    if cutoffs[0]<lookback:raise ValueError("Insufficient past-only lookback")
    out=[];total={name:{"pred":[],"actual":[],"anchor":[]} for name in ("challenger","persistence","drift")}
    for cutoff in cutoffs:
        history=rows[cutoff-lookback:cutoff]
        observed=rows[cutoff:cutoff+horizon]
        actual=[r["close"] for r in observed]
        names={"challenger":backend,"persistence":"persistence","drift":"drift"}
        report={"forecast_at_close":history[-1]["date"],"first_outcome":observed[0]["date"],
                "last_outcome":observed[-1]["date"],"past_bars_used":len(history),
                "models":{}}
        for name,model in names.items():
            predictions=_forecast(model,history,observed)
            anchors=[history[-1]["close"]]*len(observed)
            # Compare each future predicted close to the last KNOWN origin close.\n            # Never use future actual prices as direction anchors for a decision at origin.
            total[name]["pred"].extend(predictions)
            total[name]["actual"].extend(actual)
            total[name]["anchor"].extend(anchors)
            report["models"][name]={"predicted_close":predictions,
                                    "observed_close":actual}
        out.append(report)
    scores={name:_metrics(s["pred"],s["actual"],s["anchor"]) for name,s in total.items()}
    best=min(scores[k]["mae"] for k in ("persistence","drift"))
    delta=(best-scores["challenger"]["mae"])/best if best else None
    # Never declare actual predictive alpha simply from lower backtest MAE.
    return {"engine":"FUNDTEX_KRONOS_CHALLENGER_WALKFORWARD_V1",
      "symbol":record["symbol"],"source_sha256":record["source_sha256"],
      "source_quality":record["source_quality"],"as_of":record["end"],
      "upstream_model_repository":UPSTREAM,"upstream_pinned_commit":PINNED_SHA,
      "evaluation_type":"historical prefix-only expanding cutoffs with separate non-overlapping test horizons",
      "pretrained_model_contamination_unknown":True,
      "industry_alpha_verified":False,"execution_prices_verified":False,
      "trade_recommendation":"NONE","broker_order_authority":False,
      "parameters":{"lookback":lookback,"horizon":horizon,"origins":origins,"stride":stride,"seed":seed},
      "backend_label":backend if isinstance(backend,str) else "USER_AUTHORIZED_KRONOS_ADAPTER",
      "scores":scores,"relative_mae_improvement_vs_best_baseline":delta,
      "provisional_improvement_only":delta is not None and delta>0,
      "release_gate":"NOT_VALIDATED_FOR_LIVE_FINANCIAL_SIGNALS",
      "risk_notes":[
        "Model pretraining dates/assets may overlap historical test periods",
        "Historical spot OHLC forecast error does not imply options trading profitability",
        "Corporate actions, timestamps, bid/ask, taxes, liquidity and data licence unverified",
        "Model evaluation uses future observation DATES as historical exchange calendar only, never future OHLC values",
        "A model that underperforms the best naive baseline must be rejected"
      ],
      "cutoff_diagnostics":out}
