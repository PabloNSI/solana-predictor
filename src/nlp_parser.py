
import re

def parse_command(user_input):
    """
    Parsea comando del usuario en español
    
    Retorna:
    {
        'metric': 'price',  # price, volume, rsi, sma, macd, volatility
        'type': 'prediction',  # prediction, indicator, historical
        'period': 14,  # días o año
        'forecast_days': 14,
        'visualization': 'line',
        'confidence': 0.85
    }
    """
    text = user_input.lower().strip()
    
    result = {
        'metric': None,
        'type': 'historical',
        'period': 30,
        'forecast_days': 14,
        'visualization': 'line',
        'confidence': 0.3
    }
    
    # Detectar tipo de solicitud
    if any(word in text for word in ['próximo', 'futuro', 'predice', 'va a', 'será', 'predicción']):
        result['type'] = 'prediction'
        result['confidence'] = 0.7
    elif any(word in text for word in ['histórico', 'pasado', 'era', 'fue']):
        result['type'] = 'historical'
        result['confidence'] = 0.7
    elif any(word in text for word in ['rsi', 'sma', 'macd', 'bollinger', 'volatilidad', 'atr']):
        result['type'] = 'indicator'
        result['confidence'] = 0.8
    
    # Detectar métrica
    if 'precio' in text or 'cierre' in text or 'close' in text or 'costo' in text:
        result['metric'] = 'price'
        result['confidence'] += 0.2
    elif 'volumen' in text or 'volume' in text:
        result['metric'] = 'volume'
        result['confidence'] += 0.2
    elif 'rsi' in text or 'fortaleza' in text:
        result['metric'] = 'rsi'
        result['confidence'] += 0.2
    elif 'sma' in text or 'media móvil' in text or 'promedio' in text:
        result['metric'] = 'sma'
        result['confidence'] += 0.2
    elif 'macd' in text or 'convergencia' in text:
        result['metric'] = 'macd'
        result['confidence'] += 0.2
    elif 'volatilidad' in text or 'volatility' in text:
        result['metric'] = 'volatility'
        result['confidence'] += 0.2
    else:
        result['metric'] = 'price'  # Default
    
    # Detectar período
    # Números explícitos
    match = re.search(r'(\d+)\s*(días?|d\b|semanas?|meses?|años?)', text)
    if match:
        num = int(match.group(1))
        unit = match.group(2).lower()
        
        if unit.startswith('d'):
            result['period'] = num
            result['forecast_days'] = num
        elif unit.startswith('semana'):
            result['period'] = num * 7
            result['forecast_days'] = num * 7
        elif unit.startswith('mes'):
            result['period'] = num * 30
            result['forecast_days'] = num * 30
        elif unit.startswith('año'):
            result['period'] = {'year': 2000 + num if num < 100 else num}
    
    # Expresiones comunes
    if 'últimos' in text or 'últimas' in text:
        if '7' in text or 'semana' in text:
            result['period'] = 7
            result['forecast_days'] = 7
        elif '14' in text:
            result['period'] = 14
            result['forecast_days'] = 14
        elif '30' in text or 'mes' in text:
            result['period'] = 30
            result['forecast_days'] = 30
        elif '90' in text or 'trimestre' in text:
            result['period'] = 90
            result['forecast_days'] = 90
        elif '365' in text or 'año' in text:
            result['period'] = 365
            result['forecast_days'] = 365
    
    # Años específicos
    for year in range(2020, 2026):
        if str(year) in text:
            result['period'] = {'year': year}
            break
    
    # Detectar tipo visualización
    if 'barras' in text or 'bar' in text:
        result['visualization'] = 'bar'
    elif 'velas' in text or 'candlestick' in text:
        result['visualization'] = 'candlestick'
    
    # Normalizar confianza (0-1)
    result['confidence'] = min(1.0, result['confidence'])
    
    return result
