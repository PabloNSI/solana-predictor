import numpy as np

def calculate_rsi(closes, period=14):
    """RSI - Relative Strength Index"""
    deltas = np.diff(closes)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    rsi = [None] * period
    
    for i in range(period, len(closes)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        if avg_loss == 0:
            rsi_value = 100 if avg_gain > 0 else 0
        else:
            rs = avg_gain / avg_loss
            rsi_value = 100 - (100 / (1 + rs))
        
        rsi.append(rsi_value)
    
    return np.array(rsi)

def calculate_sma(prices, period=20):
    """SMA - Simple Moving Average"""
    sma = [None] * (period - 1)
    for i in range(period - 1, len(prices)):
        sma.append(np.mean(prices[i-period+1:i+1]))
    return np.array(sma)

def calculate_ema(prices, period=20):
    """EMA - Exponential Moving Average"""
    multiplier = 2 / (period + 1)
    ema = [prices[0]]
    for i in range(1, len(prices)):
        ema.append(prices[i] * multiplier + ema[i-1] * (1 - multiplier))
    return np.array(ema)

def calculate_macd(closes):
    """MACD - Moving Average Convergence Divergence"""
    ema12 = calculate_ema(closes, 12)
    ema26 = calculate_ema(closes, 26)
    
    macd = ema12 - ema26
    signal = calculate_ema(macd, 9)
    histogram = macd - signal
    
    return {
        'macd': macd,
        'signal': signal,
        'histogram': histogram
    }

def calculate_volatility(closes, period=20):
    """Volatilidad histórica anualizada"""
    returns = np.diff(closes) / closes[:-1]
    std = np.std(returns[-period:])
    return std * np.sqrt(252)  # Anualizar