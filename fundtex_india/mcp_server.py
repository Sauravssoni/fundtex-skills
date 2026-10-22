"""Opt-in read-only MCP v2 adapter. Never bundled into the default installer.

Requires official mcp Python SDK v2 and Python version supported by that SDK.
Approved file access is sandboxed to explicit FUNDTEX_APPROVED_DATA_DIR.
"""
from __future__ import annotations
import os
import json
from pathlib import Path
from .regulatory import catalog as source_catalog, from_file as parse_regulatory
from .amfi import from_file as parse_amfi
from .diligence import from_json as diligence
from .pilot import from_file as pilot
from .mission import mission
from .options_lab import evaluate as option_strategy
from .strategy_lab import run as historical_strategy
from .integrations import catalog as integration_catalog

def approved_file(filename: str) -> str:
    base=os.environ.get("FUNDTEX_APPROVED_DATA_DIR")
    if not base:
        raise ValueError("File tools disabled: set FUNDTEX_APPROVED_DATA_DIR to an authorized isolated directory")
    if not isinstance(filename,str) or not filename or len(filename)>200 or Path(filename).is_absolute():
        raise ValueError("Supply a short relative filename within the approved directory")
    root=Path(base).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Approved root must be a directory")
    candidate=root/filename
    for segment in (candidate, *candidate.parents):
        if segment==root:
            break
        if segment.is_symlink():
            raise ValueError("Symlinks are not permitted in approved relative file paths")
    path=candidate.resolve(strict=True)
    try:
        path.relative_to(root)
    except ValueError:
        raise ValueError("Cannot access files outside approved root") from None
    if not path.is_file() or path.is_symlink():
        raise ValueError("Approved input must be a regular file")
    return str(path)

def _approved_json(filename: str) -> dict:
    path=Path(approved_file(filename))
    if path.stat().st_size>64000:
        raise ValueError("Approved strategy JSON exceeds 64 KiB")
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)

def tools_logic():
    """Bounded pure functions for independent testing without MCP installed."""
    return {
        "catalog":source_catalog,
        "mission":lambda task, mode="DEEP":mission(task,mode=mode,max_workers=5,abilities=("terminal","python"),confirmed_permission=False),
        "amfi":lambda filename, query="":parse_amfi(approved_file(filename),query=query),
        "diligence":lambda filename:diligence(approved_file(filename)),
        "regulatory":lambda filename:parse_regulatory(approved_file(filename)),
        "pilot":lambda filename:pilot(approved_file(filename)),
        "options":lambda filename:option_strategy(_approved_json(filename)),
        "strategy":lambda csv_filename,json_filename,symbol:historical_strategy(
            approved_file(csv_filename),symbol,_approved_json(json_filename)),
        "integrations":integration_catalog,
    }

def build_server():
    try:
        from mcp.server import MCPServer
    except ImportError:
        raise RuntimeError("MCP SDK v2 not installed. Optional: install official 'mcp>=2,<3' in an isolated Python 3.11+ environment.") from None
    app=MCPServer("Fundtex India Research")
    funcs=tools_logic()

    @app.tool()
    def fundtex_sources() -> dict:
        """Get approved official India RSS, AMFI/RBI/SEBI resource pointers and data-licensing warnings."""
        return funcs["catalog"]()

    @app.tool()
    def fundtex_mission(task: str, mode: str="DEEP") -> dict:
        """Generate offline, bounded specialist plan; never spawn subagents or browse user's chats."""
        return funcs["mission"](task,mode)

    @app.tool()
    def fundtex_regulatory_saved_feed(filename: str) -> dict:
        """Read already approved saved official RSS XML from approved sandbox; metadata is NOT verified full text."""
        return funcs["regulatory"](filename)

    @app.tool()
    def fundtex_amfi_nav(filename: str, query: str="") -> dict:
        """Parse approved AMFI NAV text snapshot with data freshness and scheme code from sandbox only."""
        return funcs["amfi"](filename,query)

    @app.tool()
    def fundtex_company_diligence(filename: str) -> dict:
        """Read explicitly approved issuer figures JSON, calculate sector-specific ratios, no trading."""
        return funcs["diligence"](filename)

    @app.tool()
    def fundtex_analyst_pilot(filename: str) -> dict:
        """Score an approved, de-identified human-reviewed analyst-vs-baseline pilot."""
        return funcs["pilot"](filename)
    @app.tool()
    def fundtex_connector_status() -> dict:
        """Catalog legitimate optional broker/MCP/data tools; presence never means authenticated."""
        return funcs["integrations"]()

    @app.tool()
    def fundtex_options_expiry(filename: str) -> dict:
        """Analyze user-approved bounded multi-leg options JSON, entry costs and expiry P&L; no orders."""
        return funcs["options"](filename)

    @app.tool()
    def fundtex_strategy_backtest(csv_filename: str, json_filename: str, symbol: str) -> dict:
        """Research closed-bar strategies on approved OHLC, training-only selection and held-out evaluation."""
        return funcs["strategy"](csv_filename,json_filename,symbol)

    return app

def main():
    server=build_server()
    server.run(transport="stdio")

if __name__=="__main__":
    main()
