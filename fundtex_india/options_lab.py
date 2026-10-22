"""Fundtex India option payoff workbench.

Explicit premiums and lot sizes only. Expiry intrinsic-payoff arithmetic, not an
option-pricing model, a broker margin engine, a guarantee of capped real losses,
or a validated predictor. No credentials, orders, quotes or network access.
Rates use a dated 2026 NSE/Zerodha example tariff, configurable for a real broker.
"""
from __future__ import annotations

from datetime import date
from hashlib import sha256
import json
import math
import random
from statistics import mean
from typing import Any

RATE_REFERENCES = {
    "stt_sell_option_premium": "https://www.nseindia.com/static/products-services/equity-derivatives-securities-transaction-tax",
    "stamp_options_buy": "https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies",
    "example_broker_and_exchange_charges": "https://zerodha.com/charges",
    "rates_checked": "2026-10-23",
}
DEFAULT_RATES = {
    "brokerage_per_leg_inr": 20.0,  # Illustrative Zerodha-like execution fee, per opened leg
    "stt_sell_premium_rate": 0.0015,  # April 1 2026 option sale STT
    "stamp_buy_premium_rate": 0.00003,
    "exchange_premium_rate": 0.0003553,
    "sebi_turnover_rate": 0.000001,
    "gst_on_fees_rate": 0.18,
}
def _number(x: Any, name: str, lower: float = 0, upper: float | None = None):
    if isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x):
        raise ValueError(name + " must be a finite numeric value")
    if x < lower or upper is not None and x > upper:
        raise ValueError(name + " is outside permitted range")
    return float(x)

def _integer(x: Any, name: str, lower: int, upper: int):
    if isinstance(x, bool) or not isinstance(x, int) or not lower <= x <= upper:
        raise ValueError(name + " must be an integer within permitted bounds")
    return x

def _parse_input(spec: dict):
    if not isinstance(spec, dict):
        raise ValueError("Strategy specification must be a JSON object")
    allowed = {"spot", "lot_size", "underlying", "valuation_date", "expiry_date", "legs",
               "rates", "annualized_volatility", "annual_risk_free", "annual_dividend_yield", "paths", "seed",
               "max_risk_inr", "require_defined_risk", "data_quality"}
    if set(spec)-allowed: raise ValueError("Unknown strategy specification fields")
    spot = _number(spec.get("spot"), "spot", 0.001)
    lot = _integer(spec.get("lot_size"), "lot_size", 1, 100000)
    symbol = spec.get("underlying")
    if not isinstance(symbol,str) or not 1<=len(symbol)<=50 or not all(c.isascii() and (c.isalnum() or c in "-_.^") for c in symbol):
        raise ValueError("Underlying identity must be provided, never guessed")
    try:
        valued = date.fromisoformat(spec["valuation_date"])
        expiry = date.fromisoformat(spec["expiry_date"])
    except (KeyError,ValueError,TypeError):
        raise ValueError("valuation_date and expiry_date must be ISO YYYY-MM-DD") from None
    if expiry < valued or (expiry-valued).days>365:
        raise ValueError("Expiry must be 0..365 calendar days after valuation date")
    legs = spec.get("legs")
    if not isinstance(legs, list) or not 1<=len(legs)<=8:
        raise ValueError("Supply one to eight option legs")
    positions=[]
    for idx,leg in enumerate(legs):
        if not isinstance(leg,dict) or set(leg)!={"kind","side","strike","premium","lots"}:
            raise ValueError("Every leg requires exactly kind/side/strike/premium/lots")
        if leg["kind"] not in ("call","put") or leg["side"] not in ("buy","sell"):
            raise ValueError("Option leg must be call/put and buy/sell")
        strike=_number(leg["strike"],"strike",0.001)
        premium=_number(leg["premium"],"premium",0)
        if premium>spot*10:
            raise ValueError("Premium far above spot requires independent review")
        lots=_integer(leg["lots"],"lots",1,1000)
        positions.append({"kind":leg["kind"],"side":leg["side"],"strike":strike,
                          "premium":premium,"lots":lots,"units":lots*lot,
                          "direction":1 if leg["side"]=="buy" else -1})
    rates=dict(DEFAULT_RATES)
    provided=spec.get("rates",{})
    if not isinstance(provided,dict) or set(provided)-set(rates):
        raise ValueError("Rate overrides must use named fee fields")
    for key,val in provided.items():rates[key]=_number(val,key,0,1000 if key=="brokerage_per_leg_inr" else 0.05)
    buy_turn=sum(p["premium"]*p["units"] for p in positions if p["side"]=="buy")
    sell_turn=sum(p["premium"]*p["units"] for p in positions if p["side"]=="sell")
    total_turn=buy_turn+sell_turn
    brokerage=rates["brokerage_per_leg_inr"]*len(positions)
    stt=rates["stt_sell_premium_rate"]*sell_turn
    stamp=rates["stamp_buy_premium_rate"]*buy_turn
    exchange=rates["exchange_premium_rate"]*total_turn
    sebi=rates["sebi_turnover_rate"]*total_turn
    gst=rates["gst_on_fees_rate"]*(brokerage+exchange+sebi)
    charges={"brokerage":brokerage,"stt_on_open_sell_premium":stt,
             "stamp_duty_on_open_buy_premium":stamp,"exchange_transaction":exchange,
             "sebi_turnover":sebi,"gst_on_eligible_fees":gst}
    fee=sum(charges.values())
    credit=sum(p["direction"]*-p["premium"]*p["units"] for p in positions)
    return spot,lot,symbol,valued,expiry,positions,rates,charges,fee,credit

