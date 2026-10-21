"""Official-format local UDiFF ingestion and prequential forecast contracts."""
import csv
import datetime as dt
import json
import math
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from fundtex_india.importers import import_googlefinance, import_nse_udiff, export_prices
from fundtex_india.forecast import prequential

ROOT=Path(__file__).resolve().parents[1]

def _path(root, name):
    return root/name

class MarketImporterTest(unittest.TestCase):
    def test_googlefinance_archive_parsing(self):
        with tempfile.TemporaryDirectory() as d:
            source=_path(Path(d),"thirdparty.csv")
            source.write_text("Date,Open,High,Low,Close,Volume\n"
                              "1/2/2020 15:30:00,100,110,98,104,123\n"
                              "1/3/2020 15:30:00,104,111,99,105,456\n")
            data=import_googlefinance(source,"INFY.NS")
            self.assertEqual(data["rows"][0]["date"],"2020-01-02")
            self.assertEqual(data["rows"][1]["close"],105)
            self.assertEqual(data["rows"][0]["volume"],123)
            self.assertTrue(data["source_kind"].startswith("THIRD_PARTY"))
            out=_path(Path(d),"export.csv")
            manifest=export_prices(data,out)
            self.assertEqual(manifest["rows_written"],2)
            self.assertEqual(manifest["quality"],"SOURCE_FORMAT_PARSED_NOT_AUTHENTICATED")
            self.assertTrue(out.with_suffix(".csv.manifest.json").is_file())
            with self.assertRaises(FileExistsError): export_prices(data,out)

    def test_nse_udiff_two_archives_and_identity(self):
        with tempfile.TemporaryDirectory() as d:
            files=[]
            for day,close in [("2026-10-01",1400),("2026-10-02",1410)]:
                p=_path(Path(d),day+".zip")
                with zipfile.ZipFile(p,"w") as z:
                    z.writestr("cm.csv","TradDt,TckrSymb,SctySrs,ClsPric,ISIN,TtlTradgVol\n"
                              f"{day},INFY,EQ,{close},INE009A01021,1000\n"
                              f"{day},INFY,BE,1,INE009A01021,100\n"
                              f"{day},TCS,EQ,3000,INE467B01029,3000\n")
                files.append(p)
            data=import_nse_udiff(files,"INFY.NS")
            self.assertEqual(data["isin"],"INE009A01021")
            self.assertEqual([r["close"] for r in data["rows"]],[1400,1410])
            self.assertEqual(data["source_kind"],"USER_PROVIDED_NSE_UDIFF_EXCHANGE_REPORT_UNADJUSTED")
            with self.assertRaises(ValueError): import_nse_udiff(files,"INFY.BO")
            with self.assertRaises(ValueError): import_nse_udiff(files+files[:1],"INFY.NS")

class PrequentialForecastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=[]
        p=100.0
        start=dt.date(2020,1,1)
        for i in range(550):
            p *= 1.0005+0.007*math.sin(i*.33)+0.002*math.cos(i*.13)
            cls.rows.append({"date":(start+dt.timedelta(days=i)).isoformat(),"close":p})

    def test_scores_and_abstention(self):
        x=prequential(self.rows,window=252,seed=42)
        self.assertEqual(x["out_of_sample_days"],297)
        self.assertEqual(x,prequential(self.rows,window=252,seed=42))
        self.assertTrue(0<=x["empirical_interval_coverage"]<=1)
        self.assertFalse(x["gates"]["license_corporate_actions_and_pit_certified"])
        self.assertFalse(x["current_research_forecast"]["is_a_calibrated_probability"])

    def test_no_lookahead_audit_prefix(self):
        a=prequential(self.rows,window=252)
        modified=[dict(r) for r in self.rows]
        modified[-1]["close"]*=1.2
        b=prequential(modified,window=252)
        self.assertEqual(a["audit_first_last"][:5],b["audit_first_last"][:5])
        self.assertNotEqual(a["brier"],b["brier"])

    def test_short_sample_rejected(self):
        with self.assertRaises(ValueError): prequential(self.rows[:220],window=252)
        with self.assertRaises(ValueError): prequential(self.rows,window=80)

    def test_cli_forecast_json(self):
        with tempfile.TemporaryDirectory() as d:
            csvpath=Path(d)/"sample.csv"
            with csvpath.open("w",newline="") as f:
                writer=csv.DictWriter(f,fieldnames=["date","symbol","close"])
                writer.writeheader()
                for row in self.rows:
                    writer.writerow({**row,"symbol":"INFY.NS"})
            result=subprocess.run([sys.executable,"-m","fundtex_india.cli","forecast",
                "--csv",str(csvpath),"--symbol","INFY.NS"],cwd=ROOT,
                capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            data=json.loads(result.stdout)
            self.assertEqual(data["symbol"],"INFY.NS")
            self.assertIn("brier_skill_vs_constant_half",data)
            self.assertEqual(data["data_quality"],"USER_SUPPLIED_UNVERIFIED")
            self.assertTrue(data["research_only"])

if __name__=="__main__":
    unittest.main()
