"""Reproducible, honest side-by-side analyst workflow benchmark.

Reviewer-scored measurements, never an AI-generated score. This does not read chats
or client files other than the explicitly supplied approved benchmark JSON.
"""
from __future__ import annotations
from datetime import date
from hashlib import sha256
import json
from pathlib import Path

def _number(value, key, *, min_val=0, max_val=1e9):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not min_val<=value<=max_val:
        raise ValueError("Invalid benchmark metric: "+key)
    return value

def _score_run(run, expected, *, label):
    if not isinstance(run,dict):
        raise ValueError(label+" run is required")
    mins=_number(run.get("minutes"),label+".minutes",max_val=10000)
    checked=_number(run.get("verified_facts"),label+".verified_facts",max_val=expected)
    errors=_number(run.get("unsupported_claims"),label+".unsupported_claims",max_val=10000)
    critical=_number(run.get("critical_errors"),label+".critical_errors",max_val=10000)
    docs=_number(run.get("primary_sources_opened"),label+".primary_sources_opened",max_val=10000)
    if any(x!=int(x) for x in (checked,errors,critical,docs)):
        raise ValueError("Count metrics must be integers")
    if critical>errors:
        raise ValueError("Critical errors cannot exceed unsupported claims")
    return {"minutes":mins,"verified_facts":checked,"unsupported_claims":errors,
            "critical_errors":critical,"primary_sources_opened":docs,
            "fact_recall":round(checked/expected,4),
            "source_supported_claim_precision":round(checked/(checked+errors),4) if checked+errors else None,
            "task_time_minutes":mins}

def evaluate(pilot):
    if not isinstance(pilot,dict) or not isinstance(pilot.get("tasks"),list):
        raise ValueError("Pilot requires tasks list")
    if not 1<=len(pilot["tasks"])<=30:
        raise ValueError("Pilot must contain 1..30 tasks")
    if pilot.get("data_class") not in ("SYNTHETIC_FIXTURE","DEIDENTIFIED_APPROVED","PUBLIC_ONLY"):
        raise ValueError("Do not submit confidential client data; explicit data class required")
    reviewer=pilot.get("reviewer_id")
    approved=pilot.get("reviewer_approved")
    if pilot["data_class"]=="SYNTHETIC_FIXTURE" and approved is True:
        raise ValueError("Fictional analyst pilot metrics cannot be human-approved as real results")
    if not isinstance(approved,bool) or not reviewer or len(str(reviewer))>100:
        raise ValueError("Explicit human reviewer identity and approval flag required")
    results=[]
    for task in pilot["tasks"]:
        if not isinstance(task,dict):
            raise ValueError("Malformed task")
        tid=str(task.get("id",""))
        if not tid or len(tid)>60:
            raise ValueError("Short task id required")
        expected=_number(task.get("expected_facts"),"expected_facts",min_val=1,max_val=500)
        if expected!=int(expected):
            raise ValueError("expected_facts must be integer")
        base=_score_run(task.get("baseline"),expected,label="baseline")
        new=_score_run(task.get("fundtex"),expected,label="fundtex")
        saved=round(base["minutes"]-new["minutes"],2)
        eligible=bool(approved and new["critical_errors"]==0 and
                      new["verified_facts"]>=base["verified_facts"] and
                      new["unsupported_claims"]<=base["unsupported_claims"])
        results.append({"task_id":tid,"baseline":base,"fundtex":new,
                        "time_saved_minutes":saved,
                        "time_saved_percent":round(saved/base["minutes"]*100,2) if base["minutes"] else None,
                        "evidence_quality_not_worse":new["unsupported_claims"]<=base["unsupported_claims"],
                        "approved_useful_workflow":eligible})
    totals=[x["time_saved_minutes"] for x in results]
    safe=sum(x["approved_useful_workflow"] for x in results)
    return {"product":"Fundtex Analyst Pilot Benchmark",
            "pilot_status":"REVIEWED_REPORTED_METRICS_NOT_INDEPENDENTLY_AUDITED" if approved else "NOT_REVIEWED_DO_NOT_ADVERTISE",
            "data_class":pilot["data_class"],"tasks_tested":len(results),
            "reviewer_approved":approved,
            "approved_tasks":safe,
            "time_saved_minutes_total":round(sum(totals),2),
            "tasks_with_positive_time_savings":sum(v>0 for v in totals),
            "measured_runs":results,
            "notes":[
                "Time and fact judgments are user/reviewer supplied, not independently measured or verified by this software.",
                "Use the same task/source cutoff, same access rights and comparable effort for baseline and Fundtex.",
                "Keep original run transcripts privately with reviewer and timestamps; never commit client materials.",
                "Do not claim Bloomberg-equivalent coverage or improved forecast alpha based on this scorecard."
            ]}

def from_file(path):
    p=Path(path)
    if not p.is_file() or p.stat().st_size>200_000:
        raise ValueError("Pilot input missing or too large")
    return evaluate(json.loads(p.read_text(encoding="utf-8")))
