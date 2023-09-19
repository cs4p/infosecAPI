#!/usr/bin/env python3
import http.server
import socketserver


class MyHandler(http.server.SimpleHTTPRequestHandler):
    
    
    def send_200(self):
        json_response = '{"data": {}, "meta": {"pageCount": 1}}'
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(json_response.encode())
    
    def do_GET(self):
        self.send_200()
    
    def do_POST(self):
        self.send_200()
    
    def do_DELETE(self):
        self.send_200()


handler = MyHandler
server = socketserver.TCPServer(('localhost', 4001), handler)
server.serve_forever()
