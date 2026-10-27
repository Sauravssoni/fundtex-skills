# FundTex Fusion Desk — Unified Research Integration (28 October 2026)

**Status: Tested research feature branch, NOT broker-integrated production.** The point of this feature is ONE agent-native research flow—not three separate user apps.

## Sources audited

| Reference | Source | Licensing / product use |
|---|---|---|
| Day Trader skills | https://github.com/Jakeschincariol/day-trader-skill | MIT, copyright 2026 Jake Schincariol; existing 11 US-market methods are separately attributed. This branch implements an independent India 5m research/time-machine method, without copying code or broker order execution. |
| Fincept Terminal | https://github.com/Fincept-Corporation/FinceptTerminal | Public AGPL-3.0 code and repository's additional asserted commercial restrictions. **Do not copy, fork into private SaaS, imitate branding or invoke proprietary Fincept APIs without commercial permissions.** Original FundTex UI/engine only. |
| World Monitor | https://github.com/koala73/worldmonitor | AGPL-3.0 standalone platform; use official hosted service https://worldmonitor.app/mcp through user authorization and provider terms instead of copying its source. `tools/list` is public, most data `tools/call` require subscription entitlement/OAuth. |
| Kronos | https://github.com/shiyu-coder/Kronos | MIT separately attributed optional offline challenger. Historical benchmark on INFY failed price-error baseline in larger sample; must remain opt-in. |
| Kite | https://mcp.kite.trade/mcp | User's broker login succeeded, but direct ChatGPT MCP failed authenticated session binding. FundTex's private session-stable read-only gateway remains NOT deployed or authenticated. |

## Integration graph

```text
Natural language in ChatGPT / Codex / Claude / CLI
          |
  FundTex first-run + capability discovery
          |
   source verification ─── optional World Monitor OAuth MCP (global event context)
        |                 └─ NSE/BSE/RBI/SEBI/issuer primary citations
        └─ market data ── authorized read-only Kite gateway (not released)
          |
  Source-hashed evidence / timestamp / exact exchange instrument
          |
       FUSION DESK
    ┌───────────┬───────────────┬─────────────┬─────────────────┐
    God Eye     India 5m replay Kronos lab    Risk council
    forensic    paper 10k       optional      independent skeptic
    filings     bootstrap       baseline QA   & tail-risk
    └───────────┴───────────────┴─────────────┴─────────────────┘
                        |
      Source ledger + bull/bear/unknown + ABSTAIN if unsupported
                        |
    Nexus terminal local JSON viewer / report / historical motion film
```

**DO NOT mistake** source registration for OAuth login, source-pinned history for an exchange-signed feed, paper Monte Carlo for actual derivative option-chain historical trades, or a workflow plan for true parallel agent execution.

## Original new commands

```bash
# A short, reviewed, locally saved provider event subset (do not redistribute licensed feeds)
fundtex fusion-desk --events /approved/events.json --as-of 2026-10-28T03:30:00+05:30 --symbol INFY.NS

# Optional independent NSE/BSE 5m historical paper replay, no leverage or orders
fundtex daytrader-replay --csv /approved/observed_5m.csv --symbol INFY.NS \
    --capital-inr 100000 --max-loss-inr 1500 --friction-bps 16 --paths 10000

# Same source-hashed evidence plus a validated full-session paper replay in one desk response
fundtex fusion-desk --events /approved/events.json --intraday /approved/observed_5m.csv \
    --symbol INFY.NS --paths 10000
```

The current event JSON contract: a JSON list (<=300, <=2 MB) with `source` from a strict allowlist, `headline`, `category`, timezone-aware `published_at` and `observed_at`, optional `event_id`, HTTPS `source_url`, `regions`, `symbols`, and bounded `summary`. Missing provenance, future timestamps, embedded source-URL credentials, invalid sources and unknown account fields fail closed. SHA256 receipt is emitted; raw provider data is never automatically fetched by the command.

The 5m input needs `timestamp,symbol,open,high,low,close,volume` with actual timezone offsets, 75 continuous start-timestamp bars from 09:15 to 15:25 IST (09:15–15:30 session), and exact instrument identity. Replays a hypothetical **long-only 15-minute opening-range breakout** with a candle-close signal and next-candle-open fill; stop midpoint, target 1R, conservative stop when both touched within the same bar, end-of-session closure. Incomplete sessions are excluded, not backfilled.

For 10K bootstrap paths, data are resampled only from the empirically completed paper setups. This is *not* a calibrated future profit probability. Some friction inputs are illustrative and can't accurately model gap stops, brokerage exchange fees, slippage, liquidity, F&O margin or order execution. Max historical risk budget capped at 5% of hypothetical equity; 0 actual trades.

## Product/UI sync

The private FundTex website feature branch adds a local-only Nexus Fusion receipt viewer. A user can choose a finished JSON receipt in browser, view real event counts, provenance hash and historical replay diagnostics, and the JSON stays client-side. It does not falsely enable the private OAuth broker gateway, execute the CLI remotely, or import unrelated Fincept/World Monitor AGPL application code. The current web Fusion/Kronos panel continues existing own research logic.

## Launch gates and gaps

- [x] India-session replay and source schema implemented; adversarial synthetic tests added
- [x] God Eye Fusion structured risk/evidence output; client/CLI contracts staged
- [x] World Monitor public MCP `tools/list` returned **97 discoverable tools** on authorized paired Mac; all six desired research tools advertised
- [x] 3 new first-party skills; existing GOD EYE + Kronos + strategy/risk specialists retained
- [x] Private plugin draft registers optional World Monitor OAuth and disables previously unsafe direct Kite provider entry
- [ ] World Monitor user OAuth entitlement and live `get_world_brief` tool return **not tested**
- [ ] Real NSE intraday **full-session broker-sourced** data **not tested**; currently synthetic test fixtures only
- [ ] Cross-language Python report → real browser file picker visual QA pending; source build and static UI tests needed
- [ ] Private broker gateway Auth0 issuer and production HTTPS service **not deployed**
- [ ] Licensed live index-options data including bid/ask, fee/slippage/margin/exchange adjustments absent
- [ ] Market prediction calibrated out-of-time on unseen India data **not established**
- [ ] Actual exchange order execution is excluded by design

Do not make a production merge or plugin release until all relevant tests pass and a reviewer accepts the separate broker compliance/privacy/licence gates.
