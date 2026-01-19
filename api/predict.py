from http.server import BaseHTTPRequestHandler
import json
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar modelo y scaler
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'rf_model_best.pkl')
SCALER_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'scaler.pkl')

try:
    with open(MODEL_PATH, 'rb') as f:
        MODEL = pickle.load(f)
    with open(SCALER_PATH, 'rb') as f:
        SCALER = pickle.load(f)
    MODEL_LOADED = True
    print("Modelo y Scaler cargados exitosamente")
except Exception as e:
    MODEL_LOADED = False
    SCALER = None
    print(f"Error cargando modelo o scaler: {e}")
class handler(BaseHTTPRequestHandler):
    
    def _send_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Endpoint de salud (como /api/health)"""
        response = {
            "status": "healthy" if MODEL_LOADED else "unhealthy",
            "service": "Solana Predictor API",
            "model_loaded": MODEL_LOADED,
            "timestamp": datetime.now().isoformat()
        }
        self._send_response(200, response)
        def do_POST(self):
            """Endpoint de predicción - VERSIÓN CORRECTA"""
        if not MODEL_LOADED or SCALER is None:
            self._send_response(503, {"error": "Modelo o Scaler no cargado"})
            return
        
        try:
            # 1. Leer y parsear JSON
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # 2. USAR LAS FEATURES CORRECTAS DEL MODELO
            required_features = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA20', 'SMA50', 'Volatility']
            
            # Comprobar que están todas las features
            missing_features = [feat for feat in required_features if feat not in data]
            if missing_features:
                self._send_response(400, {
                    "error": "Faltan datos requeridos para el modelo",
                    "missing": missing_features,
                    "required": required_features
                })
                return
            
            # 3. Crear DataFrame en el ORDEN CORRECTO
            features = pd.DataFrame([[
                data['Open'],
                data['High'],
                data['Low'],
                data['Close'],
                data['Volume'],
                data['SMA20'],
                data['SMA50'],
                data['Volatility']
            ]], columns=required_features)
            
            # 4. ESCALAR los datos (IMPORTANTE)
            features_scaled = SCALER.transform(features)
            
            # 5. Hacer predicción
            prediction = MODEL.predict(features_scaled)[0]
            
            # 6. Respuesta exitosa
            response = {
                "success": True,
                "prediction": float(prediction),
                "model": "Random Forest",
                "features_used": required_features,
                "timestamp": datetime.now().isoformat()
            }
            
            self._send_response(200, response)
            
        except json.JSONDecodeError:
            self._send_response(400, {"error": "JSON inválido en la petición"})
        except Exception as e:
            self._send_response(500, {"error": f"Error en el servidor: {str(e)}"})