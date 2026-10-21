"""Fundtex Mission Control: deterministic, bounded plan for terminal-enabled AI agents.

Plans only; never spawns a model, fetches a feed, reads past chats, runs code,
updates files, contacts services, recommends trades or sends customer information.
Capabilities must be declared by the calling agent after it inspects its host.
"""
from __future__ import annotations
from hashlib import sha256
import json
import re

PROFILES=("generic","claude","codex","gemini","cursor","copilot","opencode")
MODES=("FAST","DEEP","INSTITUTIONAL")
ABILITIES=("terminal","web","subagents","python","filesystem")
ROLES={
    "sources":("Primary-source & timeline auditor",
               "Open permitted latest issuer/exchange filings; confirm published vs retrieved time, ticker/ISIN, scope and real evidence."),
    "fundamentals":("Company financials & forensic reviewer",
                    "Reconcile reporting periods, audited figures, units, cash quality, working capital, leverage, governance and sector-specific metrics."),
    "macro":("India macro & sector specialist",
             "Document RBI/SEBI/public-policy, rates, INR and sector channels and provide counter-causal explanations."),
    "quant":("Quant, forecast & portfolio-risk auditor",
             "Use only authorized source data, price adjustments and reproducible Fundtex arithmetic; test naive baselines, leakage, risk and costs."),
    "skeptic":("Independent falsification reviewer",
               "Attempt to disprove the main thesis, seek conflicting filings, reject unsupported alpha, disclose unverified and missing sources."),
    "editor":("Investment-committee evidence editor",
              "Resolve incompatible figures, preserve citations and timing, finalize a high-signal human-review memo with no hidden assumptions.")
}
DEEP_ORDER=("sources","fundamentals","macro","quant","skeptic","editor")
FAST_ORDER=("sources","fundamentals","skeptic")
QUANT_ORDER=("sources","quant","skeptic")
INTENT_KEYWORDS={
 "banking":("bank","nbfc","npa","lender","loan","credit","microfinance"),
 "portfolio":("portfolio","holding","asset allocation","correlation","risk contribution","mutual fund"),
 "events":("filing","news","announcement","earnings","merger","corporate action","event"),
 "quant":("predict","forecast","backtest","simulate","signal","alpha","quant","strategy"),
 "engineering":("integrate","build","code","plugin","mcp","connector","api","deploy"),
 "company":("equity","company","stock","share","valuation","financial statement","research")
}

def _classify(task):
    lower=task.casefold()
    scored=[(sum(1 for word in terms if re.search(r"(?<!\w)"+re.escape(word)+r"(?!\w)",lower)), -i, domain)
            for i,(domain,terms) in enumerate(INTENT_KEYWORDS.items())]
    score,_,name=max(scored)
    return name if score else "general"

