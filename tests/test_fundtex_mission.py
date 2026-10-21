"""Fundtex Mission Control: offline, bounded, privacy-aware agent plan tests."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

from fundtex_india.mission import mission, as_markdown

ROOT=Path(__file__).resolve().parents[1]

class MissionTests(unittest.TestCase):
    def test_default_sequential_and_skep(self):
        a=mission("Indian equity fundamental diligence")
        self.assertTrue(a["plan_only"])
        self.assertEqual(a["execution"],"SEQUENTIAL_FALLBACK")
        self.assertFalse(a["readiness"]["can_spawn_here"])
        self.assertFalse(a["readiness"]["may_access_authorized_web"])
        self.assertIn("skeptic",[x["id"] for x in a["assigned_roles"]])
        self.assertTrue(a["readiness"]["can_calculate_locally"])
        self.assertNotIn("Indian equity fundamental diligence",json.dumps(a))

    def test_parallel_only_with_tools_and_explicit_approval(self):
        kw={"agent":"claude","mode":"DEEP","abilities":("terminal","python","web","subagents"),"max_workers":5}
        unapproved=mission("Compare Indian banking earnings",**kw)
        self.assertEqual(unapproved["execution"],"SEQUENTIAL_FALLBACK")
        self.assertFalse(unapproved["readiness"]["may_access_authorized_web"])
        approved=mission("Compare Indian banking earnings",confirmed_permission=True,**kw)
        self.assertEqual(approved["execution"],"PARALLEL_IF_HOST_SUPPORTS_AND_APPROVED")
        self.assertTrue(approved["readiness"]["may_access_authorized_web"])
        self.assertEqual(len(approved["assigned_roles"]),5)
        self.assertIn("skeptic",[r["id"] for r in approved["assigned_roles"]])
        self.assertEqual(approved,mission("Compare Indian banking earnings",confirmed_permission=True,**kw))

    def test_small_worker_limit_preserves_independent_skeptic(self):
        out=mission("Indian NBFC loan quality",mode="INSTITUTIONAL",max_workers=2,
                    abilities=("terminal",),confirmed_permission=True)
        self.assertEqual(len(out["assigned_roles"]),2)
        self.assertIn("skeptic",[r["id"] for r in out["assigned_roles"]])
        self.assertFalse(out["readiness"]["can_calculate_locally"])

    def test_no_tools_is_a_real_fallback(self):
        x=mission("Evaluate my Indian stock portfolio",agent="gemini",abilities=(),mode="DEEP")
        self.assertEqual(x["execution"],"SEQUENTIAL_FALLBACK")
        self.assertFalse(x["readiness"]["can_calculate_locally"])
        self.assertFalse(x["readiness"]["may_access_authorized_web"])
        self.assertIn("missing_terminal",x["fallbacks"])
        self.assertIn("missing_web",x["fallbacks"])

    def test_input_validation_and_privacy(self):
        for task in ("", "x"*801):
            with self.assertRaises(ValueError):
                mission(task)
        with self.assertRaises(ValueError):
            mission("financials",abilities=("unrecognized_tool",))
        with self.assertRaises(ValueError):
            mission("financials",agent="fake")
        with self.assertRaises(ValueError):
            mission("financials",max_workers=7)
        private="SECRET_SHAREHOLDING_REPORT_DO_NOT_ECHO"
        x=mission(private,mode="DEEP",abilities=("terminal",))
        self.assertNotIn(private,json.dumps(x))
        self.assertEqual(len(x["task_sha256"]),64)

    def test_cli_markdown_and_json(self):
        base=[sys.executable,"-m","fundtex_india.cli","mission","--task","NSE equity diligence",
              "--agent","codex","--mode","DEEP","--abilities","terminal,python","--max-workers","5"]
        x=subprocess.run(base+["--format","json"],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(x.returncode,0,x.stderr)
        j=json.loads(x.stdout)
        self.assertTrue(j["plan_only"])
        self.assertEqual(j["declared_agent"],"codex")
        y=subprocess.run(base+["--format","markdown"],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(y.returncode,0,y.stderr)
        self.assertIn("Analyst Mission Brief",y.stdout)
        self.assertIn("Independent",y.stdout)

if __name__=="__main__":
    unittest.main()
