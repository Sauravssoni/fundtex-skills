"""Codex/ChatGPT desktop official Kite MCP first-run, no credential or order paths."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from fundtex_india.codex_kite_setup import configure, inspect, KITE_URL, READ_ONLY, FORBIDDEN

class ZeroFrictionKiteTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
    def test_not_configured_does_not_look_at_broker(self):
        first=inspect(home=self.root)
        self.assertEqual(first["status"],"NOT_CONFIGURED")
        self.assertFalse(first["provider_authentication_verified"])
        self.assertFalse(first["real_broker_quote_verified"])
        self.assertFalse(first["trading_enabled"])
        self.assertFalse((self.root/".codex").exists())
    def test_requires_explicit_approval(self):
        with self.assertRaisesRegex(ValueError,"explicitly approve"):
            configure(home=self.root,approved=False)
        self.assertFalse((self.root/".codex").exists())
    def test_one_command_creates_read_only_mcp_config(self):
        r=configure(home=self.root,approved=True)
        self.assertTrue(r["changed"])
        self.assertEqual(r["status"],"MCP_REGISTERED_NOT_AUTHENTICATED")
        self.assertFalse(r["did_not_access_broker"] is False)
        conf=(self.root/".codex/config.toml").read_text()
        self.assertIn(KITE_URL,conf)
        for x in READ_ONLY:self.assertIn('"'+x+'"',conf)
        for x in FORBIDDEN:self.assertIn('"'+x+'"',conf)
        self.assertIn('default_tools_approval_mode = "prompt"',conf)
        self.assertFalse(r["provider_authentication_verified"])
    def test_idempotent_and_backup_first_existing_user_settings(self):
        codex=self.root/".codex"
        codex.mkdir()
        path=codex/"config.toml"
        initial='model = "gpt-6"\n\n[project_settings]\nmode="private"\n'
        path.write_text(initial)
        one=configure(home=self.root,approved=True)
        self.assertTrue(one["backup_created"])
        backup=Path(one["backup_path"])
        self.assertEqual(backup.read_text(),initial)
        self.assertEqual(path.read_text().count("[mcp_servers.fundtex_kite]"),1)
        two=configure(home=self.root,approved=True)
        self.assertFalse(two["changed"])
        self.assertTrue(two["idempotent"])
        self.assertEqual(path.read_text().count("[mcp_servers.fundtex_kite]"),1)
        self.assertTrue(path.read_text().startswith(initial))
    def test_existing_mcp_server_not_overwritten(self):
        conf=self.root/".codex"
        conf.mkdir()
        p=conf/"config.toml"
        src='[mcp_servers.kite]\nurl = "https://mcp.kite.trade/mcp"\n'
        p.write_text(src)
        with self.assertRaisesRegex(ValueError,"EXISTING_KITE_SERVER"):
            configure(home=self.root,approved=True)
        self.assertEqual(p.read_text(),src)
    def test_named_dangerous_configuration_cannot_be_promoted(self):
        conf=self.root/".codex"
        conf.mkdir()
        path=conf/"config.toml"
        path.write_text('[mcp_servers.fundtex_kite]\nurl = "'+KITE_URL+'"\n')
        self.assertEqual(inspect(home=self.root)["status"],"EXISTING_SERVER_PERMISSIONS_REVIEW_REQUIRED")
        with self.assertRaises(ValueError):
            configure(home=self.root,approved=True)
    def test_malformed_toml_fails_without_edit(self):
        conf=self.root/".codex"
        conf.mkdir()
        f=conf/"config.toml"
        s="[broken\npassword = 'private'"
        f.write_text(s)
        with self.assertRaises(ValueError):
            configure(home=self.root,approved=True)
        self.assertEqual(f.read_text(),s)
    def test_cli_setup_reads_no_user_private_data_or_account(self):
        root=Path(__file__).resolve().parents[1]
        env=os.environ.copy();env["HOME"]=str(self.root)
        args=[sys.executable,"-m","fundtex_india.cli","connect",
              "--provider","zerodha-mcp","--setup"]
        r=subprocess.run(args,cwd=root,env=env,text=True,capture_output=True,timeout=15)
        self.assertEqual(r.returncode,0,r.stderr)
        result=json.loads(r.stdout)
        self.assertEqual(result["status"],"MCP_REGISTERED_NOT_AUTHENTICATED")
        self.assertFalse(result["provider_authentication_verified"])
        self.assertNotIn("access_token",r.stdout.lower())
        second=subprocess.run(args,cwd=root,env=env,text=True,capture_output=True,timeout=15)
        self.assertEqual(second.returncode,0,second.stderr)
        self.assertFalse(json.loads(second.stdout)["changed"])
        fail=subprocess.run(args+["--verify","INFY.NS"],cwd=root,env=env,text=True,capture_output=True,timeout=15)
        self.assertEqual(fail.returncode,2)
    def test_no_web_access_or_auto_install(self):
        with patch("webbrowser.open",side_effect=AssertionError("browser")):
            with patch("subprocess.run",side_effect=AssertionError("subprocess")):
                self.assertTrue(configure(home=self.root,approved=True)["changed"])

if __name__=="__main__":
    unittest.main()
