---
name: fundtex-motion-intelligence
description: Make narrated, source-linked Indian stock and options research videos from a verified current data series and optional screenshot as a visual STYLE reference. Animate real price candles, moving averages, dated events, bear/bull and negative findings, and use huashu-motion only with explicit permission and correct licensing.
---
# FundTex Motion Intelligence | Financial Films from Evidence

When the user says "analyze this chart and make a video", route to this skill **without asking the user to learn CLI commands**. Identify the security using verified exchange metadata; retrieve an authorized dated broker historical feed or public-history fallback, disclose source age/adjustments and only then script the film. A screenshot is a **visual style reference**, not an authoritative numeric data series. Never infer precise candles, forecast probabilities or option prices from pixels. If no trustworthy source/permission, prepare a titled concept only, not a fake market analysis.

## First-party source-driven film engine

A genuinely terminal-enabled host can run:

`fundtex film --csv /approved/price-history.csv --symbol INFY.NS --out /approved/new-film --reference-chart /approved/reference-chart.png`

The agent obtains/validates the CSV and chooses a **new approved** output directory. The result contains editable `storyboard.json`, `narration.txt` and **actual rendered** `analysis.mp4` when Pillow and FFmpeg are available; otherwise it must offer `--storyboard-only` and be explicit that no MP4 exists. Use `--seconds 12 --fps 12` for simple desk briefings. The source hash and last observation must be on-screen. Show the equity source's `SYNTHETIC_FIXTURE` or `USER_SUPPLIED_UNVERIFIED` classification prominently and never claim exchange-live. Historical crossovers/RSI/SMA are *retrospective descriptive indicators*, not predictive trading signals.

A suitable default video story: 00:00 security/source/date title, next chart reveal from actual OHLC, then SMA20/SMA50/RSI context, what invalidates a bullish or bearish view, and an explicit no-proven-alpha decision footer. Do not overlay dates/prices from an image instead of the CSV. Subtitles/narration must match computed numbers and disclose alternatives and uncertainty. Optional music/voice is consent-based: do not copy or invent an actor's real voice or silently fetch models/assets.

## Optional upstream motion finishing: huashu-motion

The actual open-source project shown in the user's reference is https://github.com/alchaincyf/huashu-motion by alchaincyf, **not authored by FundTex**. It ships the agent skill, `om` CLI, templates, runtime, and a browser-based frame editor. Per upstream README it requires Node 22+, Chrome/Chromium and FFmpeg; its MIT-licensed code includes assets/dependencies with **separate third-party terms**. Merely copying `SKILL.md` does not install the complete renderer.

Only **after explicit install permission and source/security/license review**, the agent may add the complete upstream skill using its supported installer (`npx skills add alchaincyf/huashu-motion`) or a pinned audited checkout, then run `om doctor` before using the full editor. Never automatically execute `npx`, clone running scripts, fetch music samples, upload private broker data, or install optional voices. Render the source-backed FundTex storyboard as an approved motion spec in huashu's compatible composition rather than substituting generated financial figures. Do not present third-party templates/fonts/audio as blanket MIT-cleared assets. Agent must verify actual installed host tools and output video in a compatible player.

## Current signals and broker onboarding

Use `fundtex broker-status` and authorized read-only data connectors if truly available; route a user to official Zerodha Kite MCP login or DhanHQ individual API setup in the broker's own UI, with one step at a time. If no broker exists, proceed with dated public history, not a fictional "current" signal. Avoid broker order/GTT/pledge/fund APIs. Video generation must not introduce new trading authority. A signal report requires independently reconciled chain data and risks, not just attractive animation.

## Agent-safe update discovery

At first authorized CLI use, optionally run `fundtex updates --check` (one GitHub HTTPS read, consent to network required). It reports commit ancestry, not merely a different source SHA. **Never auto-install** new versions or quietly overwrite a customized skill; `bash install.sh --upgrade` is an explicitly approved reviewed-checkout operation with backup. If network disabled, continue with local skills and show that update status is unverified.

Video outputs are for research/education, not SEBI-registered advice, professional forecasts or trading instructions. Even a beautiful film must faithfully show adverse cases and missing evidence.

## Broker-led videos

After approved local MCP setup and the broker-hosted login, ask for the read-only quote/historical-data tools in the host. The agent may use an authorized source for dated chart films only after validating schema, source, instrument, timestamps and data-use terms; the screenshot remains **visual style only**, never numeric evidence. Never claim a market feed is connected solely because the local MCP server appears. If the host does not expose Kite data, use dated public OHLC with an accurate provenance label and create the research film without blocking the user.
