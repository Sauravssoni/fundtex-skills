"""Fundtex: institutional memo arithmetic, human review gates and lunar placebo evaluation.

Caller-provided inputs are not independently authenticated. Research only, no execution.
"""
from __future__ import annotations
from datetime import date, datetime, timezone
from statistics import mean
import math
import random

def _num(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{field}: finite numeric value required")
    return float(value)

def _date(value, field):
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field}: YYYY-MM-DD required") from None
    if parsed > datetime.now(timezone.utc).date():
        raise ValueError(f"{field}: future dates not accepted")
    return parsed

def investment_committee(data):
    """Compute ratios and analyst-owned scenario arithmetic; never claim filing verification."""
    if not isinstance(data, dict) or not isinstance(data.get("issuer"), dict) or not isinstance(data.get("financials"), dict):
        raise ValueError("issuer and financials objects required")
    issuer, f = data["issuer"], data["financials"]
    if issuer.get("units") not in ("INR", "INR_CRORE", "USD", "USD_MILLION"):
        raise ValueError("Explicit currency and unit required")
    symbol = issuer.get("symbol", "")
    if not isinstance(symbol, str) or not (1 <= len(symbol) <= 32) or not all(c.isascii() and (c.isalnum() or c in "-_.") for c in symbol):
        raise ValueError("Short unambiguous exchange symbol required")
    _date(issuer.get("as_of"), "issuer.as_of")
    if issuer.get("per_share_currency") not in ("INR", "USD"):
        raise ValueError("Explicit per_share_currency INR or USD required: accounting units differ from per-share valuations")
    if not isinstance(issuer.get("period"), str) or not issuer["period"].strip():
        raise ValueError("Financial statement period required")
    allowed = ("revenue", "ebitda", "net_income", "cash_from_operations", "capital_expenditure",
               "total_debt", "cash_and_equivalents", "interest_expense", "ebit")
    values = {k: _num(f[k], k) if k in f and f[k] is not None else None for k in allowed}
    for key in ("revenue", "capital_expenditure", "total_debt", "cash_and_equivalents", "interest_expense"):
        if values[key] is not None and values[key] < 0:
            raise ValueError(f"{key} must be nonnegative")
    def ratio(a, b):
        return a / b if a is not None and b is not None and b > 0 else None
    v = values
    computed = {
        "ebitda_margin": ratio(v["ebitda"], v["revenue"]),
        "net_profit_margin": ratio(v["net_income"], v["revenue"]),
        "cfo_to_positive_net_income": ratio(v["cash_from_operations"], v["net_income"]),
        "interest_cover": ratio(v["ebit"], v["interest_expense"]),
        "free_cash_flow": v["cash_from_operations"] - v["capital_expenditure"] if v["cash_from_operations"] is not None and v["capital_expenditure"] is not None else None,
        "net_debt": v["total_debt"] - v["cash_and_equivalents"] if v["total_debt"] is not None and v["cash_and_equivalents"] is not None else None
    }
    refs = data.get("references", [])
    if not isinstance(refs, list) or len(refs) > 30:
        raise ValueError("0..30 source references allowed")
    registry = []
    for i, ref in enumerate(refs):
        if not isinstance(ref, dict) or not isinstance(ref.get("url"), str) or not ref["url"].startswith("https://"):
            raise ValueError("Each reference requires an HTTPS URL")
        registry.append({"url": ref["url"], "published": _date(ref.get("published"), f"references[{i}].published").isoformat(),
                         "verification": "NOT_INDEPENDENTLY_OPENED"})
    scenarios = data.get("scenarios", [])
    if not isinstance(scenarios, list) or len(scenarios) > 12:
        raise ValueError("scenarios must contain no more than 12 cases")
    expectation = None
    if scenarios:
        if len(scenarios) < 2:
            raise ValueError("At least bear and bull assumptions required")
        clean = []
        for i, scenario in enumerate(scenarios):
            if not isinstance(scenario, dict) or not scenario.get("name") or not scenario.get("assumptions"):
                raise ValueError("Each scenario needs a name and explicit assumptions")
            p = _num(scenario.get("probability"), f"scenario[{i}].probability")
            price = _num(scenario.get("value_per_share"), f"scenario[{i}].value_per_share")
            if not 0 <= p <= 1 or price < 0:
                raise ValueError("Scenario probability and valuation outside permitted ranges")
            clean.append({"name": str(scenario["name"])[:70], "probability": p, "value_per_share": price,
                          "assumptions": str(scenario["assumptions"])[:600]})
        if abs(sum(c["probability"] for c in clean) - 1) > 1e-6:
            raise ValueError("Scenario probabilities must sum to one; cannot normalize silently")
        expectation = {"hypothetical_probability_weighted_value_per_share": sum(c["probability"] * c["value_per_share"] for c in clean),
                       "cases": clean, "not_a_market_price_forecast": True}
    blockers = ["Primary source documents not independently read or reconciled"]
    if len(registry) < 2: blockers.append("Fewer than two dated documentary references")
    if any(v[k] is None for k in ("revenue", "net_income", "cash_from_operations", "total_debt", "cash_and_equivalents")):
        blockers.append("Critical financial-statement inputs missing")
    if expectation is None: blockers.append("No stated bear/base/bull probabilities and assumptions")
    warnings = []
    if computed["cfo_to_positive_net_income"] is not None and computed["cfo_to_positive_net_income"] < 0.5:
        warnings.append("Weak CFO/NI cash conversion; inspect working capital and accruals")
    if v["revenue"] == 0:
        warnings.append("Zero revenue; standard operating margins unavailable")
    raw_origin = data.get("provenance", "")
    assurance = "SYNTHETIC_FIXTURE" if isinstance(raw_origin, str) and raw_origin.startswith("SYNTHETIC_FIXTURE") else "USER_SUPPLIED_UNVERIFIED"
    return {"engine": "FUNDTEX_INVESTMENT_COMMITTEE_v1", "issuer": issuer,
            "input_assurance": assurance, "ratios": computed,
            "scenario_model": expectation, "source_register": registry,
            "risk_flags": warnings, "review_blockers": blockers,
            "verdict": "HUMAN_VERIFICATION_REQUIRED", "research_only": True}

