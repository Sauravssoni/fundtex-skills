# FundTex E2E Release Evidence — 2026-10-23

## Proof from the connected development Mac

**Full source regression:** `python3 -m unittest discover -s tests -t . -p 'test_fundtex*.py'` completed **201 tests with 0 failures and 4 optional skips** on the prior Kronos head. This feature branch adds standalone acceptance regression tests and installer staging collision protection; rerun count must be recorded separately.

**Actual 7-stage synthetic end-to-end run:** the new `fundtex acceptance --out NEW_FOLDER --million-paths --render-video` succeeded, exit 0. All output artifacts were generated locally under `/tmp/fundtex-acceptance-real-render-20261023`:
- 370 clearly labelled **SYNTHETIC_FIXTURE** OHLC rows, SHA256 `4606df31318c03b1b5132c94cc7790e322f749bcde98e053f0812927e7c3f529`.
- Source-linked SVG chart (`chart.svg`, 72,760 bytes).
- Three rule candidates evaluated with train-only selection, untouched chronological holdout, 2x/4x cost stress and negative result: `NO_OBSERVED_NET_EXCESS`.
- 60 real numerical *baseline* forecast comparisons (Kronos weights **not run** in this acceptance fixture), 12 horizon windows, separate placebo and paper-cost analysis, zero trades.
- Defined-risk synthetic NIFTY put vertical with user-supplied **75-unit lot NOT verified as an active exchange contract**, `1,000,000` sampled terminal lognormal paths and modeled intrinsic-only max loss `₹10,571.85`. No current option chain, bid/ask, actual broker margins, exercise STT, liquidity or physical settlement constraints.
- Actual 6-second / 36-frame MP4 through Pillow+FFmpeg, storyboard and narration with synthetic disclaimer. Video is research-only, not exchange-live.
- All seven components pass cross-engine original-source SHA agreement. New output receipts also include SHA-256 hashes of every artifact, fail closed on existing output destinations and show a separate `README.txt` warning.

**Private website verify:** on latest private `feature/fundtex-plugin-v011-e2e-hardening-20261023` branch, `npm run verify` completed with exit 0. All lint, strategy/security/market-data, 21 Kite gateway contracts, 4 private plugin release contracts, production vinext build and 3 rendered HTML contracts passed. Plugin source v0.11 deliberately removes automatic registration of the unrestricted official Kite MCP; 22 skill manifests and logo/brand verified. **Existing installed personal ChatGPT plugin remains v0.9 until separately validated release upload.**

## Operator one-command test

```sh
fundtex acceptance --out /an/approved/NEW-acceptance-folder
fundtex acceptance --out /an/approved/NEW-stress-folder --million-paths --render-video
```

The program requires a fresh destination, performs no network access or broker authentication, never executes orders, and returns JSON containing `PASS_OFFLINE_SYNTHETIC_COMPONENTS_ONLY`. A PASS is **not** `PRODUCTION_READY`: it explicitly sets `real_market_data_verified=false`, `broker_session_authenticated=false`, `broker_gateway_production_ready=false`, `real_kronos_model_executed=false`, `derivatives_chain_verified=false`, `real_orders_executed=0`. The release decision is `BLOCKED_UNTIL_LIVE_BROKER_AUTH_OAUTH_AND_LICENSE_GATES`.

### Separately verified Kronos — do not conflate

Real official Kronos-mini safetensors did run offline on the Mac using pinned source and Apple Metal. On **60** historical, non-independent/unknown-pretraining-membership INFY.NS future closes, Kronos MAE **₹39.12**, persistence baseline **₹35.45**, drift **₹40.01**: Kronos underperformed persistence by about **10.3%** in this test. This is a negative finding and should remain prominently visible. Any agent claiming `Kronos-alpha verified` based on this would fail the evaluation contract.

### Production and live integration blockers

1. The real account holder successfully authorized Zerodha on the broker's official page; direct hosted MCP `get_ltp` and `get_ohlc` then failed with **Please log in first**. No broker-authenticated quote has been verified. Upstream has a reported MCP session-binding issue.
2. FundTex's separate gateway model passed mocked HTTP identity/session/zero-order tests but has **no commissioned trusted OAuth provider, HTTPS deployment, JWKS lifecycle, revocation end-to-end test, actual user-isolated live Kite quote or licensed feed entitlement**. Don't claim one-click connection for ChatGPT web yet.
3. A session-stable gateway must expose only research tools, not order/GTT APIs. User test accounts with ₹0 balance still require proper security scope.
4. The production website and installed personal plugin were not modified by this acceptance run. Dev/test PRs remain drafts until independent release authorization.
5. Separate licensed option-chain snapshots, correct Indian contract lot sizes, actual historical bid/ask and settlement/STT are required before an options strategy can be scored as executable.
6. No result is a guarantee, registered adviser recommendation, brokerage margin commitment or profitable trading proof.

## Governance

Retain separate results for (a) synthetically validated numerics, (b) official model inference, (c) authenticated and licensed data connectivity, (d) hosted browser UI and OAuth, and (e) production security. Never roll these into one misleading overall "all green" status. Preserve losses, rejected models, gaps, test skips and failed live validations alongside successes.
