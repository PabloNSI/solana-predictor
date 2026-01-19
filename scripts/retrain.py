"""
Script para re-entrenamiento automático del modelo con nuevos datos.
Se ejecuta automáticamente cada 100 feedbacks o semanalmente.

USO:
    python scripts/retrain.py  # Re-entrena con datos actualizados
    python scripts/retrain.py --force  # Fuerza re-entrenamiento completo
"""

import pandas as pd
import numpy as np
import joblib
import json
import argparse
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Añadir ruta para importar módulos personalizados
sys.path.append(str(Path(__file__).parent.parent))

# Importaciones de scikit-learn
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler

# Importaciones propias (si existen)
try:
    from src.features.feature_engineering import calculate_technical_indicators
    from src.data.data_collector import fetch_latest_data
    CUSTOM_MODULES = True
except ImportError:
    CUSTOM_MODULES = False
    print("⚠️  Módulos personalizados no encontrados, usando funciones básicas")

# ==============================
# CONFIGURACIÓN
# ==============================
MODEL_DIR = Path("models")
DATA_DIR = Path("data")
FEEDBACK_DIR = Path("feedback")
BACKUP_DIR = Path("model_backups")
LOG_FILE = Path("logs/retraining.log")

# Crear directorios necesarios
for directory in [MODEL_DIR, DATA_DIR, FEEDBACK_DIR, BACKUP_DIR, Path("logs")]:
    directory.mkdir(exist_ok=True)

# ==============================
# FUNCIONES AUXILIARES
# ==============================
def load_feedback_data():
    """Carga feedback acumulado de usuarios"""
    feedback_files = list(FEEDBACK_DIR.glob("feedback_*.csv"))
    
    if not feedback_files:
        print("📭 No hay datos de feedback disponibles")
        return None
    
    feedback_dfs = []
    for file in feedback_files:
        try:
            df = pd.read_csv(file)
            feedback_dfs.append(df)
        except Exception as e:
            print(f"⚠️  Error cargando {file}: {e}")
    
    if feedback_dfs:
        return pd.concat(feedback_dfs, ignore_index=True)
    return None

