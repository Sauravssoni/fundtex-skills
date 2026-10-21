"""HTTPS fetch via verified TLS. macOS native curl is a fallback ONLY for broken Python CA installation."""
from __future__ import annotations
import shutil
import ssl
import subprocess
import urllib.error
import urllib.parse
import urllib.request

ALLOWED_HOSTS = {"news.google.com", "query1.finance.yahoo.com"}

def fetch_bytes(url: str, *, max_bytes=2_000_000, timeout=12, headers=None) -> bytes:
    host = urllib.parse.urlsplit(url).hostname
    if urllib.parse.urlsplit(url).scheme != "https" or host not in ALLOWED_HOSTS:
        raise ValueError("HTTP client only allows approved HTTPS market/news hosts")
    headers = headers or {"User-Agent": "FundtexResearch/0.1"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read(max_bytes + 1)
    except urllib.error.URLError as exc:
        # Python.org macOS builds sometimes have no OpenSSL CA bundle. System
        # curl validates using the OS trust store. NEVER disable TLS verification.
        if not isinstance(getattr(exc, "reason", None), ssl.SSLCertVerificationError):
            raise
        if not shutil.which("curl"):
            raise OSError("Python TLS CA bundle missing and secure system curl unavailable") from exc
        args = ["curl", "--fail", "--silent", "--show-error", "--location",
                "--max-time", str(timeout), "--user-agent",
                headers.get("User-Agent", "FundtexResearch/0.1"), url]
        result = subprocess.run(args, capture_output=True, timeout=timeout+3, check=False)
        if result.returncode:
            raise OSError("Secure system curl fetch failed: " + result.stderr.decode("utf-8", errors="replace")[:400]) from exc
        body = result.stdout
    if len(body) > max_bytes:
        raise ValueError("Remote response exceeds maximum permitted size")
    return body