def _payoff(price, positions, credit, fees):
    intrinsic=sum(p["direction"]*p["units"]*
        (max(price-p["strike"],0) if p["kind"]=="call" else max(p["strike"]-price,0))
        for p in positions)
    return credit+intrinsic-fees

def _geometry(positions,credit,fee):
    # Exact piecewise-linear intrinsic payoff, evaluated at every kink.
    strikes=sorted({p["strike"] for p in positions})
    xs=[0.0]+strikes
    values=[_payoff(x,positions,credit,fee) for x in xs]
    slope=sum(p["direction"]*p["units"] for p in positions if p["kind"]=="call")
    roots=set()
    for i in range(len(xs)-1):
        a,b=xs[i],xs[i+1];fa,fb=values[i],values[i+1]
        if abs(fa)<1e-8:roots.add(round(a,6))
        if abs(fb)<1e-8:roots.add(round(b,6))
        if fa*fb<0:
            roots.add(round(a-fa*(b-a)/(fb-fa),6))
    if slope and xs:
        after=xs[-1]-values[-1]/slope
        if after>xs[-1]:roots.add(round(after,6))
    low=min(values);high=max(values)
    return {
        "break_even_underlying_prices":sorted(roots),
        "max_model_profit_inr":None if slope>0 else round(high,2),
        "max_model_loss_inr":None if slope<0 else round(max(0,-low),2),
        "profit_unbounded_in_model":slope>0,
        "loss_unbounded_in_model":slope<0,
        "tail_net_call_slope_inr_per_underlying_point":slope,
        "model_payoff_at_zero_inr":round(values[0],2),
    }

