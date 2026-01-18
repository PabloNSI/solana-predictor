
import plotly.graph_objects as go
import pandas as pd

def plot_price_forecast(historical, predictions):
    """Gráfica interactiva de precio"""
    fig = go.Figure()
    
    # Histórico
    fig.add_trace(go.Scatter(
        x=historical.index,
        y=historical['Close'],
        name='Histórico',
        line=dict(color='#667eea', width=2),
        hovertemplate='<b>%{x}</b><br>$%{y:.2f}<extra></extra>'
    ))
    
    # Predicción
    future_dates = pd.date_range(
        start=historical.index[-1],
        periods=len(predictions['ensemble']) + 1
    )[1:]
    
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=predictions['ensemble'],
        name='Predicción',
        line=dict(color='#ff6b6b', width=2, dash='dash'),
        hovertemplate='<b>%{x}</b><br>$%{y:.2f}<extra></extra>'
    ))
    
    # Bandas de confianza
    fig.add_trace(go.Scatter(
        x=list(future_dates) + list(future_dates[::-1]),
        y=list(predictions['confidence_upper']) + list(predictions['confidence_lower'][::-1]),
        fill='toself',
        fillcolor='rgba(255, 107, 107, 0.2)',
        line=dict(color='rgba(255, 255, 255, 0)'),
        name='Intervalo Confianza',
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        title='Predicción de Precio Solana',
        xaxis_title='Fecha',
        yaxis_title='Precio (USD)',
        hovermode='x unified',
        height=600,
        template='plotly_dark',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def plot_volume_forecast(historical, predictions):
    """Gráfica de volumen"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=historical.index,
        y=historical['Volume'],
        name='Volumen Histórico',
        marker_color='#667eea',
        opacity=0.7
    ))
    
    future_dates = pd.date_range(
        start=historical.index[-1],
        periods=len(predictions['ensemble']) + 1
    )[1:]
    
    fig.add_trace(go.Bar(
        x=future_dates,
        y=predictions['ensemble'],
        name='Volumen Predicho',
        marker_color='#ff6b6b',
        marker_pattern_shape="/"
    ))
    
    fig.update_layout(
        title='Predicción de Volumen',
        xaxis_title='Fecha',
        yaxis_title='Volumen',
        hovermode='x unified',
        height=600,
        template='plotly_dark'
    )
    
    return fig

def plot_technical_indicators(df, indicators):
    """Gráfica de indicadores técnicos"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Open time'],
        y=df['Close'],
        name='Precio',
        line=dict(color='#667eea')
    ))
    
    colors = ['#ff6b6b', '#4ecdc4', '#95e77d']
    for i, (name, values) in enumerate(indicators.items()):
        fig.add_trace(go.Scatter(
            x=df['Open time'],
            y=values,
            name=name,
            line=dict(color=colors[i % len(colors)])
        ))
    
    fig.update_layout(
        title='Indicadores Técnicos',
        xaxis_title='Fecha',
        yaxis_title='Valor',
        height=600,
        template='plotly_dark'
    )
    
    return fig

def plot_model_comparison(rf_pred, lstm_pred, ensemble_pred):
    """Compara predicciones de modelos"""
    fig = go.Figure()
    
    days = list(range(1, len(ensemble_pred) + 1))
    
    fig.add_trace(go.Scatter(
        x=days, y=rf_pred,
        name='Random Forest',
        line=dict(color='#667eea')
    ))
    
    fig.add_trace(go.Scatter(
        x=days, y=lstm_pred,
        name='LSTM',
        line=dict(color='#ff6b6b')
    ))
    
    fig.add_trace(go.Scatter(
        x=days, y=ensemble_pred,
        name='Ensemble',
        line=dict(color='#4ecdc4', width=3, dash='dash')
    ))
    
    fig.update_layout(
        title='Comparación de Modelos',
        xaxis_title='Día',
        yaxis_title='Precio (USD)',
        height=600,
        template='plotly_dark'
    )
    
    return fig

