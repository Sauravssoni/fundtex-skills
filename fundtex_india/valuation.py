"""Explicit-input discounted cash-flow scenario, never confused with a price feed."""
from __future__ import annotations
import math

def _number(cfg, key):
    value = float(cfg[key])
    if not math.isfinite(value):
        raise ValueError(f"{key} must be finite")
    return value

def dcf(cfg: dict):
    revenue = _number(cfg, "revenue_inr")
    margin = _number(cfg, "fcf_margin")
    growth = _number(cfg, "revenue_growth")
    wacc = _number(cfg, "wacc")
    terminal = _number(cfg, "terminal_growth")
    cash = _number(cfg, "net_cash_inr")
    shares = _number(cfg, "shares_outstanding")
    years = int(cfg.get("forecast_years", 5))
    if not 1 <= years <= 15 or revenue <= 0 or shares <= 0 or not -1 <= margin <= 1 or not -0.9 < growth < 1 or not 0 < wacc < 1 or not -0.5 < terminal < wacc:
        raise ValueError("DCF requires sane positive shares/revenue and terminal_growth < wacc")
    def calc(rate, tg):
        if rate <= tg or rate <= 0:
            return None
        pv, last = 0.0, 0.0
        for yr in range(1, years+1):
            fcf = revenue * (1 + growth)**yr * margin
            pv += fcf / (1 + rate)**yr
            last = fcf
        terminal_pv = (last * (1 + tg) / (rate - tg)) / (1 + rate)**years
        return (pv + terminal_pv + cash) / shares
    per_share = calc(wacc, terminal)
    if per_share is None:
        raise ValueError("Invalid discount factors")
    sensitivity = []
    for bump_rate in [-0.02, -0.01, 0, 0.01, 0.02]:
        row = {}
        for bump_g in [-0.01, -0.005, 0, 0.005, 0.01]:
            key = f"g={terminal+bump_g:.3f}"
            row[key] = calc(wacc + bump_rate, terminal + bump_g)
        sensitivity.append({"wacc":wacc+bump_rate, "fair_value_inr_per_share":row})
    return {"scenario_value_inr_per_share":per_share,
            "assumptions":{k:cfg[k] for k in ("revenue_inr","fcf_margin","revenue_growth","wacc","terminal_growth","net_cash_inr","shares_outstanding")},
            "forecast_years":years, "sensitivity":sensitivity,
            "quality":"USER_HYPOTHESIS_NOT_OBSERVED_MARKET_FACT",
            "caveats":["DCF is assumption-driven and not an investment recommendation.",
                       "Validate cash flows, share count, dilution, working capital and financial statements.",
                       "Debt/equity and banks may require different valuation methodologies."]}