def _greeks(spot, positions, *, sigma, risk_free, dividend_yield, years):
    """Illustrative European Black-Scholes aggregate sensitivities, not observed option-chain greeks."""
    if years<=0 or sigma<=0:
        return {"status":"NOT_COMPUTABLE_ZERO_TIME_OR_VOLATILITY"}
    root=math.sqrt(years);discount_r=math.exp(-risk_free*years);discount_q=math.exp(-dividend_yield*years)
    total={"delta_inr_per_underlying_point":0.0,"gamma_inr_per_underlying_point_squared":0.0,
           "vega_inr_per_one_percentage_point_volatility":0.0,"theta_inr_per_calendar_day":0.0,
           "rho_inr_per_one_percentage_point_rate":0.0}
    def ncdf(x):return .5*math.erfc(-x/math.sqrt(2))
    for leg in positions:
        k=leg["strike"]
        d1=(math.log(spot/k)+(risk_free-dividend_yield+0.5*sigma*sigma)*years)/(sigma*root)
        d2=d1-sigma*root
        pdf=math.exp(-.5*d1*d1)/math.sqrt(2*math.pi)
        common=-spot*discount_q*pdf*sigma/(2*root)
        if leg["kind"]=="call":
            delta=discount_q*ncdf(d1)
            theta=common-risk_free*k*discount_r*ncdf(d2)+dividend_yield*spot*discount_q*ncdf(d1)
            rho=k*years*discount_r*ncdf(d2)
        else:
            delta=discount_q*(ncdf(d1)-1)
            theta=common+risk_free*k*discount_r*ncdf(-d2)-dividend_yield*spot*discount_q*ncdf(-d1)
            rho=-k*years*discount_r*ncdf(-d2)
        factor=leg["direction"]*leg["units"]
        total["delta_inr_per_underlying_point"]+=factor*delta
        total["gamma_inr_per_underlying_point_squared"]+=factor*discount_q*pdf/(spot*sigma*root)
        total["vega_inr_per_one_percentage_point_volatility"]+=factor*spot*discount_q*pdf*root*.01
        total["theta_inr_per_calendar_day"]+=factor*theta/365
        total["rho_inr_per_one_percentage_point_rate"]+=factor*rho*.01
    return {"status":"ILLUSTRATIVE_EUROPEAN_BLACK_SCHOLES_NOT_MARKET_GREEKS",
            "assumptions":{"annualized_volatility":sigma,"annual_risk_free":risk_free,
                           "annual_dividend_yield":dividend_yield,"days_to_expiry":round(years*365,6)},
            "aggregate":{k:round(v,6) for k,v in total.items()},
            "warnings":["European Black-Scholes with flat input volatility, rates and dividend yield",
                        "No fitted volatility surface, early exercise, gap jump, borrow effects or actual option bid-ask",
                        "Greeks are local sensitivities, not a profit probability or a margin guarantee"]}

