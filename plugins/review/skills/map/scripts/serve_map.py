#!/usr/bin/env python3
"""Serve one standalone architecture map on loopback until interrupted."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('html', type=Path)
    parser.add_argument('--port', type=int, default=0, help='Loopback port; default 0 allocates an available port')
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error('port must be between 0 and 65535')
    try:
        content = args.html.read_bytes()
    except OSError as error:
        parser.error(str(error))
    if not content.lstrip().lower().startswith(b'<!doctype html>'):
        parser.error('expected a standalone HTML document; render without --fragment')

    class MapHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.respond(include_body=True)

        def do_HEAD(self):
            self.respond(include_body=False)

        def respond(self, include_body):
            if self.path not in ('/', '/architecture-map.html'):
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            if include_body:
                self.wfile.write(content)

    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), MapHandler)
    except OSError as error:
        parser.error(str(error))
    server.daemon_threads = True
    print(f'http://127.0.0.1:{server.server_port}/architecture-map.html', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
