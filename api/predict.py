from http.server import BaseHTTPRequestHandler
import json
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ruta al modelo
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'rf_model_best.pkl')

# Variable global para cargar el modelo solo una vez
try:
    with open(MODEL_PATH, 'rb') as f:
        MODEL = pickle.load(f)
    MODEL_LOADED = True
    print("✅ Modelo cargado exitosamente")
except Exception as e:
    MODEL_LOADED = False
    print(f"❌ Error cargando modelo: {e}")
    MODEL = None

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
        if not MODEL_LOADED:
            self._send_response(503, {"error": "Modelo no cargado en el servidor"})
            return
        
        try:
            # 1. Leer y parsear JSON
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # 2. VERIFICAR que vienen TODAS las features necesarias
            required_features = ['close', 'volume', 'rsi', 'ma_7', 'ma_30']
            
            # Comprobar que están todas las features
            missing_features = [feat for feat in required_features if feat not in data]
            if missing_features:
                self._send_response(400, {
                    "error": "Faltan features requeridas",
                    "missing": missing_features,
                    "required": required_features
                })
                return
            
            # 3. Crear DataFrame con los valores que envía el usuario
            features = pd.DataFrame([[
                data['close'],
                data['volume'],
                data['ma_7'],
                data['ma_30']      
            ]], columns=required_features)
            
            # 4. Hacer predicción con datos REALES
            prediction = MODEL.predict(features)[0]
            
            # 5. Respuesta exitosa
            response = {
                "success": True,
                "prediction": float(prediction),
                "model": "Random Forest",
                "features_used": required_features,
                "timestamp": datetime.now().isoformat(),
                "note": "Predicción basada en datos reales proporcionados"
            }
            
            self._send_response(200, response)
            
        except json.JSONDecodeError:
            self._send_response(400, {"error": "JSON inválido en la petición"})
        except Exception as e:
            self._send_response(500, {"error": f"Error en el servidor: {str(e)}"})