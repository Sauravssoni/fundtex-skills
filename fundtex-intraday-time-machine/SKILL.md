---
name: fundtex-intraday-time-machine
description: Conservative India-specific five-minute opening-range setup scanner, risk/exit planner and reproducible 10k historical paper outcome replay with complete-session data checks. No live orders.
---
# FundTex India Intraday Time Machine

Inspired by generic scanner → entry → exit → paper replay → risk budget workflows, including Jake Schincariol's MIT day-trader-skill (https://github.com/Jakeschincariol/day-trader-skill). This is **independent Indian-market code**, not an American NYSE/PDT copy.

The host automatically obtains an approved, genuine NSE/BSE 5-minute OHLCV file when authorized. Require ISO timestamps with actual timezone offsets and complete **09:15–15:30 IST sessions (75 bars)**. Missing, partial, off-grid or different-symbol sessions are excluded, not silently interpolated. Input to `fundtex daytrader-replay --csv /approved/5m.csv --symbol INFY.NS --capital-inr 100000 --max-loss-inr 1500 --friction-bps 16 --paths 10000`. Costs are **hypothetical** bps (not provider fee validation).

V1 study is long-only 15m opening-range breakout, signal on completed candle, hypothetical entry **next bar open**, stop midpoint of opening range, target 1R, worst-case stop if target/stop both occur inside the same OHLC candle, exit at end of session. Reject >5% paper-equity risk budget; cap position by cash (no leverage, naked shorts or option lots). Bootstrap resamples already observed session trade outcomes; it is **not** a forecast of unknown future shock regimes. Flag gap-through-stop and corporate action/delivery omission.

The agent can summarize setups, propose alternate predefined research rules for a future revision, and produce educational after-action videos. It must not invent 1-minute/tick data or send orders. For actual options strategies, route to hedged-options with real full instrument/expiry lot rules, actual bid/ask and licensed chain history. No guarantee an observed setup can be executed.

The existing user's portfolio and Zerodha Kite credentials are not needed. Only automatically offer broker login if an expressly user-authorized read-only source exists and the connection is genuinely verified with a quote. Keep user data private and don't claim live paper trading from an offline 5m backtest.