"""Broker onboarding contract tests: no tokens, permission gates, honest verification."""
import json,os,unittest
from unittest.mock import patch
from fundtex_india import broker_onboarding
from fundtex_india.cli import main

class BrokerGuideTests(unittest.TestCase):
    def test_choose_is_user_question_not_auto_connection(self):
        x=broker_onboarding.guide()
        self.assertEqual(x["action"],"ASK_USER_TO_CHOOSE_BROKER")
        self.assertFalse(x["connected"])
        self.assertEqual(len(x["options"]),4)
        self.assertIn("Zerodha",x["options"][0]["label"])
    def test_each_official_guide_no_secret_material(self):
        for p in ("zerodha-mcp","fyers","kite","dhan"):
            x=broker_onboarding.guide(p)
            self.assertFalse(x["connected"])
            self.assertEqual(x["status"],"INSTRUCTIONS_ONLY_NOT_CONNECTED")
            self.assertTrue(x["url"].startswith("https://"))
            self.assertGreaterEqual(len(x["steps"]),4)
            self.assertNotIn("MY_FAKE_SECRET",json.dumps(x))
    def test_configuration_is_not_authenticated(self):
        with patch("fundtex_india.broker_onboarding.availability",return_value={"fyers":True}):
            x=broker_onboarding.guide("fyers")
            self.assertTrue(x["credential_configured"])
            self.assertFalse(x["connected"])
    def test_user_has_not_configured(self):
        with patch("fundtex_india.broker_onboarding.availability",return_value={"fyers":False}):
            with patch("fundtex_india.broker_onboarding.quote") as q:
                x=broker_onboarding.guide("fyers",verify_symbol="INFY.NS")
                self.assertEqual(x["verification"]["status"],"NOT_CONFIGURED")
                q.assert_not_called()
    def test_verified_quote_and_bad_quote(self):
        with patch("fundtex_india.broker_onboarding.availability",return_value={"fyers":True}):
            with patch("fundtex_india.broker_onboarding.quote",return_value={
                "symbol":"INFY.NS","provider":"fyers","last_price_inr":1200.5,
                "retrieved_at_utc":"2026-10-22T12:00:00Z","publisher_trade_timestamp":None}):
                x=broker_onboarding.guide("fyers",verify_symbol="INFY.NS")
                self.assertTrue(x["connected"])
                self.assertEqual(x["verification"]["status"],"AUTHENTICATED_QUOTE_RETURNED")
            with patch("fundtex_india.broker_onboarding.quote",side_effect=ValueError("no entitlement")):
                x=broker_onboarding.guide("fyers",verify_symbol="INFY.NS")
                self.assertFalse(x["connected"])
                self.assertEqual(x["verification"]["status"],"CONNECTION_FAILED")
    def test_foreign_mcp_does_not_claim_direct_cli(self):
        with self.assertRaisesRegex(ValueError,"connected AI host"):
            broker_onboarding.guide("zerodha-mcp",verify_symbol="INFY.NS")
    def test_open_official_opt_in(self):
        with patch("fundtex_india.broker_onboarding.webbrowser.open",return_value=True) as op:
            broker_onboarding.guide("fyers",open_official=False)
            op.assert_not_called()
            x=broker_onboarding.guide("fyers",open_official=True)
            self.assertTrue(x["browser_open_requested"])
            op.assert_called_once()
    def test_cli_smoke(self):
        self.assertEqual(main(["connect","--provider","choose"]),0)

if __name__=="__main__":unittest.main()
