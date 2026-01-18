
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(PROJECT_ROOT, 'data')
MODEL_PATH = os.path.join(PROJECT_ROOT, 'models')

DATA_FILE = os.path.join(DATA_PATH, 'sol_1d_data_2020_to_2025.csv')
FEATURES_FILE = os.path.join(DATA_PATH, 'features_prepared.csv')

RF_MODEL_FILE = os.path.join(MODEL_PATH, 'rf_model.pkl')
LSTM_MODEL_FILE = os.path.join(MODEL_PATH, 'lstm_model.h5')
SCALER_FILE = os.path.join(MODEL_PATH, 'scaler.pkl')

DEFAULT_FORECAST_DAYS = 14
MIN_FORECAST_DAYS = 1
MAX_FORECAST_DAYS = 365

RF_HYPERPARAMS = {
    'n_estimators': 100,
    'max_depth': 15,
    'random_state': 42
}

LSTM_HYPERPARAMS = {
    'units_1': 64,
    'units_2': 32,
    'dropout': 0.2,
    'epochs': 50,
    'batch_size': 32
}