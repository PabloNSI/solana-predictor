# Solana Price Predictor – Proyecto Final Unit 25

Sistema de predicción de precios de **Solana (SOL)** usando **Random Forest** y **LSTM**, desarrollado como **proyecto final académico** para la asignatura **Unit 25: Applied Machine Learning** (Pearson HND PD Computer Science & AI / Data Science & AI).

**Entrega principal:** Jupyter Notebook interactivo `Proyecto_Final_Unit25.ipynb` (incluye introducción, objetivos, marco teórico, EDA, preprocesamiento, entrenamiento, evaluación crítica, mejora con IA generativa, visualizaciones, conclusiones, bibliografía Harvard y anexos).

Este proyecto integra conocimientos del curso: teoría matemática, modelado en Kaggle-style, análisis de errores y storytelling visual. Incluye una demo opcional con Streamlit para mostrar predicciones en producción.

**Fecha de entrega:** 20/01/2026  
**Alumno:** Pablo Soto – Madrid

## 🚀 Quick Start (Reproducibilidad del Proyecto)

### 1. Instalación

```bash
# Clonar repositorio
git clone https://github.com/PabloNSI/solana-predictor.git
cd solana-predictor

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Abrir el notebook principal (entrega oficial)
jupyter notebook Proyecto_Final_Unit25.ipynb
```

```text
solana-predictor/
├── .gitignore
├── README.md
├── requirements.txt
│
├── Proyecto_Final_Unit25.ipynb  # ★ Entrega principal – Notebook interactivo Unit 25
│
├── data/                        # Datos para EDA y entrenamiento
│   ├── sol_1d_data_2020_to_2025.csv
│   └── features_prepared.csv
│
├── models/                      # Modelos entrenados + métricas
│   ├── lstm_model.h5
│   ├── rf_model_best.pkl        # Versión seleccionada
│   └── scaler.pkl
│
├── notebooks/                   # Notebooks de soporte (importados/referenciados en el principal)
│   ├── 01_EDA_Solana.ipynb
│   └── 02_Model_Training.ipynb
│
├── output/                      # Gráficos clave para storytelling
│   ├── LSTM_Training_Loss.png
│   ├── predictions_vs_actual.png
│   └── error_analysis.png
│
├── src/                         # Módulos reutilizables (usados en notebook y app)
│   ├── data_handler.py
│   ├── indicators.py
│   ├── nlp_parser.py            # Soporte IA generativa (sentiment, etc.)
│   ├── predictor.py
│   └── visualizer.py
│
└── (Otros md antiguos movidos o integrados al notebook: ANALISIS.md, ARCHITECTURE.md, etc.)
```
