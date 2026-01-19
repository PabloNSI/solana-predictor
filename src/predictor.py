import pickle
import tensorflow as tf
import numpy as np
from sklearn.preprocessing import StandardScaler

def load_models(model_dir):
    """
    Carga modelos pre-entrenados
    """
    try:
        rf_model = pickle.load(open(f'{model_dir}/rf_model.pkl', 'rb'))
        lstm_model = tf.keras.models.load_model(f'{model_dir}/lstm_model.h5')
        scaler = pickle.load(open(f'{model_dir}/scaler.pkl', 'rb'))
        return rf_model, lstm_model, scaler
    except FileNotFoundError:
        raise Exception("""
        Modelos no encontrados.
        Por favor, ejecuta primero los notebooks:
        - notebooks/01_EDA_Solana.ipynb
        - notebooks/02_Model_Training.ipynb
        """)

def predict_next_days(rf_model, lstm_model, scaler, features_df, days=14):
    """
    Genera predicciones para los próximos N días
    Usa Random Forest + LSTM ensemble
    """
    # Preparar features para predicción
    feature_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA20', 'SMA50', 'Volatility']
    X_features = features_df[feature_cols].values
    X_scaled = scaler.transform(X_features)
    
    # Inicializar predicciones
    rf_predictions = []
    lstm_predictions = []
    
    # Usar último dato como base
    last_features = X_scaled[-1:]
    
    # Simple: usar último valor como predicción constante
    # (En producción, haríamos auto-regresión)
    for i in range(days):
        rf_pred = rf_model.predict(last_features)[0]
        
        # LSTM requiere secuencia temporal (simplificado)
        lstm_input = np.reshape(X_scaled[-20:], (1, 20, len(feature_cols)))
        lstm_pred = lstm_model.predict(lstm_input)[0][0]
        
        rf_predictions.append(rf_pred)
        lstm_predictions.append(lstm_pred)
    
    # Ensemble
    rf_array = np.array(rf_predictions)
    lstm_array = np.array(lstm_predictions)
    ensemble = (rf_array * 0.4 + lstm_array * 0.6)
    
    # Desescalar predicciones
    rf_predictions_orig = scaler.inverse_transform(np.column_stack([
        np.zeros((len(rf_predictions), len(feature_cols)-1)),
        rf_predictions
    ]))[:, -1]
    
    return {
        'rf': rf_array,
        'lstm': lstm_array,
        'ensemble': ensemble,
        'confidence_lower': ensemble * 0.95,
        'confidence_upper': ensemble * 1.05
    }

