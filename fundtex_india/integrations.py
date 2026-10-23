"""Fundtex connector discovery: transparent, no account linking or network calls.

A registry isn't a connected provider. Capability truth must come from an actual
host or broker tool call plus source entitlements and consent.
"""
from __future__ import annotations
import importlib.util
import os

CONNECTORS=(
    {"id":"fundtex-mcp","kind":"local","label":"Fundtex read-only analyst MCP",
     "endpoint":"stdio:python -m fundtex_india.mcp_server",
     "purpose":"Authorized private-file diligence, no-code strategy backtests, option payoff lab, regulatory metadata",
     "auth":"Explicit approved local directory + optional separate MCP v2 Python SDK",
     "actions":["read approved local input","deterministic compute"],"no_trades":True,
     "url":"https://github.com/Sauravssoni/fundtex-skills"},
    {"id":"kite-official","kind":"remote","label":"Zerodha official Kite MCP",
     "endpoint":"https://mcp.kite.trade/mcp",
     "purpose":"Account-entitled data, holdings and quotes in supported AI clients",
     "auth":"Owner approves login and permissions at Zerodha; never sends credentials to Fundtex",
     "actions":["read quoted market data with explicit account consent"],"no_trades":True,
     "url":"https://zerodha.com/products/mcp/"},
    {"id":"openbb-mcp","kind":"optional-local","label":"OpenBB modular data and MCP",
     "endpoint":"http://127.0.0.1:8001/mcp",
     "purpose":"Typed economic/equity data discovery where selected providers and rights are configured",
     "auth":"Isolated user install, extension/data-provider configuration, license terms",
     "actions":["read specifically entitled data"],"no_trades":True,
     "url":"https://github.com/OpenBB-finance/OpenBB"},
    {"id":"lean","kind":"offline-backtest","label":"QuantConnect LEAN",
     "endpoint":"local optional external tool",
     "purpose":"Event-driven professional backtesting; import only authorized point-in-time market datasets",
     "auth":"Separate Docker/CLI installation, dataset entitlements, licensing validation",
     "actions":["offline research backtest"],"no_trades":True,
     "url":"https://github.com/QuantConnect/Lean"},
    {"id":"dhan-optionchain-local","kind":"broker","label":"DhanHQ v2 owner-authorized option chain",
     "endpoint":"POST https://api.dhan.co/v2/optionchain (one explicit call; rate limit per docs)",
     "purpose":"Capture broker-owner-entitled option bid/ask/OI/size snapshots and use local bounded spread analyzer",
     "auth":"Local private FUNDTEX_DHAN_CLIENT_ID and FUNDTEX_DHAN_ACCESS_TOKEN; explicit user-authorized provider login",
     "actions":["read option chain","write source-hashed LOCAL output receipt only"],"no_trades":True,
     "url":"https://dhanhq.co/docs/v2/option-chain/"},
    {"id":"fyers-data","kind":"broker","label":"FYERS authorized history and quote",
     "endpoint":"Official FYERS REST under approved host broker auth",
     "purpose":"Authenticated historical OHLCV and quote snapshots; token expires",
     "auth":"Account holder creates and authorizes app; local secret manager only",
     "actions":["read client-entitled history","read current snapshot"],"no_trades":True,
     "url":"https://fyers.in/api-docs/v3/"},
)
def catalog():
    installed = {module: bool(importlib.util.find_spec(module)) for module in ("mcp","openbb")}
    broker = {name: all(bool(os.getenv(key)) for key in keys) for name,keys in {
        "fyers":("FUNDTEX_FYERS_APP_ID","FUNDTEX_FYERS_ACCESS_TOKEN"),
        "kite_connect":("FUNDTEX_KITE_API_KEY","FUNDTEX_KITE_ACCESS_TOKEN"),
        "dhan":("FUNDTEX_DHAN_CLIENT_ID","FUNDTEX_DHAN_ACCESS_TOKEN")
    }.items()}
    return {"product":"Fundtex Integration Discovery", "network_requests_made":False,
            "accounts_connected_verified":False,"orders_enabled":False,
            "installed_optional_python_modules":installed,
            "broker_local_credential_presence_not_authentication":broker,
            "connectors":[dict(c,connection_verified=False) for c in CONNECTORS],
            "priority":[
                "Use already connected host Kite MCP for broker-authorized read-only data; never import credentials into Fundtex",
                "Use authenticated FYERS REST for client-entitled historical OHLCV if genuinely verified",
                "Use Fundtex local read-only MCP and zero-dependency Python research before requiring any OpenBB/LEAN install",
                "Optionally layer OpenBB read-only provider tools after per-source license and consent review",
                "Use LEAN only in an isolated approved evaluation with broker execution plugins disabled",
            ],
            "never":["Do not claim connected because an SDK is installed",
                     "Do not invoke GTT/order/margin-pledge/write tools",
                     "Do not forward brokerage secrets or private portfolio data to third-party routers",
                     "Do not redistribute exchange data without permission"]}
