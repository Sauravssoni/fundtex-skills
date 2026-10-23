"""Safe first-use Zerodha Kite MCP registration for Codex / ChatGPT desktop.

One explicit user approval adds the OFFICIAL hosted read-only market-data tool
allowlist to the shared Codex configuration. Credentials remain broker-hosted.
No broker login, quote, order, data upload or package installation occurs here.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import secrets
import stat
import tempfile

NAME="fundtex_kite"
KITE_URL="https://mcp.kite.trade/mcp"
READ_ONLY=("login","search_instruments","get_quotes","get_ltp",
           "get_ohlc","get_historical_data")
FORBIDDEN=("place_order","modify_order","cancel_order","place_gtt_order",
           "modify_gtt_order","delete_gtt_order")
APPROVAL="prompt"
_SECTION="\n[mcp_servers."+NAME+"]\n"
_CONFIG=(_SECTION+
    'url = "'+KITE_URL+'"\n'+
    'enabled = true\n'+
    'enabled_tools = ['+", ".join('"'+x+'"' for x in READ_ONLY)+']\n'+
    'disabled_tools = ['+", ".join('"'+x+'"' for x in FORBIDDEN)+']\n'+
    'default_tools_approval_mode = "prompt"\n'
)

def _parse_config(value):
    try:
        import tomllib
    except ImportError as exc:
        raise ValueError("Broker one-click setup needs Python >=3.11 for safe TOML parsing; update Python or configure the official MCP host directly") from None
    try:return tomllib.loads(value)
    except (ValueError,TypeError):
        raise ValueError("Existing Codex TOML cannot be safely parsed; no files changed") from None

def _config_file(home):
    home=Path(home).expanduser() if home is not None else Path.home()
    base=home/".codex"
    return base,base/"config.toml"

def inspect(*, home=None):
    base,path=_config_file(home)
    result={"provider":"Zerodha Kite MCP","server_name":NAME,"url":KITE_URL,
            "host_clients":["Codex CLI","Codex app","ChatGPT desktop MCP"],
            "trading_enabled":False,"real_broker_quote_verified":False,
            "provider_authentication_verified":False,
            "login_requires_user_action":True,
            "setup_command":"fundtex connect --provider zerodha-mcp --setup",
            "data_scope":"Read-only market data and instrument lookup; order/GTT tools blocked"}
    if base.is_symlink() or path.is_symlink():
        result["status"]="UNSAFE_SYMLINK_REVIEW_REQUIRED"
        return result
    if not path.exists():
        result["status"]="NOT_CONFIGURED"
        return result
    if path.stat().st_size>2_000_000:
        result["status"]="CONFIG_TOO_LARGE_REVIEW_REQUIRED"
        return result
    try:
        config=_parse_config(path.read_text(encoding="utf-8"))
    except (ValueError,OSError,UnicodeError):
        result["status"]="EXISTING_CONFIG_INVALID_REVIEW_REQUIRED"
        return result
    servers=config.get("mcp_servers",{})
    if not isinstance(servers,dict):
        result["status"]="EXISTING_CONFIG_INVALID_REVIEW_REQUIRED"
        return result
    current=servers.get(NAME)
    for server,settings in servers.items():
        if server!=NAME and isinstance(settings,dict) and settings.get("url")==KITE_URL:
            result["status"]="EXISTING_KITE_SERVER_REVIEW_REQUIRED"
            result["existing_server_name"]=server
            return result
    if current is None:
        result["status"]="NOT_CONFIGURED"
    elif not isinstance(current,dict) or current.get("url")!=KITE_URL:
        result["status"]="EXISTING_NAMED_SERVER_CONFLICT"
    elif (set(current.get("enabled_tools",[]))!=set(READ_ONLY)
          or not set(FORBIDDEN).issubset(set(current.get("disabled_tools",[])))
          or current.get("default_tools_approval_mode")!=APPROVAL
          or current.get("enabled") is not True):
        result["status"]="EXISTING_SERVER_PERMISSIONS_REVIEW_REQUIRED"
    else:
        result["status"]="MCP_REGISTERED_NOT_AUTHENTICATED"
        result["server_allowlist_applied"]=True
    return result

def configure(*, home=None, approved=False):
    if approved is not True:
        raise ValueError("Account holder must explicitly approve this local MCP configuration change")
    base,path=_config_file(home)
    prior=inspect(home=home)
    if prior["status"]=="MCP_REGISTERED_NOT_AUTHENTICATED":
        return {**prior,"changed":False,"idempotent":True}
    if prior["status"]!="NOT_CONFIGURED":
        raise ValueError("Existing MCP configuration needs manual review: "+prior["status"])
    if base.is_symlink() or path.is_symlink():
        raise ValueError("Refuse symlinked Codex configuration")
    # Do not scan or touch unrelated application accounts or workspace files.
    if not base.exists():
        base.mkdir(mode=0o700,parents=True)
    if not base.is_dir():raise ValueError("Codex config parent is not a directory")
    original=path.read_text(encoding="utf-8") if path.exists() else ""
    if len(original.encode("utf-8"))>2_000_000:
        raise ValueError("Codex config unexpectedly large")
    config=_parse_config(original)
    if config.get("mcp_servers") is not None and not isinstance(config["mcp_servers"],dict):
        raise ValueError("Codex MCP config invalid")
    # Avoid a race with another editor's config modifications.
    before_hash=hashlib.sha256(original.encode()).hexdigest()
    addition=("\n" if original and not original.endswith("\n") else "")+_CONFIG
    rendered=original+addition
    parsed=_parse_config(rendered)
    entry=parsed.get("mcp_servers",{}).get(NAME,{})
    if entry.get("url")!=KITE_URL or set(entry.get("enabled_tools",[]))!=set(READ_ONLY):
        raise ValueError("MCP configuration validation failed")
    backup=None
    if path.exists():
        backups=base/"fundtex-backups"
        backups.mkdir(mode=0o700,exist_ok=True)
        backup=backups/("config-"+datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")+"-"+secrets.token_hex(4)+".toml")
        fd=os.open(backup,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,"w",encoding="utf-8") as handle:handle.write(original)
    # Atomic local operation, protected restrictive permissions, no log of secrets.
    staged=None
    try:
        if (path.read_text(encoding="utf-8") if path.exists() else "")!=original:
            raise ValueError("Codex config changed during setup, do not overwrite")
        with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=base,
                                         prefix=".fundtex-kite-next-",delete=False) as temp:
            staged=Path(temp.name)
            temp.write(rendered)
            temp.flush()
            os.fchmod(temp.fileno(),stat.S_IRUSR|stat.S_IWUSR)
            os.fsync(temp.fileno())
        if (path.read_text(encoding="utf-8") if path.exists() else "")!=original:
            raise ValueError("Codex config changed during setup; refusing replacement")
        os.replace(staged,path)
    finally:
        if staged and staged.exists():staged.unlink()
    return {**inspect(home=home),"changed":True,"backup_created":bool(backup),
            "backup_path":str(backup) if backup else None,
            "previous_config_sha256":before_hash,
            "next_steps":[
                "Restart Codex or ChatGPT Desktop to discover the official Kite MCP server",
                "Find fundtex_kite in MCP servers and use Authenticate if prompted",
                "Sign in and consent only on Zerodha's official Kite site",
                "Ask your agent to discover read-only tools and verify one dated NSE quote",
                "Until then, account access remains NOT_AUTHENTICATED"],
            "no_order_access_requested":True,
            "did_not_access_broker":True}