def calculate_rsi(prices, period=14):
    """Calcula Relative Strength Index"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_technical_features(df):
    """Calcula indicadores técnicos básicos"""
    df = df.copy()
    
    # Precios y volumen
    df['price_change'] = df['close'].pct_change()
    df['log_return'] = np.log(df['close'] / df['close'].shift(1))
    
    # Medias móviles
    df['ma_7'] = df['close'].rolling(7).mean()
    df['ma_30'] = df['close'].rolling(30).mean()
    df['ma_50'] = df['close'].rolling(50).mean()
    
    # Volumen
    df['volume_ma'] = df['volume'].rolling(7).mean()
    df['volume_ratio'] = df['volume'] / df['volume_ma']
    
    # RSI
    df['rsi'] = calculate_rsi(df['close'])
    
    # Bandas de Bollinger
    df['bb_middle'] = df['close'].rolling(20).mean()
    df['bb_std'] = df['close'].rolling(20).std()
    df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
    df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
    
    # Target: Precio siguiente día (shift -1)
    df['target'] = df['close'].shift(-1)
    
    # Eliminar NaN
    df.dropna(inplace=True)
    
    return df

def load_training_data():
    """Carga y prepara datos para entrenamiento"""
    print("📂 Cargando datos de entrenamiento...")
    
    # Cargar datos históricos
    historical_path = DATA_DIR / "solana_historical.csv"
    if not historical_path.exists():
        print(f"❌ Archivo no encontrado: {historical_path}")
        return None
    
    df = pd.read_csv(historical_path)
    print(f"   📊 Datos históricos: {len(df)} registros")
    
    # Cargar datos de feedback si existen
    feedback_df = load_feedback_data()
    if feedback_df is not None and len(feedback_df) > 0:
        print(f"   📝 Datos de feedback: {len(feedback_df)} registros")
        # Combinar con datos históricos
        df = pd.concat([df, feedback_df], ignore_index=True)
    
    # Calcular features
    df = calculate_technical_features(df)
    
    # Definir features y target
    feature_cols = [
        'open', 'high', 'low', 'close', 'volume',
        'rsi', 'ma_7', 'ma_30', 'ma_50', 'volume_ma',
        'volume_ratio', 'price_change', 'log_return',
        'bb_upper', 'bb_middle', 'bb_lower'
    ]
    
    # Filtrar columnas existentes
    available_features = [col for col in feature_cols if col in df.columns]
    
    X = df[available_features]
    y = df['target']
    
    print(f"   🎯 Features disponibles: {len(available_features)}")
    print(f"   📈 Samples totales: {len(X)}")
    
    return X, y, available_features

def backup_current_model():
    """Crea backup del modelo actual"""
    current_model = MODEL_DIR / "model.pkl"
    current_scaler = MODEL_DIR / "scaler.pkl"
    current_metrics = MODEL_DIR / "model_metrics.json"
    
    if current_model.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup del modelo
        backup_model = BACKUP_DIR / f"model_backup_{timestamp}.pkl"
        current_model.rename(backup_model)
        print(f"✅ Backup creado: {backup_model}")
        
        # Backup del scaler si existe
        if current_scaler.exists():
            backup_scaler = BACKUP_DIR / f"scaler_backup_{timestamp}.pkl"
            current_scaler.rename(backup_scaler)
        
        # Backup de métricas si existe
        if current_metrics.exists():
            backup_metrics = BACKUP_DIR / f"metrics_backup_{timestamp}.json"
            current_metrics.rename(backup_metrics)
        
        return True
    return False

def train_new_model(X, y, features):
    """Entrena nuevo modelo con los datos actualizados"""
    print("🤖 Entrenando nuevo modelo...")
    
    # Split train/test (no shuffle para series temporales)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    print(f"   📚 Training samples: {len(X_train)}")
    print(f"   🧪 Testing samples: {len(X_test)}")
    
    # Normalización
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Hiperparámetros (puedes ajustarlos)
    rf_params = {
        'n_estimators': 150,  # Aumentado para más datos
        'max_depth': 20,
        'min_samples_split': 5,
        'min_samples_leaf': 2,
        'random_state': 42,
        'n_jobs': -1
    }
    
    # Entrenar modelo
    model = RandomForestRegressor(**rf_params)
    model.fit(X_train_scaled, y_train)
    
    # Evaluación
    y_pred_train = model.predict(X_train_scaled)
    y_pred_test = model.predict(X_test_scaled)
    
    # Métricas
    metrics = {
        'train': {
            'rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'mae': mean_absolute_error(y_train, y_pred_train),
            'r2': r2_score(y_train, y_pred_train)
        },
        'test': {
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
            'mae': mean_absolute_error(y_test, y_pred_test),
            'r2': r2_score(y_test, y_pred_test)
        },
        'feature_importance': dict(zip(features, model.feature_importances_))
    }
    
    print("📊 Métricas del nuevo modelo:")
    print(f"   Test RMSE: ${metrics['test']['rmse']:.2f}")
    print(f"   Test MAE: ${metrics['test']['mae']:.2f}")
    print(f"   Test R²: {metrics['test']['r2']:.4f}")
    
    return model, scaler, metrics

def save_model(model, scaler, metrics, features):
    """Guarda el nuevo modelo y sus componentes"""
    print("💾 Guardando nuevo modelo...")
    
    # Guardar modelo
    model_path = MODEL_DIR / "model.pkl"
    with open(model_path, 'wb') as f:
        joblib.dump(model, f)
    
    # Guardar scaler
    scaler_path = MODEL_DIR / "scaler.pkl"
    with open(scaler_path, 'wb') as f:
        joblib.dump(scaler, f)
    
    # Guardar métricas
    metrics_path = MODEL_DIR / "model_metrics.json"
    model_info = {
        'name': 'Random Forest Solana Predictor',
        'version': '2.0',
        'retrained_date': datetime.now().isoformat(),
        'features': features,
        'metrics': metrics,
        'hyperparameters': {
            'n_estimators': 150,
            'max_depth': 20,
            'min_samples_split': 5,
            'min_samples_leaf': 2
        },
        'training_stats': {
            'samples_total': metrics.get('samples_total', 0),
            'samples_new': metrics.get('samples_new', 0),
            'features_count': len(features)
        }
    }
    
    with open(metrics_path, 'w') as f:
        json.dump(model_info, f, indent=4)
    
    print(f"✅ Modelo guardado en: {model_path}")
    print(f"✅ Scaler guardado en: {scaler_path}")
    print(f"✅ Métricas guardadas en: {metrics_path}")
    
    return model_info

def log_retraining(info):
    """Registra el re-entrenamiento en log"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': 'model_retraining',
        'details': info
    }
    
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

