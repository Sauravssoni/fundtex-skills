"""Fundtex Analyst Studio v0.9 deterministic chart/pack and error-path tests."""
import json
import sys
import tempfile
from pathlib import Path
import unittest
from fundtex_india.chart_studio import prices, chart_spec, annotations_from_file, svg, rsi
from fundtex_india.interactive_studio import document
from fundtex_india.graphics_studio import pie, bars, heatmap, waterfall, histogram
from fundtex_india.pack_studio import build_pack

ROOT=Path(__file__).resolve().parents[1]
CSV=ROOT/"examples/india_prices.csv"

class StudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=prices(CSV,"RELIANCE.NS")
        cls.spec=chart_spec(cls.data)

    def test_close_is_not_fake_ohlc(self):
        self.assertEqual(self.spec["price_type"],"CLOSE_LINE")
        self.assertTrue(self.spec["no_live_feed"])
        self.assertEqual(self.spec["data_quality"],"SYNTHETIC_FIXTURE")
        self.assertEqual(len(self.spec["source_sha256"]),64)

    def test_flat_series_rsi_is_neutral_not_overbought(self):
        self.assertEqual(rsi([100.0] * 40, 14)[-1], 50.0)
        self.assertEqual(rsi([float(i + 100) for i in range(40)], 14)[-1], 100.0)
        self.assertEqual(rsi([float(140 - i) for i in range(40)], 14)[-1], 0.0)

    def test_svg_and_html_work_offline(self):
        graphic=svg(self.spec)
        self.assertIn("<svg",graphic)
        self.assertIn("polyline",graphic)
        self.assertNotIn("<script>",graphic)
        page=document(self.spec)
        self.assertIn("Export PNG screenshot",page)
        self.assertIn("Draw level",page)

    def test_png_fallback_when_pillow_is_available(self):
        try:
            import PIL
        except ImportError:
            self.skipTest("Optional Pillow absent")
        from fundtex_india.raster_studio import render
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/"price-chart.png"
            render(self.spec,target)
            self.assertEqual(target.read_bytes()[:8],b"\x89PNG\r\n\x1a\n")
            with self.assertRaises(ValueError):render(self.spec,target)

    def test_no_malicious_annotations(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"notes.json"
            f.write_text('[{"type":"zone","high":3,"low":5,"label":"bad"}]')
            with self.assertRaises(ValueError):annotations_from_file(str(f))

    def test_pie_bars_heatmap_waterfall_histogram(self):
        self.assertIn("<svg",pie({"Banking":.4,"IT":.6}))
        self.assertIn("<svg",bars({"A":1,"B":-2}))
        self.assertIn("<svg",heatmap({"A":{"A":1,"B":.3},"B":{"A":.3,"B":1}}))
        self.assertIn("<svg",waterfall({"EV":100,"Net Debt":-24}))
        self.assertIn("<svg",histogram([float(i)/10000 for i in range(50)]))

    def test_analyst_pack_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"pack"
            report=build_pack(CSV,"RELIANCE.NS",out)
            self.assertTrue((out/"interactive-chart.html").is_file())
            self.assertTrue((out/"price-chart.svg").is_file())
            self.assertTrue((out/"analyst-memo.md").is_file())
            self.assertTrue((out/"manifest.json").is_file())
            self.assertFalse(report["live_exchange_quotes"])
            self.assertEqual(report["data_quality"],"SYNTHETIC_FIXTURE")
            self.assertIn("omitted_optional_outputs",report)
            with self.assertRaises(ValueError):build_pack(CSV,"RELIANCE.NS",out)

    def test_close_only_report_round_trip_does_not_fake_candles(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/"pack"
            build_pack(CSV,"RELIANCE.NS",output)
            exported=prices(output/"price-history.csv","RELIANCE.NS")
            self.assertFalse(exported["ohlc"])
            self.assertEqual(exported["rows"][0]["volume"],None)
            self.assertNotIn("open",exported["rows"][0])
            # Explicitly fail where genuine next-open executions are required.
            from fundtex_india.strategy_lab import run
            with self.assertRaisesRegex(ValueError,"Genuine open"):
                run(output/"price-history.csv","RELIANCE.NS",
                    {"candidates":[{"name":"sma_cross","fast":10,"slow":50}]})

    def test_partial_or_mixed_ohlc_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/"bad-ohlc.csv"
            start="2025-01-01"
            file.write_text("date,open,high,low,close\n"
                +"\n".join(f"2025-01-{i:02d},100,102,,101" for i in range(1,20))+"\n")
            with self.assertRaisesRegex(ValueError,"Partial OHLC"):
                prices(file,"DEMO.NS")
            file.write_text("date,open,high,low,close\n"
                +"2025-01-01,,,,101\n"
                +"2025-01-02,100,102,99,101\n"
                +"".join(f"2025-01-{i:02d},,,,101\n" for i in range(3,20)))
            with self.assertRaisesRegex(ValueError,"mix close-only"):
                prices(file,"DEMO.NS")

    def test_bad_csv_or_future_data_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"bad.csv"
            f.write_text("date,close\n"+("2099-01-01,120\n"*20))
            with self.assertRaises(ValueError):prices(f,"DEMO.NS")
            f.write_text("date,open,high,low,close\n"+("2025-01-01,100,90,120,105\n"*20))
            with self.assertRaises(ValueError):prices(f,"DEMO.NS")

if __name__=="__main__":
    unittest.main()
