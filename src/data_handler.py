
from turtle import st
import pandas as pd
import numpy as np
from pathlib import Path

@st.cache_data
def load_data(filepath):
    """
    Carga CSV histórico de Solana
    Cachea el resultado para eficiencia
    """
    df = pd.read_csv(filepath)
    df['Open time'] = pd.to_datetime(df['Open time'])
    df.sort_values('Open time', inplace=True)
    return df

def get_date_range(df, period=30, year=None):
    """
    Filtra datos por período (últimos N días) o año específico
    """
    if year is not None:
        return df[df['Open time'].dt.year == year].reset_index(drop=True)
    else:
        return df.tail(period).reset_index(drop=True)

def prepare_features(df, window=20):
    """
    Prepara features para modelos predictivos
    Calcula indicadores técnicos básicos
    """
    features_df = df[['Open time', 'Open', 'High', 'Low', 'Close', 'Volume']].copy()
    
    # Retornos
    features_df['Returns'] = features_df['Close'].pct_change()
    
    # Medias móviles
    features_df['SMA20'] = features_df['Close'].rolling(window=20).mean()
    features_df['SMA50'] = features_df['Close'].rolling(window=50).mean()
    
    # Volatilidad
    features_df['Volatility'] = features_df['Returns'].rolling(window=window).std()
    
    # High-Low Range
    features_df['HL_Range'] = (features_df['High'] - features_df['Low']) / features_df['Close']
    
    # Volume normalized
    features_df['Volume_MA'] = features_df['Volume'].rolling(window=20).mean()
    features_df['Volume_Norm'] = features_df['Volume'] / features_df['Volume_MA']
    
    return features_df.dropna()