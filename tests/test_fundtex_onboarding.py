"""Offline first-session, context suggestions and installed-health regression suite."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from fundtex_india.onboarding import doctor, suggest, welcome
from fundtex_india.council import plan

ROOT=Path(__file__).resolve().parents[1]


class OnboardingTest(unittest.TestCase):
    def test_recommendations_tailored_to_authorized_brief(self):
        one=suggest("I work on Indian NBFC portfolio management and credit risk")
        self.assertEqual(len(one["suggestions"]),3)
        self.assertTrue(one["research_only"])
        self.assertEqual(one["context_access"],"EXPLICIT_USER_OR_AGENT_PROVIDED_DESCRIPTION_ONLY")
        self.assertTrue(any("portfolio" in text.lower() for text in one["suggestions"]))
        self.assertEqual(one,suggest("I work on Indian NBFC portfolio management and credit risk"))

    def test_empty_history_falls_back_without_inventing_data(self):
        result=suggest()
        self.assertEqual(len(result["suggestions"]),3)
        self.assertFalse(any("I researched your old conversations" in s for s in result["suggestions"]))
        self.assertIn("not searched",result["notice"])
        self.assertIn("Try one of these research-first prompts:",welcome())
        self.assertIn("  1. ",welcome())

    def test_long_sensitive_brief_rejected(self):
        with self.assertRaises(ValueError):
            suggest("x"*1501)

    def test_doctor_with_isolated_installed_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            d=doctor(home=temp,repo_root=str(ROOT))
            self.assertFalse(d["all_india_skills_installed"])
            self.assertTrue(d["checks_are_offline"])
            self.assertTrue(d["readme_available"])
            for agent in (".claude",".codex",".agents"):
                for name in ("fundtex-god-eye","fundtex-auto-analyst","fundtex-india-live-data","fundtex-chart-technician","fundtex-analyst-pack","fundtex-workbook-builder","fundtex-visuals-reporting","fundtex-analyst-council","fundtex-analyst-pilot","fundtex-india-regulatory","fundtex-india-diligence","fundtex-india-forecast","fundtex-india-market",
                             "fundtex-india-news","fundtex-india-risk","fundtex-india-portfolio",
                             "fundtex-india-valuation","fundtex-india-brief","fundtex-hedged-options",
                             "fundtex-strategy-research","fundtex-connector-orchestrator","fundtex-motion-intelligence","fundtex-kronos-intelligence"):
                    dest=Path(temp)/agent/"skills"/name
                    dest.mkdir(parents=True,exist_ok=True)
                    (dest/"SKILL.md").write_text("mock skill test")
            self.assertTrue(doctor(home=temp,repo_root=str(ROOT))["all_india_skills_installed"])

    def test_detect_stale_installed_engine(self):
        with tempfile.TemporaryDirectory() as temp:
            installed=Path(temp)/".local/share/fundtex-intelligence/fundtex_india"
            installed.mkdir(parents=True)
            (installed/"cli.py").write_text("# out of date engine")
            status=doctor(home=temp,repo_root=str(ROOT))
            self.assertTrue(status["installed_engine_stale_relative_to_checkout"])
            self.assertIn("approval",status["upgrade_policy"])

    def test_context_is_not_echoed_to_output(self):
        sensitive="My employer client portfolio confidential codeword ALPHA_DO_NOT_ECHO"
        output=suggest(sensitive)
        self.assertNotIn("ALPHA_DO_NOT_ECHO",json.dumps(output))
        self.assertEqual(len(output["suggestions"]),3)

    def test_council_plan_privacy_and_fallback(self):
        private="Confidential deal code name DO_NOT_ECHO"
        graph=plan(scope=private,max_workers=5,parallel=True)
        self.assertEqual(graph["worker_count"],5)
        self.assertTrue(graph["recommended_parallel"])
        self.assertEqual(graph["data_access"],"NONE_PERFORMED")
        self.assertNotIn("DO_NOT_ECHO",json.dumps(graph))
        seq=plan(scope="portfolio",max_workers=3,parallel=False,mode="QUANT")
        self.assertFalse(seq["recommended_parallel"])
        self.assertEqual(seq["worker_count"],3)
        with self.assertRaises(ValueError): plan(scope="x",max_workers=200)
        with self.assertRaises(ValueError): plan(scope="")

    def test_cli_council_contract(self):
        p=subprocess.run([sys.executable,"-m","fundtex_india.cli","council","--mode","DEEP",
                          "--max-workers","5","--parallel"],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr)
        out=json.loads(p.stdout)
        self.assertEqual(out["worker_count"],5)
        self.assertEqual(out["plan_type"],"SUGGESTED_TASK_GRAPH_NOT_EXECUTION")

    def test_cli_onboard_and_doctor(self):
        for args in (["onboard","--context","Indian bank earnings and forensic cash flows"],["doctor"]):
            cmd=[sys.executable,"-m","fundtex_india.cli"]+args
            p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
            self.assertEqual(p.returncode,0,p.stderr)
            output=json.loads(p.stdout)
            self.assertEqual(output["product"].split("|")[0].strip(),"Fundtex Financial Intelligence")


if __name__ == "__main__":
    unittest.main()
