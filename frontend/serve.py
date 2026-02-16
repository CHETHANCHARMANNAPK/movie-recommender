"""
Simple HTTP server with no-cache headers.
Prevents browsers from serving stale CSS/JS files.
"""
import http.server
import functools

class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

if __name__ == '__main__':
    PORT = 5500
    handler = functools.partial(NoCacheHandler, directory='.')
    with http.server.HTTPServer(('', PORT), handler) as httpd:
        print(f'🌐 Frontend server running at http://localhost:{PORT}')
        print('📦 Cache-Control: no-store (no browser caching)')
        httpd.serve_forever()
