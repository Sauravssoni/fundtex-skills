"""Cross-agent instructions, skill discovery, and first-use CLI regression contracts."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest
from fundtex_india.onboarding import doctor

ROOT=Path(__file__).resolve().parents[1]

class AgentPortabilityTests(unittest.TestCase):
    def test_expected_32_skills_have_valid_frontmatter(self):
        folders=sorted(p for p in ROOT.iterdir() if p.is_dir()
                       and p.name.startswith(("fundtex-","trader-")) and (p/"SKILL.md").is_file())
        self.assertEqual(len(folders),37)
        self.assertEqual(sum(x.name.startswith("fundtex-") for x in folders),26)
        for folder in folders:
            lines=(folder/"SKILL.md").read_text(encoding="utf-8").splitlines()
            self.assertGreater(len(lines),8,folder.name)
            self.assertEqual(lines[0],"---",folder.name)
            self.assertIn("---",lines[1:25],folder.name)
            header=lines[1:lines[1:25].index("---")+1]
            self.assertTrue(any(line.startswith("name:") for line in header),folder.name)
            self.assertTrue(any(line.startswith("description:") for line in header),folder.name)

    def test_portable_workspace_instructions_exist_and_are_bounded(self):
        paths=("AGENTS.md","CLAUDE.md","GEMINI.md",".github/copilot-instructions.md",
               ".cursor/rules/fundtex-research.mdc","docs/AGENT_PORTABILITY.md",
               "docs/ANALYST_DELIVERY_CONTRACT.md","docs/CLAUDE_FIRST_RUN.md")
        for name in paths:
            self.assertTrue((ROOT/name).is_file(),name)
            self.assertTrue((ROOT/name).stat().st_size>100,name)
        cursor=(ROOT/".cursor/rules/fundtex-research.mdc").read_text()
        self.assertTrue(cursor.startswith("---\n"))
        self.assertIn("alwaysApply: false",cursor)
        for forbidden in (".claude-plugin/plugin.json",".codex-plugin/plugin.json"):
            self.assertFalse((ROOT/forbidden).exists())

    def test_clean_install_and_doctor_fallback(self):
        with tempfile.TemporaryDirectory() as temp:
            env=os.environ.copy()
            env["HOME"]=temp
            a=subprocess.run(["bash","install.sh"],cwd=ROOT,env=env,text=True,capture_output=True)
            b=subprocess.run(["bash","install.sh"],cwd=ROOT,env=env,text=True,capture_output=True)
            self.assertEqual(a.returncode,0,a.stderr)
            self.assertEqual(b.returncode,0,b.stderr)
            self.assertIn("skills installed=111 skipped=0",a.stdout)
            self.assertIn("skills installed=0 skipped=111",b.stdout)
            self.assertIn("Try one of these research-first prompts:",a.stdout)
            status=doctor(home=temp,repo_root=str(ROOT))
            self.assertTrue(status["all_india_skills_installed"])
            self.assertFalse(status["installed_engine_stale_relative_to_checkout"])
            self.assertTrue(status["installed_reference_bundle_present"])
            self.assertTrue(status["autonomous_first_run_ready"])
            self.assertEqual(status["missing_reference_paths"], [])
            self.assertTrue((Path(temp)/".local/share/fundtex-intelligence/docs/CLAUDE_FIRST_RUN.md").is_file())
            self.assertTrue((Path(temp)/".local/share/fundtex-intelligence/examples/india_prices.csv").is_file())
            for v in status["installation"].values():
                self.assertEqual(v["india_skills_present"],26)
            launcher=Path(temp)/".local/bin/fundtex"
            p=subprocess.run([str(launcher),"mission","--task","Indian bank research",
                               "--agent","gemini","--mode","DEEP","--abilities",
                               "terminal,python","--format","json"],
                             cwd=ROOT,env=env,text=True,capture_output=True)
            self.assertEqual(p.returncode,0,p.stderr)
            result=json.loads(p.stdout)
            self.assertTrue(result["plan_only"])
            self.assertEqual(result["execution"],"SEQUENTIAL_FALLBACK")
            # Upgrade is explicit, preserves a real copy of customized skill contents.
            modified=Path(temp)/".claude/skills/fundtex-auto-analyst/SKILL.md"
            modified.write_text(modified.read_text()+"\nCUSTOM_USER_MARKER_KEEP_IN_BACKUP\n")
            update=subprocess.run(["bash","install.sh","--upgrade"],cwd=ROOT,env=env,text=True,capture_output=True)
            self.assertEqual(update.returncode,0,update.stderr)
            self.assertIn("updated=111",update.stdout)
            self.assertIn("UPDATE docs references",update.stdout)
            self.assertIn("UPDATE examples references",update.stdout)
            self.assertTrue(doctor(home=temp,repo_root=str(ROOT))["autonomous_first_run_ready"])
            self.assertNotIn("CUSTOM_USER_MARKER_KEEP_IN_BACKUP",modified.read_text())
            backups=list((Path(temp)/".local/share/fundtex-intelligence").glob(
                "fundtex-backup-*/agent-1-fundtex-auto-analyst/SKILL.md"))
            self.assertEqual(len(backups),1)
            self.assertIn("CUSTOM_USER_MARKER_KEEP_IN_BACKUP",backups[0].read_text())
            self.assertFalse(doctor(home=temp,repo_root=str(ROOT))["installed_engine_stale_relative_to_checkout"])

if __name__ == "__main__":
    unittest.main()
