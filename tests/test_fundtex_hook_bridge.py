"""Private host lifecycle instrumentation emits only fixed public event details."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fundtex_india.hook_bridge import record,main
from fundtex_india.activity import read_events

class AgentHookBridgeTests(unittest.TestCase):
    def test_no_logging_without_explicit_owner_opt_in(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"agent-events.jsonl"
            r=record("codex","SessionStart",environment={"FUNDTEX_EVENT_LOG":str(path)})
            self.assertEqual(r["reason"],"OWNER_OPT_IN_REQUIRED")
            self.assertFalse(path.exists())
    def test_actual_host_name_fixed_and_no_payload_exposed(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"agent-events.jsonl"
            env={"FUNDTEX_EVENT_OPT_IN":"1","FUNDTEX_EVENT_LOG":str(path),
                 "PROMPT":"confidential brokerage token bearer SUPER_SECRET"}
            for event in ("SessionStart","PreToolUse","PostToolUse","SubagentStart","SubagentStop","Stop"):
                self.assertTrue(record("claude",event,environment=env)["recorded"])
            events=read_events(path)
            self.assertEqual(len(events),6)
            self.assertEqual(events[0]["agent"],"Claude Code")
            self.assertEqual(events[3]["event"],"subagent-start")
            self.assertNotIn("SUPER_SECRET",path.read_text())
            self.assertNotIn("confidential",path.read_text())
    def test_codex_labels_and_unsupported_input_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"events.jsonl"
            env={"FUNDTEX_EVENT_OPT_IN":"1","FUNDTEX_EVENT_LOG":str(path)}
            self.assertTrue(record("codex","SessionEnd",environment=env)["recorded"])
            self.assertEqual(read_events(path)[0]["agent"],"Codex")
            for host,event in (("untrusted","SessionStart"),("codex","DangerousHook")):
                with self.assertRaises(ValueError):
                    record(host,event,environment=env)
            self.assertEqual(len(read_events(path)),1)
    def test_relative_path_and_missing_parent_never_write(self):
        a=record("codex","SessionStart",environment={"FUNDTEX_EVENT_OPT_IN":"1","FUNDTEX_EVENT_LOG":"events.jsonl"})
        self.assertEqual(a["reason"],"APPROVED_ABSOLUTE_EVENT_LOG_REQUIRED")
    def test_no_stdout_in_runtime_hook(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"events.jsonl"
            with patch.dict(os.environ,{"FUNDTEX_EVENT_OPT_IN":"1","FUNDTEX_EVENT_LOG":str(path)}):
                from io import StringIO
                from contextlib import redirect_stdout
                output=StringIO()
                with redirect_stdout(output):
                    self.assertEqual(main(["--host","codex","--event","Stop"]),0)
                self.assertEqual(output.getvalue(),"")
                self.assertEqual(len(read_events(path)),1)
if __name__=="__main__":
    unittest.main()
