# India Financial Source Connectors — explicit consent & provenance

Fundtex is a source-aware analyst toolkit, NOT a licensed exchange terminal. No proxying around exchange rules, no broker integration, no client-data redistribution.

## Usable sources

| Provider | Integration | Rights and limitations |
|---|---|---|
| SEBI | Official RSS, read-only feed discovery: fundtex regulatory --feed sebi | Metadata is not actual verified circular/order. Open original linked document. |
| RBI | Releases/notifications RSS: fundtex regulatory --feed rbi-releases or --feed rbi-notifications | Headlines are only source leads; verify original publication and effective dates. |
| AMFI | User-provided official-format daily NAV snapshot: fundtex amfi --file /approved/NAVAll.txt --query "fund name" | End-of-day scheme/plan/option NAV; supports 2026 8-column and old 6-column formats; verify stale scheme dates, source identity and usage rights. |
| NSE/BSE | SEBI official corporate-filings directory: https://www.sebi.gov.in/curation/corporate_filings.html | No unapproved automated scraping or free republishing of licensed market/company datasets; secure agreements for commercial feeds. |
| data.gov.in | Registration + user-approved government open dataset/API | Obtain own API key when necessary; obey source-specific terms and release dates. |
| RBI DBIE | Approved download/export | Verify provenance/revisions/units; no claim that unofficial mirrors are official. |

Official policy references:
https://www.sebi.gov.in/rss.html
https://www.rbi.org.in/Scripts/rss.aspx
https://www.amfiindia.com/net-asset-value
https://data.gov.in/help
https://www.nseindia.com/static/market-data/nse-data-policy

## Important technical contracts

The RSS reader uses only approved HTTPS feed URLs, same-host HTTPS redirects, eight-second network timeout, one-MB limit and safe XML parsing. Every item receives metadata-only NOT-VERIFIED status and a SHA-256 receipt; an agent must open the actual linked original for verification. The AMFI importer is offline only, six-MB maximum, validates positive finite scheme NAV and per-scheme date, and returns age/staleness warnings without claiming real-time quotes.

Commands:
    fundtex sources
    fundtex regulatory --feed sebi --max-items 10
    fundtex regulatory --feed rbi-releases --max-items 10
    fundtex regulatory --file /approved/source.xml
    fundtex amfi --file /approved/NAVAll.txt --query "Direct Plan" --as-of 2026-10-21

The included sample XML/NAV datasets are deliberately FICTIONAL. No real issuer document, NAV file or confidential portfolio is included in the repo.

## Optional MCP connector

An opt-in read-only MCP server is available in fundtex_india/mcp_server.py. Uses the official MCP Python SDK v2 (optional external dependency; NOT installed automatically). In an isolated supported Python >=3.11 environment install mcp>=2,<3 after inspection, then run module with standard input/output transport. The server exposes official source catalog, bounded agent planning, approved saved RSS, approved AMFI NAV, issuer diligence and analyst-pilot scoring.

For any file-reading tool, FUNDTEX_APPROVED_DATA_DIR MUST point to an explicitly authorized sandbox. If missing, file access is denied. Inputs must be relative paths inside that directory; traversal, absolute paths, symlinks and nonfiles are rejected. The server exposes no live order, unsanctioned internet access, or unrestricted local file access.

Illustrative host MCP config (replace all paths with actual approved paths):
{
  "mcpServers": {
    "fundtex-local": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "fundtex_india.mcp_server"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/fundtex-skills",
        "FUNDTEX_APPROVED_DATA_DIR": "/approved/deidentified-finance-inputs"
      }
    }
  }
}

The MCP SDK v2 host handshake and individual agent integration require verification in the actual authorized client; ordinary installer tests do not certify them. Documentation: https://github.com/modelcontextprotocol/python-sdk .
