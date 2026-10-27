"""World Monitor MCP fixed-provider/entitlement tests; no external paid calls."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fundtex_india.world_monitor_client import read_only,URL
class Reply:
 status=200
 headers={"Content-Type":"application/json"}
 def __enter__(self):return self
 def __exit__(self,*args):pass
 def read(self,max_bytes):
    return json.dumps({"jsonrpc":"2.0","id":1,
        "result":{"content":[{"type":"text","text":"{\"sources\":[]}"}]}}).encode()
class Opener:
 def __init__(self):self.requests=[]
 def open(self,req,timeout=0):
    self.requests.append((req.full_url,req.method,req.data,req.get_header("X-worldmonitor-key")))
    return Reply()
class WorldMonitorSafetyTests(unittest.TestCase):
 def test_public_discovery_requires_only_explicit_output_file(self):
    op=Opener()
    with tempfile.TemporaryDirectory() as root:
       p=Path(root)/"sources.json"
       r=read_only(out=p,opener=op)
       self.assertEqual(r["provider_endpoint"],URL)
       self.assertTrue(p.is_file())
       self.assertFalse(r["request_used_account_key"])
       self.assertFalse(r["trading_enabled"])
       self.assertEqual(len(op.requests),1)
       self.assertEqual(json.loads(op.requests[0][2])["params"]["name"],"get_sources")
       with self.assertRaises(ValueError):read_only(out=p,opener=op)
 def test_explicit_consent_and_secret_only_from_env(self):
    op=Opener()
    with tempfile.TemporaryDirectory() as root:
      f=Path(root)/"risk.json"
      with self.assertRaisesRegex(ValueError,"user-approved"):
        read_only("get_country_risk",args={"country_code":"IN"},out=f,opener=op)
      with self.assertRaisesRegex(ValueError,"user-owned"):
        read_only("get_country_risk",args={"country_code":"IN"},out=f,approved=True,opener=op)
      with patch.dict("os.environ",{"WORLD_MONITOR_API_KEY":"wm_"+"a"*40}):
        r=read_only("get_country_risk",args={"country_code":"IN"},out=f,approved=True,opener=op)
      self.assertTrue(r["request_used_account_key"])
      self.assertNotIn("wm_"+"a"*40,json.dumps(r))
      self.assertEqual(len(op.requests),1)
 def test_reject_arbitrary_tool_and_unknown_fields_before_network(self):
    op=Opener()
    with tempfile.TemporaryDirectory() as root:
      p=Path(root)/"x.json"
      for tool,args in [("place_order",{}),("get_sources",{"url":"http://localhost"}),("get_country_risk",{"country_code":"../../"})]:
       with self.assertRaises(ValueError):read_only(tool,args=args,out=p,approved=True,opener=op)
      self.assertEqual(op.requests,[])
 def test_mcp_result_error_fail_closed_and_no_file(self):
    class Broken(Reply):
      def read(self,max_bytes):return b'{"jsonrpc":"2.0","id":1,"result":{"isError":true,"content":[]}}'
    class ErrorOpener:
      def open(self,req,timeout=0):return Broken()
    with tempfile.TemporaryDirectory() as root:
      f=Path(root)/"x.json"
      with self.assertRaisesRegex(ValueError,"unavailable"):
       read_only(out=f,opener=ErrorOpener())
      self.assertFalse(f.exists())
if __name__=="__main__":unittest.main()
