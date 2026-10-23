"""Agent-readable read-only brokerage onboarding without secret collection.

This module NEVER asks for secrets, writes tokens, handles login callbacks, or
asserts that a broker was connected. Account approval is user's action.
"""
from __future__ import annotations
import webbrowser
from .broker_quotes import availability, quote
from .market import validate_symbol

PROVIDERS={
    "zerodha-mcp":{
        "name":"Zerodha Kite MCP (Codex, ChatGPT Desktop and supported hosts)",
        "url":"https://zerodha.com/products/mcp/",
        "mode":"Official hosted read-only research MCP, permissioned by Codex/ChatGPT Desktop",
        "pricing":"Broker advertises no extra charge for Kite MCP; confirm current terms",
        "steps":[
            "Approve official hosted Kite setup by running fundtex connect --provider zerodha-mcp --setup.",
            "Restart Codex/ChatGPT Desktop and open MCP settings; the official Kite server appears for user authentication.",
            "The account holder signs in and consents through Zerodha's official authentication page, not through Fundtex or chat.",
            "The host allows only instrument lookup, OHLC/LTP/quotes/historical data; block GTT/order tools and require user consent for login.",
            "Verify a real read-only quote in the host before declaring authenticated. The Python CLI does not inherit broker OAuth without an authorized bridge."
        ],
        "credential_handling":"No credentials in Fundtex; broker handles login and consent.",
        "cli_quote_supported":False
    },
    "fyers":{
        "name":"FYERS v3 personal API",
        "url":"https://fyers.in/api-docs/v3/getting-started/authentication/",
        "mode":"Personal developer app with browser authorization + short-lived token",
        "pricing":"Eligible FYERS clients: provider advertises data APIs at no extra subscription; confirm current eligibility",
        "steps":[
            "Use the official FYERS API Dashboard to create an individual application and an authorized redirect URI.",
            "Follow the documented browser authorization-code flow and grant only necessary permissions.",
            "Exchange the authorization code for an access token using the official secure instructions; do not paste codes or secrets into chat.",
            "Store app ID and access token in the user's approved local secret manager or protected terminal environment as FUNDTEX_FYERS_APP_ID and FUNDTEX_FYERS_ACCESS_TOKEN.",
            "Ask the agent to run the read-only broker quote verification, then choose --source fyers for authorized daily OHLCV candlesticks. FYERS tokens can expire daily."
        ],
        "credential_handling":"OS/private runtime secret storage only; never chat, git, command history or public logs.",
        "cli_quote_supported":True
    },
    "kite":{
        "name":"Zerodha Kite Connect developer API",
        "url":"https://kite.trade/docs/connect/v3/user/",
        "mode":"Kite Connect API app; separate from free Kite MCP",
        "pricing":"Retail Personal: no market data; retail Connect ₹500/month, October 2026 active-trader credits may apply; qualifying mass-retail startups may request free developer APIs directly from Zerodha. Free Kite MCP remains separate.",
        "steps":[
            "If using Claude and only needing AI-assistant market data, consider official free Kite MCP instead of a paid developer app.",
            "Otherwise open Zerodha Kite Connect's official developer console, create/authorize an app and confirm market-data access.",
            "Complete browser login and redirect/token issuance in the broker-approved application; Fundtex does not implement the login flow.",
            "Store FUNDTEX_KITE_API_KEY and FUNDTEX_KITE_ACCESS_TOKEN in the user's approved private local environment.",
            "Ask Fundtex to verify one read-only quote; report any missing/expired entitlement without inventing data."
        ],
        "credential_handling":"Only locally configured environment/secret manager; no account password in AI chat.",
        "cli_quote_supported":True
    },
    "dhan":{
        "name":"DhanHQ v2 market-data API",
        "url":"https://dhan.co/support/platforms/dhanhq-api/how-to-access-dhan-api/",
        "mode":"Dhan Web > Profile > DhanHQ Trading & Data APIs",
        "pricing":"Data API subscription ₹499 + applicable taxes per month on current Dhan guidance; verify before paying",
        "steps":[
            "Log into official Dhan Web using the user's own browser and open Profile > DhanHQ Trading/Data APIs.",
            "Check Data APIs entitlement and price; any payment or subscription must be explicitly approved by the account owner.",
            "Generate an official short-lived access token in the broker's browser, never paste it into Claude/Fundtex conversation.",
            "Store FUNDTEX_DHAN_CLIENT_ID and FUNDTEX_DHAN_ACCESS_TOKEN in a permitted local secret manager/environment.",
            "Create FUNDTEX_DHAN_SYMBOL_MAP using verified exchange-specific Dhan security IDs, then verify one read-only quote. No guessed security IDs."
        ],
        "credential_handling":"Local secret manager only; never automated payment or account trading.",
        "cli_quote_supported":True
    }
}

def guide(provider="choose",*,open_official=False,verify_symbol=None):
    status=availability()
    if provider=="choose":
        if verify_symbol:raise ValueError("Choose a specific provider before verification")
        return {
            "connected":False,"action":"ASK_USER_TO_CHOOSE_BROKER",
            "question":"Which broker would you like to connect for live read-only market data?",
            "options":[{"id":key,"label":val["name"],"mode":val["mode"],
                        "pricing":val["pricing"],"url":val["url"]}
                       for key,val in PROVIDERS.items()],
            "existing_configuration":{key:bool(status.get(key)) for key in ("fyers","kite","dhan")},
            "privacy":"Never paste passwords, OAuth codes or access tokens into chat. Authentication remains with the broker.",
            "note":"Showing instructions does not authenticate an account; --setup configures a protected MCP entry only."
        }
    if provider not in PROVIDERS:raise ValueError("Unknown broker. Choose fyers, kite, dhan or zerodha-mcp")
    info=PROVIDERS[provider]
    result={"provider":provider,**info,"connected":False,"authorization_required":True,
            "status":"INSTRUCTIONS_ONLY_NOT_CONNECTED",
            "credential_configured":bool(status.get(provider,False)),
            "trading_authority":False}
    if open_official:
        success=webbrowser.open(info["url"])
        result["browser_open_requested"]=bool(success)
    if verify_symbol:
        if not info["cli_quote_supported"]:
            raise ValueError("Kite MCP verification must happen through the connected AI host, not the Fundtex CLI")
        sym=validate_symbol(verify_symbol)
        if not result["credential_configured"]:
            result["verification"]={"status":"NOT_CONFIGURED","symbol":sym}
        else:
            # This is a real authenticated quote test. No fallback; failures are explicit.
            try:
                sample=quote(sym,provider)
                result["verification"]={"status":"AUTHENTICATED_QUOTE_RETURNED",
                    "symbol":sym,"price_inr":sample["last_price_inr"],
                    "retrieved_at_utc":sample["retrieved_at_utc"],
                    "provider_trade_timestamp":sample.get("publisher_trade_timestamp"),
                    "research_only":True}
                result["connected"]=True
                result["status"]="READ_ONLY_BROKER_QUOTE_VERIFIED"
            except (ValueError,OSError) as exc:
                result["verification"]={"status":"CONNECTION_FAILED","symbol":sym,
                    "reason":str(exc)[:180]}
    return result
