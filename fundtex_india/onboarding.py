"""Offline, opt-in Fundtex analyst onboarding. No local history, filesystem or network search.

The calling agent may include an explicitly authorized short task description;
otherwise safe example prompts are chosen. Suggestions are educational research
workflows and do not imply that any financial data was loaded.
"""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import sys

PLAYBOOK = (
    ("company", ("earnings", "stock", "equity", "company", "fundamental", "result", "nse", "bse", "annual", "invest"),
     "Research the next company I name on NSE/BSE: verify the latest primary filings and dates, inspect cash-flow versus earnings, challenge the bull and bear cases, show valuation assumptions, and identify what is still unverified."),
    ("portfolio", ("portfolio", "holdings", "allocation", "mutual", "asset", "fund", "wealth", "risk", "rebalanc"),
     "Audit a portfolio CSV I authorize: assess sector concentration, correlations, drawdown, historical tail risk and risk contribution; compare against sensible benchmarks and flag missing corporate-action or transaction-cost information."),
    ("macro", ("macro", "rates", "rbi", "inflation", "currency", "sector", "economy", "fx", "oil", "policy"),
     "Prepare an India macro-to-sector briefing: verify relevant RBI, SEBI and company sources, connect plausible rate/FX/commodity drivers, give contrary explanations and a dated monitoring checklist."),
    ("forecast", ("model", "forecast", "predict", "signal", "backtest", "quant", "simulation", "strategy", "alpha"),
     "Test a sourced Indian equity price history with Fundtex Forecast Lab and GOD EYE: compare chronological probabilities to naïve baselines, check intervals and model leakage, disclose actual costs and ABSTAIN if edge is not supported."),
    ("events", ("news", "filings", "merger", "event", "ipo", "corporate", "disclosure", "announcement"),
     "Identify the most material changes in an Indian company or sector I specify: timestamp and verify primary exchange announcements, separate events from market speculation, then assess possible second-order impacts and unanswered questions."),
)

DEFAULTS = (
    "Research one NSE/BSE stock I select using primary filings and an adversarial bull/bear/unknown thesis, with dates and a clear NOT VERIFIED label for missing information.",
    "Evaluate an authorized portfolio CSV for concentration, downside risk, correlations and unrealistic assumptions; never transmit private holdings without my approval.",
    "Compare a sourced Indian price series against buy-and-hold and simple probability baselines using the Fundtex forecast and GOD EYE tools; report failures and abstain when no edge is proven.",
)

def suggest(context: str = "") -> dict:
    if len(context) > 1500:
        raise ValueError("Context description must be <=1500 characters; do not paste personal records")
    lower=context.lower()
    ranks=sorted(((sum(1 for word in words if word in lower), -i, name, prompt)
                  for i,(name,words,prompt) in enumerate(PLAYBOOK)),reverse=True)
    chosen=[item[3] for item in ranks if item[0] > 0][:3]
    for fallback in DEFAULTS:
        if len(chosen) == 3:
            break
        if fallback not in chosen:
            chosen.append(fallback)
    return {
        "product":"Fundtex Financial Intelligence | Syntheon Technology",
        "mode":"OFFLINE_FIRST_TASK_SUGGESTIONS",
        "context_access":"EXPLICIT_USER_OR_AGENT_PROVIDED_DESCRIPTION_ONLY",
        "suggestions":chosen,
        "research_only":True,
        "requires_authorized_inputs":True,
        "notice":"Agent chat history, files, external account data and market feeds were not searched. To personalize further, ask what daily research the analyst currently performs."
    }

def doctor(home: str | None = None, *, repo_root: str | None = None) -> dict:
    homepath=Path(home if home is not None else os.path.expanduser("~")).expanduser()
    root=Path(repo_root).resolve() if repo_root else Path(__file__).resolve().parents[1]
    targets=(".claude/skills",".codex/skills",".agents/skills")
    expected=("fundtex-god-eye","fundtex-chart-technician","fundtex-analyst-pack","fundtex-workbook-builder","fundtex-visuals-reporting","fundtex-analyst-council","fundtex-analyst-pilot","fundtex-india-regulatory","fundtex-india-diligence","fundtex-india-forecast","fundtex-india-market",
              "fundtex-india-news","fundtex-india-risk","fundtex-india-portfolio",
              "fundtex-india-valuation","fundtex-india-brief")
    manifest={}
    for rel in targets:
        folder=homepath/rel
        found=[name for name in expected if (folder/name/"SKILL.md").is_file()]
        manifest[rel]={"india_skills_present":len(found),"india_skills_expected":len(expected),
                       "missing":[name for name in expected if name not in found]}
    checkout_cli=root/"fundtex_india"/"cli.py"
    installed_cli=homepath/".local/share/fundtex-intelligence/fundtex_india/cli.py"
    engine_stale=None
    if checkout_cli.is_file() and installed_cli.is_file():
        origin_hash=hashlib.sha256(checkout_cli.read_bytes()).digest()
        snapshot_hash=hashlib.sha256(installed_cli.read_bytes()).digest()
        engine_stale=origin_hash!=snapshot_hash
    return {
        "product":"Fundtex Financial Intelligence","python":sys.version.split()[0],
        "installed_engine_stale_relative_to_checkout":engine_stale,
        "upgrade_policy":"Never overwrite installed engine without explicit user approval",
        "python_supported":sys.version_info >= (3,9),
        "engine_importable":True,
        "engine_origin":str(Path(__file__).resolve().parent),
        "installation":manifest,
        "all_india_skills_installed":all(len(item["missing"])==0 for item in manifest.values()),
        "fundtex_launcher_present":(homepath/".local/bin/fundtex").is_file(),
        "readme_available":(root/"README.md").is_file(),
        "checks_are_offline":True,
        "notice":"Only expected installation paths were inspected. No private chats, documents, API keys or accounts were accessed."
    }

def welcome() -> str:
    suggestions=suggest()["suggestions"]
    lines=[
        "",
        "FUNDTEX FINANCIAL INTELLIGENCE  •  INDIA RESEARCH EDITION",
        "-----------------------------------------------------------",
        "Installed skills support Claude, Codex and compatible agents.",
        "Try one of these research-first prompts:",
    ]
    for idx,prompt in enumerate(suggestions,1):
        lines.append(f"  {idx}. {prompt}")
    lines.extend([
        "",
        "Personalize: fundtex onboard --context 'I research Indian banks, NBFCs and credit'",
        "Healthcheck:  fundtex doctor",
        "Agent plan:   fundtex mission --task 'India banking peer diligence' --mode DEEP",
        "Evidence first. No live-price guarantee. No autonomous trades.",
        "For contextual past-work suggestions ask your agent to consider only",
        "conversation/memory sources it is actually authorized to access.",
        ""
    ])
    return "\n".join(lines)

if __name__ == "__main__":
    print(welcome())
