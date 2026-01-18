import streamlit as st
import pandas as pd
import numpy as np
from src.nlp_parser import parse_command
from src.data_handler import load_data, get_date_range, prepare_features
from src.predictor import load_models, predict_next_days
from src.visualizer import (
    plot_price_forecast, 
    plot_volume_forecast,
    plot_technical_indicators,
    plot_model_comparison
)
from src.indicators import calculate_rsi, calculate_sma, calculate_macd, calculate_volatility
import config

# Config página
st.set_page_config(
    page_title="Solana Predictor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #1a1f2e;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ================================
# SIDEBAR
# ================================
st.sidebar.title("📊 Solana Predictor")
st.sidebar.markdown("---")
st.sidebar.markdown("""
**Versión:** 1.0
**Dataset:** 2020-2025 (1,877 días)
**Modelos:** Random Forest + LSTM

### Ejemplos de comandos:
- "gráfico de precio próximos 14 días"
- "volumen predicho en 2027"
- "comparación RF vs LSTM"
- "RSI histórico en 2023"
- "volatilidad últimas 2 semanas"
- "MACD en los próximos 30 días"
""")

st.sidebar.markdown("---")
st.sidebar.info("⚠️ **Disclaimer:** Este es un sistema educativo. No es asesoramiento financiero.")

# ================================
# MAIN CONTENT
# ================================
st.title("🚀 Solana Price Prediction System")
st.markdown("Análisis técnico y predicción de precios usando Machine Learning")

# ================================
# INPUT DEL USUARIO
# ================================
user_input = st.text_input(
    "¿Qué quieres analizar?",
    placeholder="Ej: 'gráfico de precio próximos 14 días'",
    label_visibility="collapsed"
)

# ================================
# PROCESAMIENTO
# ================================
if user_input:
    with st.spinner("Analizando tu consulta..."):
        try:
            # 1. Parsear comando
            parsed = parse_command(user_input)
            
            if not parsed or parsed['confidence'] < 0.2:
                st.error("❌ No entendí tu pregunta. Intenta con:")
                st.info("- 'Precio próximos 14 días'")
                st.info("- 'Volumen en 2024'")
                st.info("- 'RSI histórico'")
            else:
                # 2. Cargar datos
                st.write(f"📌 Buscando: **{parsed['metric'].upper()}** | Período: **{parsed['period']}**")
                
                df = load_data(config.DATA_FILE)
                
                # 3. Filtrar según período
                if isinstance(parsed['period'], dict) and 'year' in parsed['period']:
                    data_range = get_date_range(df, year=parsed['period']['year'])
                    period_label = f"Año {parsed['period']['year']}"
                else:
                    days = parsed['period'] if isinstance(parsed['period'], int) else 30
                    if parsed['type'] == 'prediction':
                        # Para predicciones, usa últimos 100 días como base
                        data_range = get_date_range(df, period=100)
                        period_label = f"Próximos {days} días (desde base de {len(data_range)} días)"
                    else:
                        data_range = get_date_range(df, period=days)
                        period_label = f"Últimos {days} días"
                
                # 4. Seleccionar métrica
                if parsed['type'] == 'prediction':
                    # ==================
                    # PREDICCIÓN
                    # ==================
                    st.subheader("🔮 Predicción")
                    
                    with st.spinner("Cargando modelos..."):
                        rf_model, lstm_model, scaler = load_models(config.MODEL_PATH)
                    
                    with st.spinner("Generando predicciones..."):
                        features = prepare_features(data_range)
                        forecast_days = parsed.get('forecast_days', config.DEFAULT_FORECAST_DAYS)
                        
                        predictions = predict_next_days(
                            rf_model, lstm_model, scaler, 
                            features, 
                            days=forecast_days
                        )
                    
                    # Mostrar métricas
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "Precio Actual",
                            f"${data_range['Close'].iloc[-1]:.2f}",
                            f"+{predictions['ensemble'][0] - data_range['Close'].iloc[-1]:.2f}"
                        )
                    with col2:
                        st.metric(
                            "Predicción (Día +14)",
                            f"${predictions['ensemble'][min(14, len(predictions['ensemble'])-1)]:.2f}"
                        )
                    with col3:
                        confidence = parsed['confidence']
                        st.metric("Confianza del Modelo", f"{confidence*100:.0f}%")
                    
                    st.markdown("---")
                    
                    # Gráficas según métrica
                    if parsed['metric'] == 'price':
                        st.subheader("📈 Predicción de Precio")
                        fig = plot_price_forecast(
                            data_range[['Open time', 'Close']].set_index('Open time'),
                            predictions
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Comparación modelos
                        st.subheader("🔬 Comparación de Modelos")
                        fig_comp = plot_model_comparison(
                            predictions['rf'],
                            predictions['lstm'],
                            predictions['ensemble']
                        )
                        st.plotly_chart(fig_comp, use_container_width=True)
                    
                    elif parsed['metric'] == 'volume':
                        st.subheader("📊 Predicción de Volumen")
                        fig = plot_volume_forecast(
                            data_range[['Open time', 'Volume']].set_index('Open time'),
                            predictions
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                elif parsed['type'] == 'indicator':
                    # ==================
                    # INDICADORES TÉCNICOS
                    # ==================
                    st.subheader("📉 Análisis Técnico")
                    
                    closes = data_range['Close'].values
                    
                    if parsed['metric'] == 'rsi':
                        rsi = calculate_rsi(closes, period=14)
                        fig = plot_technical_indicators(
                            data_range.copy(),
                            indicators={'RSI': rsi}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Interpretación
                        current_rsi = rsi[-1]
                        if current_rsi > 70:
                            st.warning(f"🔴 RSI en {current_rsi:.1f}: SOBRECOMPRA")
                        elif current_rsi < 30:
                            st.success(f"🟢 RSI en {current_rsi:.1f}: SOBREVENTA")
                        else:
                            st.info(f"⚪ RSI en {current_rsi:.1f}: Neutro")
                    
                    elif parsed['metric'] == 'sma':
                        sma20 = calculate_sma(closes, period=20)
                        sma50 = calculate_sma(closes, period=50)
                        sma200 = calculate_sma(closes, period=200)
                        
                        fig = plot_technical_indicators(
                            data_range.copy(),
                            indicators={'SMA20': sma20, 'SMA50': sma50, 'SMA200': sma200}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif parsed['metric'] == 'macd':
                        macd_data = calculate_macd(closes)
                        fig = plot_technical_indicators(
                            data_range.copy(),
                            indicators={'MACD': macd_data['macd'], 'Signal': macd_data['signal']}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif parsed['metric'] == 'volatility':
                        vol = calculate_volatility(closes, period=20)
                        st.metric("Volatilidad Histórica Anualizada", f"{vol*100:.2f}%")
                        st.info(f"Riesgo: {'Alto' if vol > 0.5 else 'Medio' if vol > 0.3 else 'Bajo'}")
                
                elif parsed['type'] == 'historical':
                    # ==================
                    # ANÁLISIS HISTÓRICO
                    # ==================
                    st.subheader("📚 Análisis Histórico")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Precio Mínimo", f"${data_range['Close'].min():.2f}")
                    with col2:
                        st.metric("Precio Máximo", f"${data_range['Close'].max():.2f}")
                    with col3:
                        st.metric("Precio Promedio", f"${data_range['Close'].mean():.2f}")
                    with col4:
                        change = ((data_range['Close'].iloc[-1] - data_range['Close'].iloc[0]) / data_range['Close'].iloc[0]) * 100
                        st.metric("Cambio %", f"{change:.2f}%")
                    
                    st.markdown("---")
                    
                    # Gráfica histórica
                    if parsed['metric'] == 'price':
                        fig = plot_price_forecast(
                            data_range[['Open time', 'Close']].set_index('Open time'),
                            {'ensemble': data_range['Close'].values}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif parsed['metric'] == 'volume':
                        fig = plot_volume_forecast(
                            data_range[['Open time', 'Volume']].set_index('Open time'),
                            {'ensemble': data_range['Volume'].values}
                        )
                        st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Por favor, intenta de nuevo con una pregunta clara.")

# ================================
# FOOTER
# ================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8rem;'>
    <p>Solana Price Predictor | Proyecto Final Unit 25 Applied Machine Learning</p>
    <p>⚠️ Sistema Educativo - No es Asesoramiento Financiero</p>
</div>
""", unsafe_allow_html=True)