# FundTex Motion Intelligence and Safe Update Discovery
**23 October 2026. Experimental release branch; research only.**

## What a new user experiences

User: "Analyze my current NIFTY or Infosys chart, challenge the obvious technical signal, and make me a 10-second premium video. Check for FundTex improvements before doing the work."

A compatible Claude Code, Codex or other coding agent with installed FundTex skills must:
1. Confirm actual terminal/file permissions and run **offline** `fundtex doctor`.
2. If the host explicitly allows the Internet, run `fundtex updates --check`. GitHub commit ancestry is read only; show whether the selected remote reference is truly ahead, behind, divergent or unknown. Never install from a remote address without separately reviewing and approving the checkout. The default `main` comparison may be older than a cutting-edge feature branch.
3. Discover any already-authorized read-only broker feed. **Do not force brokerage setup**. An unconnected user can proceed with dated public history (user understands unlicensed rights and no real-time guarantee); never invent prices when a source fails.
4. Identify the instrument and period, retrieve actual approved history with genuine OHLC when needed, inspect dates, quote provenance, corporate actions and indicator definitions. A screenshot is only a design-style reference, NOT a price source.
5. Create a cinematic yet conservative research film: time-aligned historical candles/line, SMA/RSI evidence, on-screen source/date/hash, explicitly adverse risks and concluding `NO VERIFIED TRADE SIGNAL`. No auto orders or market-maker expectations.
6. Verify the video can actually be opened/decoded. If optional dependencies are unavailable, deliver the editable storyboard and narration **without inventing an MP4**.

### Agent-side commands (the human doesn't memorize these)

```bash
fundtex doctor
fundtex updates --check                     # explicit network permission
fundtex research --symbol INFY.NS --period 2y --source public-ohlc --quote off --out /approved/new-pack
fundtex film --csv /approved/new-pack/price-history.csv --symbol INFY.NS --out /approved/new-film --seconds 10 --fps 12
fundtex film --csv /approved/price-history.csv --symbol INFY.NS --out /approved/new-storyboard --storyboard-only
```

The built-in first-party renderer requires **Pillow + FFmpeg** for MP4 and produces an H.264 yuv420p `analysis.mp4`, `storyboard.json` and `narration.txt`. Browser playback, sound, narration and cinematic finishing are separate optional features; no unauthorized voice synthesis or copyrighted tracks.

### Verified Mac smoke

Connected approved MacBook Pro (Python 3.11, macOS with Pillow and FFmpeg installed) created:
`/tmp/fundtex-infy-financial-film-20261023/analysis.mp4`, storyboard and narration from a previously retrieved 495-observation unofficial Yahoo unadjusted OHLC Infosys historical report, last dated 2026-10-21. FFmpeg decoder inspection confirmed **10.00 seconds, H.264, 960 × 540, 12 fps**. This is an **unverified historical-data demonstration**, not current guaranteed NSE streaming data. No music/voice, client account or specific live financial signal used. The Mac path is not a public download URL.

## Upstream huashu-motion (optional and properly attributed)

Project the user referenced: **alchaincyf/huashu-motion** (https://github.com/alchaincyf/huashu-motion). It is a separately maintained open-source agent skill/CLI/studio for code-rendered branded films. Upstream says Node.js >=22, local Chrome/Chromium and FFmpeg are required. Its source is MIT, but bundled GSAP, fonts, samples and other materials carry their own usage conditions.

The **FundTex skill points to upstream**, preserves its identity, and does not vendor/copy any third-party executable or fonts. A human must explicitly authorize installation of complete huashu-motion (not merely its SKILL.md), inspect source/dependencies and licensing, and run its `om doctor` before letting the agent create a finishing composition. Do not silently execute npx or send broker data to third-party services.

## Exact update-detection contract

`fundtex updates` by default returns `OFFLINE_NOT_CHECKED`; **zero network**. With `--check`, it reads only GitHub HTTPS commit/compare metadata from `Sauravssoni/fundtex-skills` and compares the selected branch to the commit recorded by the safe installer in `~/.local/share/fundtex-intelligence/.installed_source_commit`.

Statuses include `UP_TO_DATE_FOR_SELECTED_REF`, `UPDATE_AVAILABLE_FOR_SELECTED_REF`, `BRANCH_DIVERGED_REVIEW_REQUIRED`, `INSTALLED_NEWER_THAN_SELECTED_REF`, `INSTALLED_SOURCE_UNKNOWN` and `UPDATE_CHECK_FAILED_CLOSED`. A remote SHA is not enough: a positive update claim requires GitHub's descendant comparison. The engine never downloads remote code, executes shell scripts or overwrites customized skills. An approved checkout can later be installed with backup-first `bash install.sh --upgrade`.

## User-friendly broker onboarding

**Zerodha (first-time, lowest friction in supported Claude Desktop client).**
Open https://zerodha.com/products/mcp/ . In Claude Desktop select Settings → Developer → Edit Config. Add official Kite MCP host `https://mcp.kite.trade/mcp` via `npx mcp-remote` as documented by Zerodha (preserve any existing MCP server settings). Restart Claude, check its tool selector, authorize using the broker's **own** two-factor Kite login, and verify a read-only quote for an actual ticker. Kite MCP broker authorization is **not automatically shared** with FundTex's separate Python CLI REST token environment. Don't paste passwords or tokens in chat.

**DhanHQ (direct option chain for local FundTex research).**
Owner opens https://web.dhan.co and selects My Profile → Access DhanHQ APIs, checks data API entitlement, explicitly approves any subscription, generates an access token with approximately **24 hours** validity, and stores credentials locally using an approved OS secret manager. FundTex uses `FUNDTEX_DHAN_CLIENT_ID` and `FUNDTEX_DHAN_ACCESS_TOKEN` in a permitted private local host only. Ask agent to perform a **read-only** quote validation; option-chain capture requires an independently verified underlying security ID, segment, expiry and lot size. Source: https://dhanhq.co/docs/v2/authentication/ and https://dhanhq.co/docs/v2/option-chain/ . One unique option-chain request per three seconds; no undocumented retries.

For a multi-user public FundTex onboarding service, **individual manually generated tokens are not a scalable consent model**: the proper broker-approved partner/OAuth permission flow, privacy and market-data contracts must be separately designed and legally reviewed. This branch does NOT offer a live public aggregator or execution authority.

## Release readiness and limitations

Changes are staged in `feature/fundtex-chart-film-auto-updates-20261023`, stacked on read-only Dhan option-chain PR #5. The associated private v0.8 skill is staged in a separate review branch; **installed ChatGPT plugin version is still v0.7** unless Plugin Creator reports an authenticated successful update. No main branch deployment and no general access to user brokerage. The author's future training claims are strictly conditional on data/validation; a video alone cannot establish profitable strategy performance.
