# api/predict.py
import json
import numpy as np
import pandas as pd
import joblib
from datetime import datetime

# Cargar el MEJOR modelo (Random Forest)
model = joblib.load('model.pkl')  # O 'rf_model_best.pkl'

def handler(request):
    """Maneja las solicitudes POST para predicciones"""
    
    # Obtener datos del cuerpo de la solicitud
    data = request.get_json()
    
    # Verificar que tenemos todos los features necesarios
    required_features = [
        'open', 'high', 'low', 'close', 'volume',
        'rsi', 'ma_7', 'ma_30', 'volume_ma', 'price_change'
    ]
    
    # Crear DataFrame con el mismo orden que durante el entrenamiento
    # AJUSTA ESTOS NOMBRES según tus features exactos
    features = pd.DataFrame([[
        data.get('open', 0),
        data.get('high', 0),
        data.get('low', 0),
        data.get('close', 0),
        data.get('volume', 0),
        data.get('rsi', 50),
        data.get('ma_7', 0),
        data.get('ma_30', 0),
        data.get('volume_ma', 0),
        data.get('price_change', 0)
    ]])
    
    # Hacer la predicción
    prediction = model.predict(features)[0]
    
    # Calcular intervalo de confianza (aproximado basado en tu error promedio)
    confidence_interval = {
        'lower': prediction * 0.93,  # -7% (basado en tu error promedio)
        'upper': prediction * 1.07   # +7%
    }
    
    # Preparar respuesta
    response = {
        'success': True,
        'prediction': float(prediction),
        'confidence_interval': confidence_interval,
        'model': {
            'name': 'Random Forest Regressor',
            'version': '1.0',
            'accuracy': {
                'avg_error_usd': 6.85,  # Tu error promedio
                'r2_score': float(rf_test_r2)  # Tu R²
            }
        },
        'timestamp': datetime.now().isoformat(),
        'note': 'Modelo entrenado con datos históricos de Solana'
    }
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response, indent=2)
    }


# Para probar localmente
if __name__ == "__main__":
    class MockRequest:
        def get_json(self):
            return {
                'open': 150.25,
                'high': 152.30,
                'low': 149.80,
                'close': 151.50,
                'volume': 2500000,
                'rsi': 65.3,
                'ma_7': 148.2,
                'ma_30': 145.8,
                'volume_ma': 2300000,
                'price_change': 0.02
            }
    
    result = handler(MockRequest())
    print("Prueba local exitosa:")
    print(json.dumps(json.loads(result['body']), indent=2))
    
    with open('model_metrics.json', 'r') as f:
        metrics = json.load(f)