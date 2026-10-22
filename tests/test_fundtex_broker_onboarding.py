"""Document-level regression: natural-language broker setup, consent and research-only boundaries."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "BROKER_CONNECTION_ASSISTANT.md"
AUTO = ROOT / "fundtex-auto-analyst" / "SKILL.md"
DATA = ROOT / "fundtex-india-live-data" / "SKILL.md"


class BrokerOnboardingContractTests(unittest.TestCase):
    def test_official_kite_mcp_not_third_party_clone(self):
        text = GUIDE.read_text(encoding="utf-8")
        self.assertIn("https://mcp.kite.trade/mcp", text)
        self.assertIn("claude mcp add --transport http --scope user kite https://mcp.kite.trade/mcp", text)
        self.assertIn("https://zerodha.com/products/mcp/", text)
        self.assertNotIn("kite-mcp-server.fly.dev", text)
        self.assertIn("distinct", text.lower())

    def test_broker_login_explicit_consent_and_no_trade(self):
        text = GUIDE.read_text(encoding="utf-8")
        for clause in ("explicitly agrees", "read-only", "Do NOT", "Never", "GTT", "credentials",
                       "not a separate", "24 hours", "MCP"):
            self.assertIn(clause.lower(), text.lower())
        self.assertIn("does NOT populate FUNDTEX_KITE_API_KEY", text)

    def test_autonomous_agent_prompt_routes_correctly(self):
        auto = AUTO.read_text(encoding="utf-8")
        data = DATA.read_text(encoding="utf-8")
        for page in (auto, data):
            self.assertIn("BROKER_CONNECTION_ASSISTANT.md", page)
            self.assertIn("https://mcp.kite.trade/mcp", page)
        self.assertIn("Do not ask them to find scripts", auto)
        self.assertIn("one concise question", auto)
        self.assertIn("NO_CONFIGURED_BROKER", auto)

    def test_root_discovery_and_public_only(self):
        for name in ("AGENTS.md", "CLAUDE.md", "README.md"):
            text = (ROOT/name).read_text(encoding="utf-8")
            self.assertIn("docs/BROKER_CONNECTION_ASSISTANT.md", text)
        guide = GUIDE.read_text(encoding="utf-8")
        self.assertNotIn("FUNDTEX_KITE_ACCESS_TOKEN=", guide)
        self.assertNotIn("sk_live_", guide)

if __name__ == "__main__":
    unittest.main()
