"""Source adapter and analyst pilot tests: offline, no financial network required."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from fundtex_india import amfi, regulatory, pilot, mcp_server

ROOT=Path(__file__).resolve().parents[1]

class RegulatoryTests(unittest.TestCase):
    def test_catalog_is_official_and_entitlement_safe(self):
        out=regulatory.catalog()
        self.assertFalse(out["live_market_data_entitlement"])
        self.assertEqual(set(out["official_rss_feeds"]),{"sebi","rbi-releases","rbi-notifications"})
        self.assertTrue(all(v["url"].startswith("https://") for v in out["official_rss_feeds"].values()))

    def test_offline_rss_parse_and_dates(self):
        r=regulatory.from_file(ROOT/"examples/regulatory_fixture_SYNTHETIC.xml",source="SYNTHETIC_FIXTURE")
        self.assertEqual(r["items_returned"],2)
        self.assertTrue(r["items"][0]["requires_opening_link"])
        self.assertEqual(r["items"][0]["published_at_utc"],"2026-10-21T09:00:00+00:00")
        self.assertIn("UNVERIFIED",r["source_status"])
        self.assertEqual(len(r["input_sha256"]),64)
        self.assertEqual(regulatory.from_file(ROOT/"examples/regulatory_fixture_SYNTHETIC.xml")["input_sha256"],r["input_sha256"])

    def test_rss_poisoned_and_garbage_fail_closed(self):
        for s in ('<!DOCTYPE rss [ <!ENTITY foo "x"> ]><rss/>',"<rss><channel><item></rss>","<html>not rss</html>"):
            with self.assertRaises(ValueError):
                regulatory.parse_feed(s,"attack")
        with self.assertRaises(ValueError):
            regulatory.parse_feed("x"*regulatory.MAX_BYTES+"Y","too big")
        with self.assertRaises(ValueError):
            regulatory.fetch("unknown")
        with self.assertRaises(ValueError):
            regulatory.fetch("sebi",timeout=0)

    def test_feed_skips_nonhttps_phishing(self):
        xml="<rss><channel><item><title>Text</title><link>http://evil.example/phish</link><pubDate>Wed, 21 Oct 2026 09:00:00 GMT</pubDate></item></channel></rss>"
        self.assertEqual(regulatory.parse_feed(xml,"test")["items_returned"],0)

class AMFITests(unittest.TestCase):
    def test_eight_columns_nav_and_stale_flags(self):
        d=amfi.from_file(ROOT/"examples/amfi_fixture_SYNTHETIC.txt",query="LARGE CAP",as_of="2026-10-21")
        self.assertEqual(d["schema_columns"],8)
        self.assertEqual(d["matching_schemes"],2)
        self.assertTrue(all(x["status"]=="AS_OF_DATE_ONLY" for x in d["returned_schemes"]))
        self.assertEqual(d["returned_schemes"][0]["nav_inr"],245.6)
        old=amfi.from_file(ROOT/"examples/amfi_fixture_SYNTHETIC.txt",query="OLD SERIES",as_of="2026-10-21")
        self.assertEqual(old["returned_schemes"][0]["status"],"STALE_VERIFY")

    def test_legacy_six_column_and_bad_data(self):
        good="Scheme Code;ISIN Div Payout/ ISIN Growth;ISIN Div Reinvestment;Scheme Name;Net Asset Value;Date\n10001;INF0000;-;FICTIONAL;13.51;20-Oct-2026\n"
        self.assertEqual(amfi.parse(good,as_of="2026-10-21")["schema_columns"],6)
        with self.assertRaises(ValueError):
            amfi.parse("Scheme Code;NAV\n5;1")
        with self.assertRaises(ValueError):
            amfi.parse(good,max_results=500)

    def test_no_fabricated_nav_for_invalid(self):
        content="Scheme Code;ISIN Div Payout/ ISIN Growth;ISIN Div Reinvestment;Scheme Name;Plan;Option;Net Asset Value;Date\n1;-;-;Invalid;Direct;Growth;NaN;20-Oct-2026\n2;-;-;Invalid;Direct;Growth;-;20-Oct-2026\n"
        x=amfi.parse(content,as_of="2026-10-21")
        self.assertEqual(x["matching_schemes"],0)
        self.assertEqual(x["skipped_rows"],2)

class PilotTests(unittest.TestCase):
    def test_not_advertised_without_human_review(self):
        r=pilot.from_file(ROOT/"examples/analyst_pilot_SYNTHETIC.json")
        self.assertEqual(r["tasks_tested"],2)
        self.assertEqual(r["pilot_status"],"NOT_REVIEWED_DO_NOT_ADVERTISE")
        self.assertEqual(r["approved_tasks"],0)
        self.assertEqual(r["time_saved_minutes_total"],27)
        self.assertEqual(r["tasks_with_positive_time_savings"],2)

    def test_human_review_does_not_allow_accuracy_regression(self):
        raw=json.loads((ROOT/"examples/analyst_pilot_SYNTHETIC.json").read_text())
        raw["reviewer_approved"]=True
        with self.assertRaises(ValueError):
            pilot.evaluate(raw)
        raw["data_class"]="DEIDENTIFIED_APPROVED"
        r=pilot.evaluate(raw)
        self.assertTrue(r["measured_runs"][0]["approved_useful_workflow"])
        self.assertFalse(r["measured_runs"][1]["approved_useful_workflow"])
        self.assertEqual(r["approved_tasks"],1)
        raw["reviewer_approved"]=1
        with self.assertRaises(ValueError):pilot.evaluate(raw)
        raw["reviewer_approved"]=False
        raw["tasks"][0]["fundtex"]["critical_errors"]=2
        raw["tasks"][0]["fundtex"]["unsupported_claims"]=0
        with self.assertRaises(ValueError):pilot.evaluate(raw)

class MCPAccessTests(unittest.TestCase):
    def test_requires_approved_data_dir_and_cannot_escape(self):
        with patch.dict("os.environ",{"FUNDTEX_APPROVED_DATA_DIR":""}):
            with self.assertRaises(ValueError):mcp_server.approved_file("foo.json")
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/"issuer.json").write_text("{}")
            with patch.dict("os.environ",{"FUNDTEX_APPROVED_DATA_DIR":tmp}):
                self.assertEqual(mcp_server.approved_file("issuer.json"),str((Path(tmp)/"issuer.json").resolve()))
                for name in ("/etc/passwd","../outside.json"):
                    with self.assertRaises((ValueError,FileNotFoundError)):mcp_server.approved_file(name)
                self.assertIn("catalog",mcp_server.tools_logic())
                r=mcp_server.tools_logic()["mission"]("Bank earnings","DEEP")
                self.assertTrue(r["plan_only"])

class CLITests(unittest.TestCase):
    def test_four_new_commands(self):
        cases=[
            ["sources"],
            ["regulatory","--file",str(ROOT/"examples/regulatory_fixture_SYNTHETIC.xml")],
            ["amfi","--file",str(ROOT/"examples/amfi_fixture_SYNTHETIC.txt"),"--query","DEMO","--as-of","2026-10-21"],
            ["pilot","--inputs",str(ROOT/"examples/analyst_pilot_SYNTHETIC.json")]
        ]
        for args in cases:
            p=subprocess.run([sys.executable,"-m","fundtex_india.cli"]+args,cwd=ROOT,text=True,capture_output=True)
            self.assertEqual(p.returncode,0,(args,p.stderr))
            self.assertIsInstance(json.loads(p.stdout),dict)

if __name__=="__main__":
    unittest.main()
