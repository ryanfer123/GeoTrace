import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs,urlsplit

from geotrace.core import SNAPSHOT,available,fetch_image,image_url,markdown_report,validate_investigation
CATALOG=json.loads(SNAPSHOT.read_text())
SPEC={'name':'Aral Sea','notes':'Compare shorelines visually.','bounds':[56,42,62,47],
      'layer':'MODIS_Terra_CorrectedReflectance_TrueColor','before':'2001-08-01','after':'2023-08-01'}

class CoreTests(unittest.TestCase):
    def test_date_gaps_are_rejected(self):
        layer=next(x for x in CATALOG['layers'] if x['id']==SPEC['layer'])
        self.assertTrue(available('2022-10-10',layer['intervals']))
        self.assertFalse(available('2022-10-15',layer['intervals']))
        self.assertTrue(available('2022-10-23',layer['intervals']))

    def test_dates_require_hyphenated_iso_format(self):
        for day in ('20230801',None,True,'not-a-date'):
            with self.subTest(day=day),self.assertRaises(ValueError):available(day,['2023-01-01/2023-12-31/P1D'])

    def test_wms_longitude_latitude_order_and_explicit_time(self):
        url=image_url(SPEC,SPEC['before']);query=parse_qs(urlsplit(url).query)
        self.assertEqual(query['BBOX'],['56,42,62,47'])
        self.assertEqual(query['TIME'],['2001-08-01'])
        self.assertEqual(query['VERSION'],['1.1.1'])
        self.assertEqual(query['SRS'],['EPSG:4326'])
        self.assertEqual(query['HEIGHT'],['1000'])

    def test_validation_rejects_invalid_geometry_dates_and_layer(self):
        for field,value in [('bounds',[62,42,56,47]),('bounds',[0,0,float('nan'),4]),('bounds',[0,0,True,4]),('bounds',[0,-90,10,10]),('before','2022-10-15'),('after','2001-07-01'),('layer','untrusted'),('notes',{}),('name','')]:
            data=copy.deepcopy(SPEC);data[field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):validate_investigation(data,CATALOG)

    def test_validated_spec_does_not_retain_extra_provenance(self):
        data=dict(SPEC,sources={'invented':True})
        self.assertNotIn('sources',validate_investigation(data,CATALOG))

    def test_download_checks_mime_and_jpeg_signature(self):
        with tempfile.TemporaryDirectory() as directory:
            for response in [(b'xml error','text/xml'),(b'not jpeg','image/jpeg')]:
                with patch('geotrace.core.fetch_bytes',return_value=response),self.assertRaises(ValueError):
                    fetch_image(image_url(SPEC,'2020-01-01'),directory)

    def test_cache_hash_provenance_and_reuse(self):
        data=b'\xff\xd8verified test jpeg bytes'
        with tempfile.TemporaryDirectory() as directory,patch('geotrace.core.fetch_bytes',return_value=(data,'image/jpeg')) as fetch:
            first=fetch_image(image_url(SPEC,'2020-01-01'),directory)
            second=fetch_image(image_url(SPEC,'2020-01-01'),directory)
            self.assertEqual(first,second);self.assertEqual(fetch.call_count,1)
            self.assertEqual(first['sha256'],hashlib.sha256(data).hexdigest())

    def test_report_preserves_notes_and_limits(self):
        source={'url':'https://example.test','sha256':'abc','fetched_at':'today','bytes':3}
        record={'spec':SPEC,'created':'today','catalog_verified':'2026-10-24','sources':{'before':source,'after':source}}
        report=markdown_report(record)
        self.assertIn(SPEC['notes'],report);self.assertIn('No NDVI',report);self.assertIn('SHA256: abc',report)
