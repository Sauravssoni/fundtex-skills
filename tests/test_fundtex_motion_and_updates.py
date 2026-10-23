"""Fundtex chart film and explicit-only update-awareness acceptance gates."""
from datetime import date,timedelta
from hashlib import sha256
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fundtex_india.film_studio import storyboard,create,render_frame,frame_state
from fundtex_india.update_recon import check

class MotionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home=Path(self.tmp.name)
        self.csv=self.home/"synthetic.csv"
        with self.csv.open("w",newline="",encoding="utf-8") as f:
            w=csv.writer(f)
            w.writerow(("date","symbol","open","high","low","close","volume","source"))
            for i in range(125):
                close=100.0+i*.2
                w.writerow(((date(2026,1,1)+timedelta(days=i)).isoformat(),
                            "DEMO.NS",close-.1,close+.4,close-.6,close,10000,"SYNTHETIC_FIXTURE"))
    def test_storyboard_dated_data_and_no_price_from_image(self):
        ref=self.home/"reference.png"
        ref.write_bytes(b"opaque reference bytes, style only")
        story,rows,inds=storyboard(self.csv,"DEMO.NS",reference_chart=ref)
        self.assertIn("SYNTHETIC FIXTURE",story["source_quality"])
        self.assertEqual(story["source_sha256"],sha256(self.csv.read_bytes()).hexdigest())
        self.assertEqual(story["reference_chart"]["purpose"],"VISUAL_STYLE_REFERENCE_ONLY_NOT_PRICE_SOURCE")
        self.assertEqual(story["last_close"],rows[-1]["close"])
        self.assertEqual(story["frames"],120)
        self.assertFalse(story["calibrated_prediction"])
        self.assertEqual(story["trade_recommendation"],"NONE")
    def test_animation_does_not_show_future_rsi_or_full_return_early(self):
        story,rows,inds=storyboard(self.csv,"DEMO.NS")
        first=frame_state(story,rows,inds,0)
        last=frame_state(story,rows,inds,story["frames"]-1)
        self.assertLess(first["visible"],len(rows))
        self.assertEqual(first["date"],rows[first["visible"]-1]["date"])
        self.assertEqual(first["close"],rows[first["visible"]-1]["close"])
        self.assertEqual(first["rsi14_as_of_frame"],inds["rsi14"][len(inds["rsi14"])-len(rows)+first["visible"]-1])
        self.assertNotEqual(first["window_return_pct_to_date"],story["historical_window_return_pct"])
        self.assertEqual(last["date"],story["window_end"])
        self.assertAlmostEqual(last["window_return_pct_to_date"],story["historical_window_return_pct"],places=3)

    def test_storyboard_only_safe_and_no_files_overwritten(self):
        directory=self.home/"new-film"
        result=create(self.csv,"DEMO.NS",directory,make_mp4=False,seconds=6,fps=6)
        self.assertIsNone(result["video"])
        self.assertTrue((directory/"storyboard.json").is_file())
        self.assertTrue((directory/"narration.txt").is_file())
        self.assertFalse((directory/"analysis.mp4").exists())
        with self.assertRaisesRegex(ValueError,"NEW directory"):
            create(self.csv,"DEMO.NS",directory,make_mp4=False)
    def test_missing_or_incompatible_data_abstains(self):
        with self.assertRaisesRegex(ValueError,"Duration"):
            storyboard(self.csv,"DEMO.NS",seconds=90)
        with self.assertRaises(ValueError):
            storyboard(self.csv,"OTHER.NS")
        with self.assertRaisesRegex(ValueError,"Reference chart"):
            storyboard(self.csv,"DEMO.NS",reference_chart=self.csv)
    @unittest.skipUnless(shutil.which("ffmpeg"),"Optional FFmpeg not installed")
    def test_actual_mp4_is_created_with_real_frames(self):
        try:import PIL
        except ImportError:self.skipTest("Pillow optional")
        out=self.home/"film"
        result=create(self.csv,"DEMO.NS",out,seconds=6,fps=6)
        self.assertTrue((out/"analysis.mp4").is_file())
        self.assertGreater((out/"analysis.mp4").stat().st_size,10000)
        self.assertEqual(result["frames"],36)
        self.assertEqual(result["third_party_huashu"],"NOT_INSTALLED_OR_CALLED")
        self.assertFalse(result["trading_authority"])

class UpdateAwarenessTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home=Path(self.tmp.name)
        self.sha="a"*40
        marker=self.home/".local/share/fundtex-intelligence/.installed_source_commit"
        marker.parent.mkdir(parents=True)
        marker.write_text(self.sha+"\n",encoding="ascii")
    def test_offline_doctor_no_network(self):
        with patch("urllib.request.urlopen",side_effect=AssertionError("not authorized")):
            result=check(home=self.home)
        self.assertEqual(result["status"],"OFFLINE_NOT_CHECKED")
        self.assertFalse(result["automatic_install"])
    def test_exact_commit_and_ahead_with_mocked_github(self):
        def fetch(url):
            if "/compare/" in url:return {"status":"ahead","ahead_by":4}
            return {"sha":"b"*40}
        update=check(home=self.home,online=True,fetch=fetch)
        self.assertEqual(update["status"],"UPDATE_AVAILABLE_FOR_SELECTED_REF")
        self.assertEqual(update["commits_behind"],4)
        self.assertTrue(update["user_approval_required_for_upgrade"])
        def same(url):return {"sha":self.sha}
        self.assertEqual(check(home=self.home,online=True,fetch=same)["status"],"UP_TO_DATE_FOR_SELECTED_REF")
    def test_divergent_or_failed_remote_never_promoted_to_update(self):
        self.assertEqual(check(home=self.home,online=True,fetch=lambda url:{"sha":"b"*40} if "/compare/" not in url else {"status":"diverged"})["status"],"BRANCH_DIVERGED_REVIEW_REQUIRED")
        self.assertEqual(check(home=self.home,online=True,fetch=lambda url:{"sha":"malformed"})["status"],"UPDATE_CHECK_FAILED_CLOSED")
        with self.assertRaises(ValueError):check(home=self.home,ref="../../private",online=False)
    def test_cli_film_and_updates_modes(self):
        root=Path(__file__).resolve().parents[1]
        # CLI --storyboard-only runs without ffmpeg and never needs an account.
        with tempfile.TemporaryDirectory() as t:
            file=Path(t)/"data.csv"
            with file.open("w",newline="") as f:
                w=csv.writer(f);w.writerow(("date","symbol","close","source"))
                for i in range(45):
                    w.writerow(((date(2026,1,1)+timedelta(days=i)).isoformat(),"DEMO.NS",100+i,"SYNTHETIC_FIXTURE"))
            out=Path(t)/"film"
            proc=subprocess.run([sys.executable,"-m","fundtex_india.cli","film",
                                "--csv",str(file),"--symbol","DEMO.NS","--out",str(out),"--storyboard-only"],
                               cwd=root,text=True,capture_output=True,timeout=20)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertTrue((out/"storyboard.json").is_file())
            p=subprocess.run([sys.executable,"-m","fundtex_india.cli","updates"],cwd=root,text=True,capture_output=True,timeout=15)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertEqual(json.loads(p.stdout)["status"],"OFFLINE_NOT_CHECKED")

if __name__=="__main__":
    unittest.main()
