from http.server import BaseHTTPRequestHandler
import json
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Cargar modelo
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../models/rf_model_best.pkl')

try:
    with open(MODEL_PATH, 'rb') as f:
        MODEL = pickle.load(f)
    MODEL_LOADED = True
except Exception as e:
    MODEL_LOADED = False
    print(f"Error loading model: {e}")

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/api/health' or self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({
                "status": "healthy" if MODEL_LOADED else "unhealthy",
                "model_loaded": MODEL_LOADED,
                "timestamp": datetime.now().isoformat()
            })
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            if not MODEL_LOADED:
                self.send_response(503)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = json.dumps({"error": "Model not loaded"})
                self.wfile.write(response.encode())
                return
            
            # Ejemplo simple de predicción
            features = pd.DataFrame([[
                data.get('close', 150.0),
                data.get('volume', 2500000),
                data.get('rsi', 50.0)
            ]])
            
            prediction = MODEL.predict(features)[0]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps({
                "success": True,
                "prediction": float(prediction),
                "timestamp": datetime.now().isoformat()
            })
            self.wfile.write(response.encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({"error": str(e)})
            self.wfile.write(response.encode())