def evaluate(spec: dict):
    spot,lot,symbol,valued,expiry,positions,rates,charges,fee,credit=_parse_input(spec)
    g=_geometry(positions,credit,fee)
    if spec.get("require_defined_risk",True) is not False and g["loss_unbounded_in_model"]:
        raise ValueError("Strategy has unbounded modeled loss; set require_defined_risk=false to study without execution")
    budget=spec.get("max_risk_inr")
    if budget is not None:
        budget=_number(budget,"max_risk_inr",0.01)
        if g["loss_unbounded_in_model"] or g["max_model_loss_inr"]>budget:
            raise ValueError("Modeled maximum loss exceeds stated research risk budget")
    grid_end=max(spot*2,1.6*max(p["strike"] for p in positions),1)
    prices=[round(grid_end*i/120,6) for i in range(121)]
    payoff=[{"underlying_at_expiry":p,"model_pnl_inr":round(_payoff(p,positions,credit,fee),2)}
            for p in prices]
    curve={ "underlying":symbol, "as_of":valued.isoformat(), "expiry":expiry.isoformat(),
        "lot_size_user_verified":False, "lot_size_user_supplied":lot,
        "spot_user_supplied_not_live_quote":spot,
        "total_legs":len(positions),"opening_net_premium_credit_inr":round(credit,2),
        "opening_cost_breakdown_inr":{k:round(v,4) for k,v in charges.items()},
        "opening_total_cost_inr":round(fee,4),
        "net_initial_cash_flow_after_entry_fees_inr":round(credit-fee,2),
        "payoff_model":"Expiry intrinsic settlement at a single spot, all legs same underlying/expiry; includes modeled opening charges only",
        "geometry":g,"stress_grid":payoff,
        "observed_options_chain":False,
        "margin_requirement":"NOT_COMPUTED_BROKER_AND_EXCHANGE_DEPENDENT",
        "exercise_and_expiry_stt":"NOT_MODELED; exercise STT on long ITM options, settlement, assignment and compulsory liquidation can change actual losses",
        "exit_slippage_liquidity":"NOT_MODELED; multi-leg fills, bid-ask spreads, brokerage and taxes on exits can alter P&L",
        "physical_delivery":"NOT_MODELED; stock options can trigger physical-settlement obligations",
        "rates_used":rates,"tariff_references":RATE_REFERENCES,
        "data_quality":spec.get("data_quality","USER_SUPPLIED_UNVERIFIED"),
        "trading_authority":False,"research_only":True
    }
    sigma=spec.get("annualized_volatility")
    if sigma is not None:
        sigma=_number(sigma,"annualized_volatility",0,3)
        r=_number(spec.get("annual_risk_free",0.06),"annual_risk_free",-0.1,0.3)
        n=_integer(spec.get("paths",10000),"paths",100,1000000)
        seed=_integer(spec.get("seed",42),"seed",0,2147483647)
        years=(expiry-valued).days/365.0
        dividend=_number(spec.get("annual_dividend_yield",0.0),"annual_dividend_yield",0,0.3)
        curve["illustrative_greeks"]=_greeks(spot,positions,sigma=sigma,risk_free=r,dividend_yield=dividend,years=years)
        rng=random.Random(seed)
        dr=(r-0.5*sigma*sigma)*years
        volatility=sigma*math.sqrt(years)
        pnl=sorted(_payoff(spot*math.exp(dr+volatility*rng.gauss(0,1)),
                           positions,credit,fee) for _ in range(n))
        def q(x):
            z=x*(n-1);j=int(z);return pnl[j]*(1-(z-j))+pnl[min(j+1,n-1)]*(z-j)
        left=[x for x in pnl if x<=q(0.05)]
        # Uncertainty is from finite Monte Carlo draws conditional on the assumed
        # terminal distribution, NOT model risk, fee uncertainty or real-world alpha.
        positive=sum(x>0 for x in pnl)
        phat=positive/n
        z=1.96
        denom=1+z*z/n
        centre=(phat+z*z/(2*n))/denom
        half=(z/denom)*math.sqrt(phat*(1-phat)/n+z*z/(4*n*n))
        sample_mean=mean(pnl)
        sample_std=math.sqrt(sum((x-sample_mean)**2 for x in pnl)/(n-1))
        sampling_mean_half=z*sample_std/math.sqrt(n)
        curve["scenario_simulation"]={
            "model":"Single terminal lognormal underlying price; user-supplied annualized volatility, NOT option IV surface",
            "paths":n,"seed":seed,"volatility_user_supplied":sigma,"annual_risk_free":r,
            "horizon_calendar_days":(expiry-valued).days,
            "mean_model_pnl_inr":round(sample_mean,2),"probability_positive_model_pnl":phat,
            "monte_carlo_sampling_only_95pct_interval":{
                "positive_pnl_frequency_wilson":[round(max(0,centre-half),6),round(min(1,centre+half),6)],
                "mean_model_pnl_inr_normal_approx":[round(sample_mean-sampling_mean_half,2),round(sample_mean+sampling_mean_half,2)],
                "does_not_account_for_model_misspecification":True
            },
            "p05_model_pnl_inr":round(q(.05),2),"p50_model_pnl_inr":round(q(.5),2),
            "p95_model_pnl_inr":round(q(.95),2),
            "expected_shortfall_worst5pct_pnl_inr":round(mean(left),2),
            "calibrated_probability_of_profit":False,
            "warnings":["Returns and payoff distribution are model-dependent, not broker quotes or calibrated odds",
                        "No path-dependent events, skew, bid-ask, commissions on exits, exercise STT, margin, liquidity or early assignment",
                        "Gross max-loss geometry does not guarantee the actual post-tax loss limit"]
        }
    return curve