# ==============================
# FUNCIÓN PRINCIPAL
# ==============================
def main(force_retrain=False):
    """Función principal de re-entrenamiento"""
    print("="*60)
    print("🚀 SOLANA PREDICTOR - RE-ENTRENAMIENTO AUTOMÁTICO")
    print("="*60)
    
    start_time = datetime.now()
    
    # Verificar si es necesario re-entrenar
    feedback_count = len(list(FEEDBACK_DIR.glob("feedback_*.csv")))
    
    if not force_retrain and feedback_count < 10:
        print(f"📭 Feedback insuficiente ({feedback_count}/10).")
        print("   Ejecuta con --force para re-entrenar de todos modos.")
        return
    
    try:
        # 1. Cargar datos
        result = load_training_data()
        if result is None:
            print("❌ No se pudieron cargar datos para entrenamiento")
            return
        
        X, y, features = result
        
        # 2. Crear backup del modelo actual
        backup_current_model()
        
        # 3. Entrenar nuevo modelo
        model, scaler, metrics = train_new_model(X, y, features)
        
        # 4. Guardar nuevo modelo
        model_info = save_model(model, scaler, metrics, features)
        
        # 5. Registrar en log
        log_retraining({
            'samples_total': len(X),
            'feedback_samples': feedback_count,
            'metrics': metrics['test'],
            'duration_seconds': (datetime.now() - start_time).total_seconds()
        })
        
        # 6. Limpiar feedback procesado
        if feedback_count > 0:
            for file in FEEDBACK_DIR.glob("feedback_*.csv"):
                archive_path = FEEDBACK_DIR / "archived" / file.name
                archive_path.parent.mkdir(exist_ok=True)
                file.rename(archive_path)
            print(f"🗑️  Feedback procesado archivado: {feedback_count} archivos")
        
        # 7. Resumen
        duration = datetime.now() - start_time
        print("\n" + "="*60)
        print("🎉 RE-ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
        print("="*60)
        print(f"⏱️  Duración: {duration.total_seconds():.1f} segundos")
        print(f"📊 Nuevas métricas (Test):")
        print(f"   • RMSE: ${metrics['test']['rmse']:.2f}")
        print(f"   • MAE: ${metrics['test']['mae']:.2f}")
        print(f"   • R²: {metrics['test']['r2']:.4f}")
        print(f"📈 Mejora esperada en predicciones: {feedback_count} nuevos samples")
        print(f"💾 Modelo actualizado en: {MODEL_DIR}/")
        
    except Exception as e:
        print(f"❌ Error durante el re-entrenamiento: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# ==============================
# PUNTO DE ENTRADA
# ==============================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Re-entrena el modelo de predicción de Solana')
    parser.add_argument('--force', action='store_true', 
                       help='Forzar re-entrenamiento incluso con poco feedback')
    
    args = parser.parse_args()
    main(force_retrain=args.force)