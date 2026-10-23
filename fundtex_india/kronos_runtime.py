"""Optional Kronos offline inference adapter. Does not fetch weights or run broker APIs.

Prerequisite: approved unmodified upstream checkout pinned to exact commit
plus separately inspected, locally cached Hugging Face safetensors directories.
No network, subprocess trading, torch.load, pickles or auto installation here.
"""
from __future__ import annotations
from pathlib import Path
import importlib
import importlib.util
import json
import os
import subprocess
import sys
from .kronos_lab import PINNED_SHA, SUPPORTED

def doctor(*,checkout=None,weights=None,tokenizer=None,model_size="mini"):
    if model_size not in SUPPORTED:raise ValueError("Only the official Kronos-mini/small/base are supported")
    requirements={x:importlib.util.find_spec(x) is not None for x in
                  ("numpy","pandas","torch","einops","huggingface_hub","safetensors")}
    source=None
    if checkout:
        p=Path(checkout).expanduser().resolve()
        source=_check_checkout(p,raise_on_invalid=False)
    files={"weights":bool(weights and (Path(weights).expanduser()/ "model.safetensors").is_file() and
                            (Path(weights).expanduser()/ "config.json").is_file()),
           "tokenizer":bool(tokenizer and (Path(tokenizer).expanduser()/ "model.safetensors").is_file() and
                               (Path(tokenizer).expanduser()/ "config.json").is_file())}
    return {"engine":"FUNDTEX_KRONOS_OFFLINE_RUNTIME_DOCTOR",
      "upstream_commit":PINNED_SHA,"official_model":SUPPORTED[model_size][0],
      "python_optional_dependencies":requirements,"checkout":source,"local_safetensors":files,
      "ready_for_approved_offline_inference":all(requirements.values()) and source is not None and source.get("trusted",False) and all(files.values()),
      "network_downloads_performed":False,"model_inference_executed":False,
      "broker_connected":False,"trading_enabled":False}

def _check_checkout(root,*,raise_on_invalid=True):
    good=(root/"model/kronos.py").is_file() and (root/"model/module.py").is_file()
    head=None;remote=None;clean=False
    if good:
        try:
            def run(*args):
                return subprocess.run(["git","-C",str(root),*args],capture_output=True,text=True,check=True,timeout=8).stdout.strip()
            head=run("rev-parse","HEAD")
            remote=run("remote","get-url","origin")
            changes=run("status","--porcelain=v1","--untracked-files=all")
            clean=not changes
        except (OSError,subprocess.SubprocessError):pass
    valid=good and head==PINNED_SHA and remote in (
        "https://github.com/shiyu-coder/Kronos.git","https://github.com/shiyu-coder/Kronos",
        "git@github.com:shiyu-coder/Kronos.git") and clean
    result={"trusted":bool(valid),"pinned_commit_matches":head==PINNED_SHA,
            "official_origin":remote in ("https://github.com/shiyu-coder/Kronos.git",
               "https://github.com/shiyu-coder/Kronos","git@github.com:shiyu-coder/Kronos.git"),
            "clean_checkout":clean}
    if not valid and raise_on_invalid:raise ValueError("Approved original Kronos checkout must be clean and pinned to official commit")
    return result

def _check_local_checkpoint(path):
    p=Path(path).expanduser().resolve(strict=True)
    if not p.is_dir() or not (p/"config.json").is_file() or not (p/"model.safetensors").is_file():
        raise ValueError("Offline Kronos requires inspected local safetensors and config, no remote download")
    if (p/"pytorch_model.bin").exists():
        raise ValueError("Unsafe/ambiguous pickle checkpoint present; require safetensors-only folder")
    if (p/"model.safetensors").stat().st_size>2_000_000_000:
        raise ValueError("Model beyond approved 2GB bound")
    config=json.loads((p/"config.json").read_text(encoding="utf-8"))
    if not isinstance(config,dict):raise ValueError("Invalid model config")
    return p

def load_offline(*,checkout,weights,tokenizer,model_size="mini",device="cpu",seed=42):
    if model_size not in SUPPORTED:raise ValueError("Unknown official Kronos size")
    if device not in ("cpu","mps","cuda:0"):raise ValueError("Explicit CPU/MPS/CUDA device required")
    if isinstance(seed,bool) or not isinstance(seed,int) or not 0<=seed<=2147483647:
        raise ValueError("Bounded seed required")
    root=Path(checkout).expanduser().resolve(strict=True)
    _check_checkout(root)
    wp=_check_local_checkpoint(weights);tp=_check_local_checkpoint(tokenizer)
    d=doctor(checkout=root,weights=wp,tokenizer=tp,model_size=model_size)
    if not d["ready_for_approved_offline_inference"]:
        raise ValueError("Missing runtime dependencies or checkpoint source gate")
    import numpy as np
    import pandas as pd
    import torch
    # Intentional local import from a fully pinned, clean upstream checkout.
    if "model" in sys.modules:
        existing=getattr(sys.modules["model"],"__file__","")
        if not existing or not Path(existing).resolve().is_relative_to(root):
            raise ValueError("Conflicting Python 'model' module already loaded")
    sys.path.insert(0,str(root))
    try:
        official=importlib.import_module("model")
        torch.manual_seed(seed)
        selected=official.Kronos.from_pretrained(str(wp))
        tok=official.KronosTokenizer.from_pretrained(str(tp))
        selected.eval();tok.eval()
        predictor=official.KronosPredictor(selected,tok,device=device,max_context=SUPPORTED[model_size][2])
    finally:
        sys.path.remove(str(root))
    def predict(history,destination_dates):
        if not history or not destination_dates:raise ValueError("Past OHLC and future session dates required")
        df=pd.DataFrame([{"open":r["open"],"high":r["high"],"low":r["low"],"close":r["close"],
                          "volume":r["volume"] if r["volume"] is not None else 0.0} for r in history])
        x_timestamp=pd.to_datetime([r["date"] for r in history])
        y_timestamp=pd.to_datetime(list(destination_dates))
        # Preceding model call only sees the history slice, no future prices or account data.
        with torch.inference_mode():
            result=predictor.predict(df=df,x_timestamp=x_timestamp,y_timestamp=y_timestamp,
                                     pred_len=len(destination_dates),T=1.0,top_p=0.9,
                                     sample_count=1,verbose=False)
        return [float(v) for v in result["close"].tolist()]
    return predict
