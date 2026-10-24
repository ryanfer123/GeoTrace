"""Single-user loopback server and SQLite investigation notebook."""
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
from urllib.parse import urlsplit
import uuid

from . import __version__
from .core import SNAPSHOT,fetch_image,image_url,markdown_report,now,refresh_catalog,validate_investigation

WEB=Path(__file__).parent/'web'


def connect(database):
    db=sqlite3.connect(database)
    db.execute('CREATE TABLE IF NOT EXISTS investigations (id TEXT PRIMARY KEY, created TEXT, body TEXT)')
    return db


class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,database,cache,**kwargs):
        self.database,self.cache=database,Path(cache)
        super().__init__(*args,directory=str(WEB),**kwargs)

    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; frame-ancestors 'none'")
        super().end_headers()

    def send_data(self,data,kind='application/json; charset=utf-8',status=200,filename=None):
        if not isinstance(data,bytes): data=json.dumps(data,ensure_ascii=False,allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type',kind)
        self.send_header('Content-Length',str(len(data)))
        if filename:self.send_header('Content-Disposition',f'attachment; filename="{filename}"')
        self.end_headers();self.wfile.write(data)

    def valid_host(self):
        if self.headers.get('Host') not in {f'localhost:{self.server.server_port}',f'127.0.0.1:{self.server.server_port}'}:
            self.send_data({'error':'Only localhost requests are accepted.'},status=403);return False
        return True

    def do_GET(self):
        if not self.valid_host():return
        path=urlsplit(self.path).path
        if path=='/api/state':
            with connect(self.database) as db:
                records=[json.loads(row[0]) for row in db.execute('SELECT body FROM investigations ORDER BY created DESC')]
            self.send_data({'catalog':self.server.catalog,'investigations':records,'version':__version__})
        elif path.startswith('/api/export/'):
            identifier=path.removeprefix('/api/export/')
            with connect(self.database) as db:row=db.execute('SELECT body FROM investigations WHERE id=?',(identifier,)).fetchone()
            if not row:self.send_data({'error':'Investigation not found.'},status=404);return
            record=json.loads(row[0])
            if urlsplit(self.path).query=='format=md':
                self.send_data(markdown_report(record).encode(),'text/markdown; charset=utf-8',filename=f'geotrace-{identifier}.md')
            else:self.send_data(record,filename=f'geotrace-{identifier}.json')
        elif path.startswith('/api/images/'):
            key=path.removeprefix('/api/images/')
            if len(key)!=64 or any(c not in '0123456789abcdef' for c in key):
                self.send_data({'error':'Invalid image key.'},status=400);return
            file=self.cache/(key+'.jpg')
            if not file.exists():self.send_data({'error':'Cached image not found. Reload the comparison to fetch it.'},status=404);return
            self.send_data(file.read_bytes(),'image/jpeg')
        elif path in ('/','/app.js','/motion.js','/style.css','/favicon.svg') or (path.startswith('/vendor/') and Path(path).name in {p.name for p in (WEB/'vendor').iterdir()}):
            super().do_GET()
        else:self.send_data({'error':'Not found.'},status=404)

    def do_POST(self):
        if not self.valid_host():return
        origin=self.headers.get('Origin')
        if origin and origin!=f'http://{self.headers.get("Host")}':
            self.send_data({'error':'Cross-origin writes are not allowed.'},status=403);return
        try:
            if self.headers.get('Content-Type','').split(';')[0]!='application/json':raise ValueError('Send application/json.')
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=32768:raise ValueError('Request exceeds 32 KiB or is empty.')
            data=json.loads(self.rfile.read(length));path=urlsplit(self.path).path
            if path=='/api/catalog/refresh':
                self.server.catalog=refresh_catalog();self.send_data(self.server.catalog);return
            spec=validate_investigation(data,self.server.catalog)
            if path=='/api/compare':
                with ThreadPoolExecutor(max_workers=2) as pool:
                    futures={label:pool.submit(fetch_image,image_url(spec,spec[label]),self.cache) for label in ('before','after')}
                    sources={label:future.result() for label,future in futures.items()}
                self.send_data({'spec':spec,'sources':sources,'catalog_verified':self.server.catalog['verified']})
            elif path=='/api/investigations':
                # Fetch/reuse exact sources on save; client-supplied provenance is ignored.
                sources={label:fetch_image(image_url(spec,spec[label]),self.cache) for label in ('before','after')}
                record={'id':str(uuid.uuid4()),'created':now(),'version':__version__,'spec':spec,'sources':sources,'catalog_verified':self.server.catalog['verified']}
                with connect(self.database) as db:db.execute('INSERT INTO investigations VALUES (?,?,?)',(record['id'],record['created'],json.dumps(record,ensure_ascii=False)))
                self.send_data(record,status=201)
            else:self.send_data({'error':'Not found.'},status=404)
        except (ValueError,TypeError) as error:self.send_data({'error':str(error)},status=400)
        except Exception as error:
            self.log_error('Source request failed: %s',error)
            self.send_data({'error':'The satellite source could not be loaded. Check connectivity, choose another advertised date, or try again.'},status=502)


def make_server(port=8767,database='geotrace.sqlite3',cache='.geotrace-cache'):
    server=ThreadingHTTPServer(('127.0.0.1',port),partial(Handler,database=str(database),cache=str(cache)))
    server.catalog=json.loads(SNAPSHOT.read_text())
    return server
