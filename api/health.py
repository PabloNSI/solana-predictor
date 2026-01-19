from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = json.dumps({
            "status": "healthy",
            "service": "solana-predictor-api",
            "timestamp": datetime.now().isoformat()
        })
        self.wfile.write(response.encode())