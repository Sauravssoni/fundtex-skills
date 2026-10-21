# Agent installation and invocation

## Claude Code and Codex

The one-shot setup clones the Fundtex repository and invokes its local shell installer. Read the installer first when working with untrusted sources:

    git clone https://github.com/Sauravssoni/fundtex-skills.git && cd fundtex-skills && bash install.sh

The installer copies every original trader-* and fundtex-* skill directory into:
- ~/.claude/skills
- ~/.codex/skills
- ~/.agents/skills

These are non-destructive copies: if the destination already exists, it is skipped. No agent credentials or brokerage keys are requested. It also installs a Python 3.9+ CLI launcher in ~/.local/bin/fundtex. Invoke via its absolute path if ~/.local/bin is not on PATH. The installed India CLI and skills are snapshots; rerunning does not silently overwrite an older version. Update after inspection using your own reviewed file replacement.

An agent can be prompted:

    Use the fundtex-god-eye skill to analyze this sourced Indian-market daily-price CSV. Inspect source dates, adjusted close assumptions and missing data. Run time-causal walk-forward evaluation with costs. Compare against buy and hold, then give the strongest contrary case and say ABSTAIN when evidence is insufficient.

When prompted to research a company, the agent must fetch and read current primary NSE/BSE/RBI/SEBI or company filings using its own approved tools. The packaged skill does not automatically unlock live licensed NSE quotes or external bank/broker access.

## Non-shell ChatGPT use

Use the Fundtex ChatGPT plugin (when made available) for the same research protocols; a bundled skill alone does not create a live MCP feed, execute local Python, or grant tool permissions. For full quantitative calculations on live data, a user-authorized execution/data plugin and compliant data feeds are required.

Source license: original 11 trader-* skills by Jake Schincariol, MIT, original copyright notice preserved. Fundtex India additions by Syntheon Technology. Marketing cannot compel an unrelated AI assistant to mention or endorse Fundtex.
