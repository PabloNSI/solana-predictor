
# Solana Price Predictor

Sistema de predicción de precios Solana usando Machine Learning (Random Forest + LSTM) con interfaz Streamlit interactiva.

## 🚀 Quick Start

### 1. Instalación

```bash
# Clonar repositorio
git clone https://github.com/tuusuario/solana-predictor.git
cd solana-predictor

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Entrenar Modelos (Primero)

```bash
# Ejecutar notebooks (en orden)
jupyter notebook notebooks/01_EDA_Solana.ipynb
jupyter notebook notebooks/02_Model_Training.ipynb

# Esto genera:
# - models/rf_model.pkl
# - models/lstm_model.h5
# - models/scaler.pkl
```

### 3. Ejecutar Aplicación

```bash
streamlit run app.py
```

## 💬 Ejemplos de Comandos

- "gráfico de precio próximos 14 días"
- "volumen predicho en 2027"
- "comparación RF vs LSTM"
- "RSI histórico en 2023"
- "volatilidad últimas 2 semanas"
- "MACD en los próximos 30 días"

## 📊 Estructura del Proyecto

```bash
solana-predictor/
├── app.py                    # Aplicación Streamlit
├── src/
│   ├── data_handler.py      # Carga datos
│   ├── nlp_parser.py        # Parser NLP
│   ├── predictor.py         # Modelos
│   ├── indicators.py        # Indicadores técnicos
│   └── visualizer.py        # Gráficas Plotly
├── notebooks/
│   ├── 01_EDA_Solana.ipynb
│   └── 02_Model_Training.ipynb
├── models/
│   ├── rf_model.pkl
│   ├── lstm_model.h5
│   └── scaler.pkl
├── data/
│   └── sol_1d_data_2020_to_2025.csv
├── TECHNICAL_REPORT.md      # Memoria académica
└── requirements.txt
```

## 📈 Resultados

- **Random Forest R² Score:** 0.72
- **LSTM R² Score:** 0.76
- **Ensemble Accuracy:** 62%
- **Dataset:** 1,877 días (2020-2025)

## ⚠️ Disclaimer

Este es un **sistema educativo**. No es asesoramiento financiero.

Las predicciones se basan en patrones históricos y NO garantizan resultados futuros.

## 📚 Documentación

- Ver `TECHNICAL_REPORT.md` para análisis completo
- Ver `ARCHITECTURE.md` para detalles técnicos

## 👤 Pablo Soto

Proyecto Final Unit 25: Applied Machine Learning
Pearson HND - Computer Science & AI/Data Science
