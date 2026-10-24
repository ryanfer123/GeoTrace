import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from test_core import SPEC
from geotrace.server import make_server

class APITests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();root=Path(self.tmp.name)
        self.server=make_server(0,root/'db.sqlite3',root/'cache')
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.tmp.cleanup()
    def request(self,path,data=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port)
        c.request('POST' if data is not None else 'GET',path,json.dumps(data) if data is not None else None,headers or {'Content-Type':'application/json'})
        r=c.getresponse();result=(r.status,dict(r.getheaders()),r.read());c.close();return result
    def test_real_bundled_reference_compare_save_and_export(self):
        status,_,body=self.request('/api/compare',SPEC);self.assertEqual(status,200)
        comparison=json.loads(body)
        self.assertEqual(set(comparison['sources']),{'before','after'})
        source=comparison['sources']['before']
        status,_,image=self.request('/api/images/'+source['key']);self.assertEqual(status,200);self.assertTrue(image.startswith(b'\xff\xd8'))
        status,_,body=self.request('/api/investigations',SPEC);self.assertEqual(status,201);record=json.loads(body)
        self.assertEqual(len(json.loads(self.request('/api/state')[2])['investigations']),1)
        status,headers,body=self.request('/api/export/'+record['id']);self.assertEqual(status,200);self.assertIn('attachment',headers['Content-Disposition'])
        self.assertEqual(json.loads(body),record)
        self.assertIn('No NDVI',self.request('/api/export/'+record['id']+'?format=md')[2].decode())
    def test_invalid_geometry_not_saved(self):
        self.assertEqual(self.request('/api/investigations',dict(SPEC,bounds=[0,0,0,1]))[0],400)
        self.assertEqual(json.loads(self.request('/api/state')[2])['investigations'],[])
    def test_source_failure_has_clear_gateway_response(self):
        with patch('geotrace.server.fetch_image',side_effect=TimeoutError('offline')):
            self.assertEqual(self.request('/api/compare',SPEC)[0],502)
    def test_foreign_origin_and_host_rejected(self):
        self.assertEqual(self.request('/api/compare',SPEC,{'Content-Type':'application/json','Origin':'https://example.com'})[0],403)
        self.assertEqual(self.request('/api/state',headers={'Host':'example.com'})[0],403)
    def test_missing_report_and_bad_cache_path(self):
        self.assertEqual(self.request('/api/export/missing')[0],404)
        self.assertEqual(self.request('/api/images/../../server.py')[0],400)
        self.assertEqual(self.request('/api/images/'+'0'*64)[0],404)
    def test_refresh_metadata_uses_server_catalog(self):
        updated=dict(self.server.catalog,verified='2026-10-25')
        with patch('geotrace.server.refresh_catalog',return_value=updated):
            self.assertEqual(self.request('/api/catalog/refresh',{})[0],200)
        self.assertEqual(json.loads(self.request('/api/state')[2])['catalog']['verified'],'2026-10-25')
