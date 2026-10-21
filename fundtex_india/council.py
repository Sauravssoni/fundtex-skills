"""Offline optional multi-agent research desk planner.

Produces a bounded task graph; it does NOT spawn workers, read private data,
or send anything to external services. The host and user remain in control.
"""
from __future__ import annotations

ROLES=(
    ("primary_sources","Primary Source Auditor","Verify actually opened NSE/BSE/issuer documents, exact publication timestamps, symbol/ISIN and missing or conflicting facts."),
    ("financial_forensics","Fundamental Forensics Analyst","Review sourced balance sheet, operating cash flow, receivables, debt, audit and governance; use sector-correct measures."),
    ("macro_sector","India Macro/Sector Analyst","Verify RBI, SEBI and rate/INR/commodity sector exposures; challenge simplistic causal interpretations."),
    ("quant_risk","Quant & Risk Analyst","Run approved read-only Fundtex commands; test pricing adjustments, baselines, leakage, costs, tail-risk and ABSTAIN gates."),
    ("independent_skeptic","Independent Skeptic","Form the strongest contrary thesis; flag unverified claims, missing alternatives and overconfident forecast language."),
    ("review_editor","Research Review Editor","Reconcile source contradictions and as-of dates; preserve traceable assumptions and produce reviewer-ready brief.")
)

def plan(*, scope: str="India equities", max_workers: int=5, parallel: bool=False, mode: str="DEEP") -> dict:
    if not isinstance(scope,str) or len(scope)>400 or not scope.strip():
        raise ValueError("Please provide a short non-sensitive task scope (1–400 characters)")
    if mode not in ("QUICK","DEEP","QUANT"):
        raise ValueError("mode must be QUICK, DEEP or QUANT")
    if not isinstance(max_workers,int) or not 1<=max_workers<=6:
        raise ValueError("max_workers must be between 1 and 6")
    selected=(ROLES[0],ROLES[4]) if mode=="QUICK" else (
        (ROLES[3],ROLES[4],ROLES[0]) if mode=="QUANT" else ROLES
    )
    n=min(max_workers,len(selected))
    chosen=selected[:n]
    return {
        "product":"Fundtex Financial Intelligence | Syntheon Technology",
        "plan_type":"SUGGESTED_TASK_GRAPH_NOT_EXECUTION",
        "mode":mode,
        "worker_count":len(chosen),
        "recommended_parallel":bool(parallel and len(chosen)>1),
        "requires_host_subagents":bool(parallel and len(chosen)>1),
        "user_authorization_required_for_sensitive_inputs":True,
        "data_access":"NONE_PERFORMED",
        "task_scope":"USER_PROVIDED_SCOPE_NOT_ECHOED",
        "workers":[{"id":rid,"role":title,"bounded_task":task,
                    "deliverable":"Dated primary evidence, source type, verified figures, contradictions, limitations"}
                   for rid,title,task in chosen],
        "lead_instructions":[
            "Confirm as-of IST, venue/symbol, source rights, privacy limits, time and compute budget.",
            "If host does not support authorized parallel workers, run all roles sequentially.",
            "Reconciling conflicting facts is required; do not average incompatible periods or share counts.",
            "Show primary sources actually consulted, quantified assumptions, strongest skeptic and review gaps.",
            "No broker execution, no confidential-data exfiltration and no guaranteed predictive alpha."
        ]
    }
