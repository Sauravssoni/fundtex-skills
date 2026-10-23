# FundTex Motion Intelligence v0.8 — verified prototype and first-run broker guide
**Audited 23 October 2026.** This is a research-film and command-line skill feature branch, not a deployed trading service.

## Actual deliverable and proof

The connected authorized Mac contains a genuine generated local research film, **not synthetic frames pretending to be exchange-live**:

- Video: `/tmp/fundtex-infy-financial-film-20261023/analysis.mp4`
- Storyboard: `/tmp/fundtex-infy-financial-film-20261023/storyboard.json`
- Narration draft: `/tmp/fundtex-infy-financial-film-20261023/narration.txt`
- Source: previously fetched **unofficial** Yahoo unadjusted INFY.NS 2y historical OHLC, reimported through an analyst-pack CSV. The film conservatively labels source `UNVERIFIED INPUT — SOURCE: USER CSV`. Actual data-vendor and corporate-action adjustment provenance must be revalidated independently; the reference screenshot is not a source of historical prices.
- Source file SHA-256 embedded in manifest: `5b829f5823ec40936405286c79021ead28f94e421c5302ac83549affff9e5764`.
- Completed 10.0-second video, 960 × 540 H.264, 12 frames/s = 120 frames, 63,578 bytes. An independent FFmpeg full-file decode produced **exit status 0**. No audio is embedded, and no audio/voice/film renderer is secretly installed.
- Original optional `huashu-motion` open-source editing pipeline was **not executed**. It is explicitly an optional finishing tool.
- Full Python suite: **171 executed tests, 0 failures, 4 optional skips** under isolated HOME/PYTHONPATH. The FFmpeg+Pillow test skipped in the stripped environment because Pillow isn't available there; a direct smoke render with real default Python and FFmpeg succeeded on the same Mac.

## One-request agent-native UX

A new user in a genuinely permissioned terminal host asks:

> "Analyze INFY for the last year, validate its sources, show the bullish and bearish technical interpretation, and create a clean cinematic chart explainer video. Don't trade."

The agent validates the exact instrument and source, uses approved read-only market data or an explicitly labelled unofficial public historical fallback, creates an approved input file, then runs `fundtex film` with a **new** output path and inspects its MP4, JSON storyboard and text narration. User does not manually assemble JSON/CLI commands. If video engine deps are unavailable, it returns an actual storyboard rather than claiming an MP4 exists. Optional screenshot `--reference-chart` only supplies a checksum and intended aesthetics; the engine does NOT OCR the screenshot, inspect accounts, or treat image coordinates as prices.

Commands for a tester:

```bash
# Only within an explicitly authorized research folder with a dated input CSV
fundtex film --csv /approved/history.csv --symbol INFY.NS --out /approved/new-film --seconds 10 --fps 12
fundtex film --csv /approved/history.csv --symbol INFY.NS --out /approved/new-story --storyboard-only
fundtex updates                   # no network; offline availability report
fundtex updates --check --ref main # one explicit GitHub read-only ancestry check; never install
fundtex doctor                    # local dependency and installer readiness check
```

## Huashu upstream motion style — licensing and optional installation

Upstream: `alchaincyf/huashu-motion` (https://github.com/alchaincyf/huashu-motion). This independent MIT codebase provides a JavaScript/GSAP/Chrome film editor and optional sounds. The bundled GSAP uses its own no-charge standard licence, its fonts are individually licensed, and a bundled cartoon likeness is NOT commercially reusable. `node >=22`, an approved Chromium host and FFmpeg are prerequisites. To use it, a person explicitly approves the source and installation, and an authorized agent reviews a pinned revision and the third-party notice, installs the complete runtime and only then calls `om doctor`. The FundTex first-party standalone renderer works without any of this.

## Safe update recognition

The `install.sh` default now records a recognized *git checkout* source commit at `~/.local/share/fundtex-intelligence/.installed_source_commit` (only when it can determine an exact SHA), with backup-first behavior for an explicit `--upgrade`. The `fundtex updates` CLI stays offline by default; `--check` performs at most an explicit ancestry check against the chosen GitHub branch and classifies:
- source marker not available -> `INSTALLED_SOURCE_UNKNOWN`
- exact source SHA match -> `UP_TO_DATE_FOR_SELECTED_REF`
- trusted remote branch ahead -> `UPDATE_AVAILABLE_FOR_SELECTED_REF`
- installed ahead or sources diverged -> non-upgrade advisory
- authentication/network errors -> `UPDATE_CHECK_FAILED_CLOSED`

It does **not** execute or download remote code, install revisions, modify private skill folders or automatically query GitHub on every analysis. Coding agents may proactively offer the user one approval to check updates. No unattended update promises.

## Broker sign-in: account-holder-first, no secrets in chat

**Which account already exists?** This is the only essential routing detail.

**Zerodha account, easiest Claude/MCP path:** Visit https://zerodha.com/products/mcp/ and choose the supported AI client. For Claude Desktop, official support instructions at https://support.zerodha.com/category/trading-and-markets/general-kite/others-kite/articles/connect-zerodha-ai-assistant describe configuring the remote MCP server `https://mcp.kite.trade/mcp` with a trusted client and signing into Kite yourself through Zerodha. Grant read-only consent and verify the real tools/quote with the client. Merely enabling Kite MCP in Claude does not automatically install it into ChatGPT or wire it into the local Python process.

**Dhan account, best fit for current native CLI options-chain adapter:** Visit https://web.dhan.co/ and sign in. Open *My Profile → Get Trading & Data APIs*, generate the appropriate access token and review Data APIs entitlement. The provider presently states a ₹499+tax monthly auto-renewing data subscription; **do not activate it without user approval**. Store the broker client ID and token only with your local OS secret manager or restricted execution environment; never in chat or GitHub. The CLI can read the genuinely user-approved `POST /v2/optionchain` for the exact verified `UnderlyingScrip`, `UnderlyingSeg`, expiry and lot size. It must never access order placement endpoints. Token expiry and broker data licensing apply.

**FYERS/Kite Connect:** other official approved adapters may support read-only price quotes, but current option-chain file schema is Dhan-specific. Never pass arbitrary FYERS option-chain payloads into the Dhan normalizer.

## Known release limits

No 1-click live broker connection was executed in this audit: no account-holder credentials or real quote entitlements are configured. No financial return prediction or price forecast was validated by the motion test. No audio/music, multi-track movie editing, dynamic option-chain filmmaking, risk alert notifications or auto-install updater are included. A research film is not a trading strategy backtest. Correct exchange time, exact current lot sizes, complete Indian transaction charges, corporate action adjustments, settlement/assignment rules and lawful market-data redistribution remain separate gates.

**Production `main` unchanged. Keep feature PR draft until authorized real broker QA, browser visual QA and licensing checks are finished.**
