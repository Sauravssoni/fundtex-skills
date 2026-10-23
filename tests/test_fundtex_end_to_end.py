"""Offline E2E user-journey regression: real engine composition, no broker/network."""
from pathlib import Path
import json
from hashlib import sha256
import tempfile
import unittest
from unittest.mock import patch
from fundtex_india.acceptance import run

class WholeProductOfflineTest(unittest.TestCase):
    def test_full_seven_stage_research_and_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/"first-user"
            with patch("socket.create_connection",side_effect=AssertionError("network prohibited")):
                result=run(folder)
            self.assertEqual(result["checked_components"],7)
            self.assertEqual(result["status"],"PASS_OFFLINE_SYNTHETIC_COMPONENTS_ONLY")
            self.assertEqual(result["release_decision"],"BLOCKED_UNTIL_LIVE_BROKER_AUTH_OAUTH_AND_LICENSE_GATES")
            self.assertTrue(all(c["status"]=="PASS" for c in result["checks"]))
            self.assertFalse(result["real_market_data_verified"])
            self.assertFalse(result["broker_session_authenticated"])
            self.assertFalse(result["broker_gateway_production_ready"])
            self.assertFalse(result["real_kronos_model_executed"])
            self.assertFalse(result["derivatives_chain_verified"])
            self.assertEqual(result["real_orders_executed"],0)
            self.assertTrue((folder/"chart.svg").is_file())
            self.assertTrue((folder/"film/storyboard.json").is_file())
            self.assertFalse((folder/"film/analysis.mp4").exists())
            self.assertTrue((folder/"README.txt").is_file())
            self.assertIn("SYNTHETIC", (folder/"README.txt").read_text())
            artifact_hashes=result["artifact_digests_sha256"]
            self.assertGreaterEqual(len(artifact_hashes),8)
            for relative,digest in artifact_hashes.items():
                self.assertEqual(sha256((folder/relative).read_bytes()).hexdigest(),digest)

            history=json.loads((folder/"strategy.json").read_text())
            paper=json.loads((folder/"paper-cost-placebo.json").read_text())
            forecast=json.loads((folder/"forecast-baselines.json").read_text())
            board=json.loads((folder/"film/storyboard.json").read_text())
            for record in (history,paper,forecast,board):
                self.assertEqual(record["source_sha256"],result["source_sha256"])
            self.assertEqual(history["data_quality"],"SYNTHETIC_FIXTURE")
            with self.assertRaisesRegex(ValueError,"NEW path"):
                run(folder)
    def test_failure_never_creates_production_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            with self.assertRaisesRegex(ValueError,"NEW path"):
                run(base)
            self.assertFalse((base/"acceptance-report.json").exists())
            self.assertFalse((base/"SYNTHETIC-OHLC.csv").exists())
if __name__=="__main__":
    unittest.main()
