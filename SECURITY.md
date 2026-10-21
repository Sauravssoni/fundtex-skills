# Security and Responsible Use

Fundtex Financial Intelligence is open-source, read-only research software — not a trading, custodial, financial-data licensing or professional advice service. The India engine has no broker credentials or order-execution pathway. The original MIT-licensed upstream trader-broker component remains US-oriented and should not be connected to live Indian trading without separate review.

## Data privacy and consent

- Never upload employer client portfolios, research notes, account IDs, deal information, secrets or proprietary pricing to a remote AI agent without explicit firm authorization.
- The Fundtex onboarding/doctor commands do not access personal chats, connected apps, browser history, financial accounts or local customer files. Context-aware suggestions use only a short voluntarily provided description.
- Optional Claude/Codex subagents must respect the host's permissions, budgets and data classification. Never share sensitive data among extra workers by default.
- Public issue reports should contain fabricated examples or redacted data, never real portfolio holdings or user-specific credentials.

## Data and supply-chain safeguards

- Only use licensed or otherwise permitted NSE/BSE, issuer, RBI/SEBI and broker source material.
- Verify exact origin and SHA-256 of all imported files. An NSE UDiFF-format ZIP import checks structure but cannot authenticate the publisher or adjust dividends/splits.
- Git clone/binary installs should be inspected before running. No installer will knowingly overwrite an existing skill or engine; upgrades require deliberate user review.
- Rate-limited quote adapters must fail closed, never fill missing live prices with generated values.

## Vulnerability reporting

Please avoid publishing exploitable vulnerabilities or sensitive details in public issues before triage. Contact the repository maintainer via a private GitHub security advisory where available, or use the repository owner's private contact channel. Include affected version, minimal reproducible safe example, expected/actual behavior and recommended mitigations.

## Limits

Passing unit tests, Monte Carlo simulation or archived-data research checks does NOT validate regulated investment advice, predictive alpha, data protection compliance, system resilience or exchange-data redistribution permissions. Separate SEBI/Indian-law review and institutional security controls are required before client-facing services.