def mission(task: str, *, agent="generic", mode="FAST", abilities=("terminal","python"),
            max_workers=5, confirmed_permission=False):
    if not isinstance(task,str) or not 1<=len(task.strip())<=800:
        raise ValueError("Task must be a short, non-sensitive description (1..800 chars)")
    if agent not in PROFILES or mode not in MODES:
        raise ValueError("Unknown profile or mode")
    if not isinstance(max_workers,int) or not 1<=max_workers<=6:
        raise ValueError("max_workers must be 1..6")
    if not isinstance(abilities,(tuple,list,set)) or any(x not in ABILITIES for x in abilities):
        raise ValueError("Unknown capability; provide a subset of terminal,web,subagents,python,filesystem")
    caps=tuple(sorted(set(abilities)))
    area=_classify(task)
    requested=FAST_ORDER if mode=="FAST" else (QUANT_ORDER if area=="quant" else DEEP_ORDER)
    # Always retain a critical independent skeptic even when user caps workers.
    capped=list(requested[:max_workers])
    if "skeptic" in requested and "skeptic" not in capped:
        capped[-1]="skeptic"
    chosen=list(dict.fromkeys(capped))
    parallel=bool("subagents" in caps and confirmed_permission and max_workers>1 and len(chosen)>1)
    can_research="web" in caps and confirmed_permission
    can_calculate="terminal" in caps and "python" in caps
    roles=[
        {"id":key,"name":ROLES[key][0],"objective":ROLES[key][1],
         "sources_must_be_verifiable":True,
         "must_report_uncertainty":True}
        for key in chosen
    ]
    return {
        "product":"Fundtex Financial Intelligence | Syntheon Technology",
        "engine":"MISSION_CONTROL_v0.1",
        "plan_only":True,
        "declared_agent":agent,"mode":mode,"task_category":area,
        "task_sha256":sha256(task.encode("utf-8")).hexdigest(),
        "task_input_echoed":False,
        "capabilities_declared":list(caps),
        "human_data_permission_confirmed":bool(confirmed_permission),
        "max_workers":max_workers,"assigned_roles":roles,
        "execution":"PARALLEL_IF_HOST_SUPPORTS_AND_APPROVED" if parallel else "SEQUENTIAL_FALLBACK",
        "readiness":{
            "can_calculate_locally":can_calculate,
            "may_access_authorized_web":can_research,
            "can_spawn_here":False,
            "requires_external_host_for_worker_execution":True
        },
        "steps":[
            "Confirm user objective, timeframe, source rights, approved work data and as-of IST.",
            "Read AGENTS.md, docs/AGENT_PORTABILITY.md and docs/ANALYST_DELIVERY_CONTRACT.md, then select relevant SKILL.md files.",
            "If installation is requested, inspect installer, install safely, run doctor and do both clearly synthetic diligence demos.",
            "If source tools are permitted, open actually accessible NSE/BSE/company/RBI/SEBI primary documents and record evidence timestamps.",
            "If permitted data and Python are available, run only relevant CLI tools; record source hashes and exact numeric assumptions.",
            "Make a bull/bear/unknown case, challenge it with the independent skeptic, reconcile reporting differences and source contradictions.",
            "Deliver a professional concise evidence-linked analyst packet and exactly three context-appropriate next tasks."
        ],
        "delivery_contract":{
            "opening":"Actionable executive result, with source/freshness status and no invented facts",
            "sections":["as_of_IST_and_scope","source_register","financial_quality","sector_and_macro",
                        "scenario_arguments","quantified_risks_if_tested","opposition_and_unknowns",
                        "confidence_in_evidence_not_predicted_profit","human_review_next_step"],
            "compliance":["No autonomous trades or personalized recommendations",
                          "No portfolio/client exfiltration or private historical-chat sweep",
                          "Never state live quote access unless tool results prove it",
                          "If missing valid research inputs, deliver a clearly labelled partial result and stop"],
            "quality_gates":["source_and_time_correct","formulas_reproducible",
                            "counterargument_present","baseline_if_prediction","no_false_precision",
                            "privacy_and_license_review"]
        },
        "fallbacks":{
            "missing_terminal":"Read protocol and provide setup instructions; do not claim installation or computations",
            "missing_web":"Use approved local inputs; label primary source verification pending",
            "missing_python":"Do sourced qualitative research only; do not claim a CLI ran",
            "missing_subagents":"Perform each specialist role sequentially with the same independent skepticism",
            "no_user_permission":"No remote data requests or worker sharing; request permission before restricted access",
            "no_verified_edge":"ABSTAIN from actionable forecasting and propose a falsifiable future validation"
        },
        "limits":["This plan creates no subagents and performs no tasks itself.",
                  "Performance is bounded by the agent host's permissions, actual market data and tools.",
                  "The word 'mission' is a workflow plan, not a trading signal or forecast guarantee."]
    }

def as_markdown(plan):
    lines=["# FUNDTEX — Analyst Mission Brief",
           "Mode: "+plan["mode"]+" | Role: "+plan["task_category"]+" | Runner: "+plan["declared_agent"],
           "Execution: "+plan["execution"]+" | No worker executed by this command",
           "",
           "## Specialist assignments"]
    for role in plan["assigned_roles"]:
        lines.append("- **"+role["name"]+"**: "+role["objective"])
    lines.append("")
    lines.append("## Execution")
    lines.extend(str(i)+". "+s for i,s in enumerate(plan["steps"],1))
    lines.extend(["","## Evidence and release gates"])
    lines.extend("- "+v for v in plan["delivery_contract"]["quality_gates"])
    lines.extend(["","No guarantee of price prediction, current live market access or model superiority."])
    return "\n".join(lines)+"\n"
