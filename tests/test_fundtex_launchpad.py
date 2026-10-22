"""Optional start-page output safety and markup checks."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fundtex_india.launchpad import create, render

class LaunchpadTests(unittest.TestCase):
    def test_offline_render_and_user_approval(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"welcome.html"
            with patch("webbrowser.open") as opener:
                result=create(str(path),open_browser=False,installed_skills=True)
                opener.assert_not_called()
                self.assertFalse(result["browser_open_requested"])
                markup=path.read_text()
                self.assertIn("FUNDTEX",markup)
                self.assertIn("No orders",markup)
                self.assertNotIn("<script",markup)
                self.assertNotIn("api_key",markup)
                with self.assertRaisesRegex(ValueError,"overwrite"):create(str(path))
    def test_real_browser_opt_in_only(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"opening.html"
            with patch("webbrowser.open") as opener:
                result=create(str(path),open_browser=True)
                self.assertTrue(result["browser_open_requested"])
                opener.assert_called_once()
    def test_bad_file_and_html_injection_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,".html"):create(str(Path(d)/"no"))
            html=render(installed_skills=False,source_status='<script>alert("1")</script>')
            self.assertIn("&lt;script&gt;",html)
            self.assertNotIn('<script>alert(',html)

if __name__=="__main__":
    unittest.main()
