from socketserver import ThreadingMixIn
from http.server import SimpleHTTPRequestHandler, HTTPServer

CatchAllHandler_MetricFilename = None

class ThreadingServer(ThreadingMixIn, HTTPServer):
    pass

class CatchAllHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.protocol_version = 'HTTP/1.1'
        self.send_response(200, 'OK')
        self.send_header('Content-type', 'text')
        self.end_headers()
        with open(CatchAllHandler_MetricFilename, 'rb') as index:
            self.wfile.write(index.read())

class HttpServer():
    def __init__(self, config):
        global CatchAllHandler_MetricFilename

        CatchAllHandler_MetricFilename = config.metricfilename()
        self.serveraddr = ('', config.httpport())
        self.server = ThreadingServer(self.serveraddr, CatchAllHandler)

    def run(self):
        self.server.serve_forever()