_EPOCH = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
_PERIOD_DAYS = 29.53058867
_PHASES = ("new", "waxing", "full", "waning")

def lunar_phase(day):
    d = _date(day, "date")
    noon = datetime(d.year, d.month, d.day, 12, tzinfo=timezone.utc)
    frac = (((noon - _EPOCH).total_seconds() / 86400) % _PERIOD_DAYS) / _PERIOD_DAYS
    return _PHASES[min(int(frac * 4), 3)]

def lunar_placebo(rows, *, seed=42, permutations=1000):
    """Pre-select a phase using training history; attempt to falsify on untouched holdout."""
    if not isinstance(rows, list) or not 160 <= len(rows) <= 100000:
        raise ValueError("Need 160..100000 source-dated daily-return rows")
    if not isinstance(permutations, int) or not 100 <= permutations <= 10000:
        raise ValueError("Permutations must be 100..10000")
    seen = set()
    samples = []
    for item in rows:
        if not isinstance(item, dict):
            raise ValueError("Each row must include date and return")
        d = _date(item.get("date"), "row.date")
        r = _num(item.get("return"), "row.return")
        if d in seen or (samples and d <= samples[-1][0]) or r < -1:
            raise ValueError("Unique strictly increasing dates and valid simple returns required")
        seen.add(d)
        samples.append((d, r, lunar_phase(d.isoformat())))
    cut = int(len(samples) * 0.7)
    train, holdout = samples[:cut], samples[cut:]
    groups = {p: [v for _, v, phase in train if phase == p] for p in _PHASES}
    if any(len(group) < 10 for group in groups.values()):
        raise ValueError("Insufficient training observations per phase")
    selected = max(_PHASES, key=lambda phase: mean(groups[phase]))
    is_selected = [phase == selected for _, _, phase in holdout]
    n_selected = sum(is_selected)
    if not 10 <= n_selected <= len(holdout) - 10:
        raise ValueError("Holdout phase samples insufficient")
    values = [v for _, v, _ in holdout]
    def contrast(vs):
        return mean(v for v, yes in zip(vs, is_selected) if yes) - mean(v for v, yes in zip(vs, is_selected) if not yes)
    observed = contrast(values)
    randomizer = random.Random(seed)
    extremes = 0
    for _ in range(permutations):
        trial = values[:]
        randomizer.shuffle(trial)
        extremes += abs(contrast(trial)) >= abs(observed)
    return {"engine": "FUNDTEX_LUNAR_PLACEBO_v1", "train_size": len(train),
            "heldout_size": len(holdout), "training_selected_phase": selected,
            "heldout_return_contrast": observed,
            "simple_randomization_p_value": (extremes + 1) / (permutations + 1),
            "seed": seed, "input_assurance": "USER_SUPPLIED_UNVERIFIED",
            "verdict": "EXPLORATORY_ONLY_NOT_A_TRADING_SIGNAL",
            "limitations": ["Approximate lunar phase, not precise ephemeris",
                            "Calendar, serial correlation, multiple comparisons, and regime confounding remain",
                            "No demonstrated causal, predictive, or executable advantage"]}
