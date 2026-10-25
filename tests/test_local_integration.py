"""Local routes and browser-safe cloud configuration remain separate from hosting."""
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from geotrace.server import make_server


class LocalIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.server = make_server(0, root / 'db.sqlite3', root / 'cache')
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def request(self, path):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port)
        connection.request('GET', path)
        response = connection.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        connection.close()
        return result

    def test_homepage_and_workspace_are_distinct_working_routes(self):
        home = self.request('/')[2].decode()
        self.assertIn('See a place change over time.', home)
        self.assertIn('/workspace', home)
        for path in ('/workspace', '/workspace/', '/workspace.html'):
            status, _, content = self.request(path)
            self.assertEqual(status, 200)
            self.assertIn('investigation-form', content.decode())
            self.assertIn('/cloud.js', content.decode())
            self.assertNotIn('src="/hosted.js"', content.decode())

    def test_homepage_cloud_and_image_assets_are_served(self):
        for path in ('/home.css', '/home.js', '/cloud.css', '/cloud.js',
                     '/home-assets/aral-earlier.jpg', '/home-assets/aral-later.jpg',
                     '/home-assets/provenance.json'):
            self.assertEqual(self.request(path)[0], 200)
        self.assertEqual(self.request('/cloud.config.json')[0], 404)
        self.assertEqual(self.request('/home-assets/../server.py')[0], 404)

    def test_public_cloud_config_marks_local_mode(self):
        config = {'configured': True, 'url': 'https://example.supabase.co',
                  'publishableKey': 'sb_publishable_example', 'table': 'geotrace_cloud_workspaces'}
        with patch('geotrace.server.cloud_config', return_value=config):
            status, headers, body = self.request('/api/cloud/config')
        self.assertEqual(status, 200)
        self.assertFalse(json.loads(body)['hosted'])
        self.assertEqual(json.loads(body)['publishableKey'], 'sb_publishable_example')
        self.assertEqual(headers['Cache-Control'], 'no-store')

    def test_csp_allows_only_the_configured_supabase_origin(self):
        with patch('geotrace.server.cloud_config', return_value={
            'configured': True, 'url': 'https://example.supabase.co',
        }):
            policy = self.request('/workspace')[1]['Content-Security-Policy']
        self.assertIn("connect-src 'self' https://example.supabase.co", policy)
        self.assertNotIn('*.supabase.co', policy)
        self.assertNotIn("'unsafe-inline'", policy)
        with patch('geotrace.server.cloud_config', return_value={'configured': False}):
            policy = self.request('/')[1]['Content-Security-Policy']
        self.assertIn("connect-src 'self';", policy)
        self.assertNotIn('https://example.supabase.co', policy)
