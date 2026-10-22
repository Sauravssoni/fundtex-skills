import json
from pathlib import Path
import tempfile
import unittest
from fundtex_india.activity import emit, read_events

class AgentActivity(unittest.TestCase):
    def test_emit_real_events(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"events.jsonl"
            a=emit(p,agent="Claude Code",event="issuer-filing",status="start",detail="Reading approved source")
            self.assertTrue(a["recorded"])
            self.assertFalse(a["data_sent_off_device"])
            self.assertEqual(read_events(p)[0]["agent"],"Claude Code")
    def test_secrets_and_arbitrary_symbols_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"events.jsonl"
            with self.assertRaises(ValueError):emit(p,agent="Codex",event="auth",status="progress",detail="api_key=abc")
            with self.assertRaises(ValueError):emit(p,agent="<script>",event="source",status="done")
            self.assertFalse(p.exists())
    def test_reject_symlink(self):
        with tempfile.TemporaryDirectory() as t:
            a=Path(t)/"a";a.write_text("private")
            b=Path(t)/"b";b.symlink_to(a)
            with self.assertRaises(ValueError):read_events(b)
if __name__=="__main__":
    unittest.main()
