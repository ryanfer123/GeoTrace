import argparse
from .server import make_server

parser=argparse.ArgumentParser(description='Local satellite-image investigation desk')
parser.add_argument('--port',type=int,default=8767)
parser.add_argument('--database',default='geotrace.sqlite3')
parser.add_argument('--cache',default='.geotrace-cache')
args=parser.parse_args()
server=make_server(args.port,args.database,args.cache)
print(f'GeoTrace: http://127.0.0.1:{server.server_port}',flush=True)
try:server.serve_forever()
except KeyboardInterrupt:pass
finally:server.server_close()
