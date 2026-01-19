
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
source venv/bin/activate  # En Windows: .\venv\Scripts\Activate.ps1

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

```text
solana-predictor/
├── .gitignore
├── .streamlit/
│   └── config.toml
├── ANALISIS.md
├── ARCHITECTURE.md
├── MODELO_SELECCIONADO.md
├── README.md
├── TECHNICAL_REPORT.md
├── api/
│   ├── feedback.py
│   ├── health.py
│   └── predict.py
├── app.py
├── config.py
├── data/
│   ├── features_prepared.csv
│   └── sol_1d_data_2020_to_2025.csv
├── models/
│   ├── README_MODELS.md
│   ├── lstm_model.h5
│   ├── model.pkl
│   ├── model_info.json
│   ├── model_metrics.json
│   ├── rf_model.pkl
│   ├── rf_model_best.pkl
│   └── scaler.pkl
├── notebooks/
│   ├── 01_EDA_Solana.ipynb
│   └── 02_Model_Training.ipynb
├── output/
│   ├── LSTM_Training_Loss.png
│   ├── error_analysis.png
│   └── predictions_vs_actual.png
├── requirements.txt
├── run_tests.py
├── scripts/
│   ├── requirements.txt
│   └── retrain.py
├── src/
│   ├── data_handler.py
│   ├── indicators.py
│   ├── nlp_parser.py
│   ├── predictor.py
│   └── visualizer.py
├── tests/
└── vercel.json
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
