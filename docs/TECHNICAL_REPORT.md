# Informe Técnico: Sistema de Predicción de Precio de Solana (SOL)

Fecha del documento: 2026-01-20  
Autor: Pablo Soto (PabloNSI)

## Resumen ejecutivo (Abstract)

Este informe describe un sistema reproducible para predecir el precio de cierre diario de Solana (SOL/USDT) usando ingeniería de features y modelos de Machine Learning. Se experimentó con dos enfoques principales: Random Forest (modelo final) y redes LSTM. El pipeline ingiere datos OHLCV históricos de Binance, aplica limpieza y construcción de indicadores técnicos (RSI, medias móviles, etc.), realiza una separación temporal entre entrenamiento y prueba y evalúa modelos mediante RMSE, MAE y R², además de métricas de dirección y consistencia. El Random Forest seleccionado (n_estimators=100, max_depth=15, min_samples_split=5, min_samples_leaf=2, random_state=42) alcanzó en test: MAE ≈ 6.85, RMSE ≈ 9.24 y R² ≈ 0.934 (ver `notebooks/model_info.json`). Con el dataset disponible (~1.877 observaciones diarias, 2020-08-11 a 2025-09-29) el enfoque basado en features y Random Forest supera al LSTM en generalización; se discuten limitaciones y vías de mejora.

---

## 1. Objetivo

Construir y evaluar un sistema reproducible que, a partir de históricos diarios de SOL/USDT, produzca predicciones del precio de cierre próximas en horizonte diario, comparando un modelo clásico de árboles (Random Forest) con un modelo secuencial (LSTM), y proponiendo la opción final para despliegue local.

## 2. Resumen del conjunto de datos

- Fuente: Binance (historical OHLCV).
- Activo: SOL/USDT.
- Periodo: 2020-08-11 — 2025-09-29.
- Registros: 1.877 observaciones diarias.
- Variables originales: Open, High, Low, Close, Volume.
- Archivos relevantes: `data/sol_1d_data_2020_to_2025.csv`, `data/features_prepared.csv`.

Consideraciones: los datos se trabajan en series temporales diarias; no se han incluido en el pipeline variables exógenas (noticias, sentimiento) en esta versión.

## 3. Pipeline de preprocesamiento y features

3.1 Limpieza

- Eliminación o imputación de valores nulos.
- Verificación de duplicados y consistencia temporal.

3.2 Ingeniería de features

- Indicadores técnicos calculados: RSI, medias móviles simples (SMA) y exponenciales (EMA), bandas, momentum, etc. (implementados en `src/indicators.py`).
- Derivados: retornos diarios, volatilidad rolling, volumen normalizado.

3.3 Escalado y particionado

- Escalado: StandardScaler (guardado para producción en `models/scaler.pkl`).
- Split temporal train/test: 80/20 respetando orden cronológico para evitar contaminación futura.

3.4 Formatos de salida

- Conjuntos listos para entrenamiento, validación y prueba, y tablas de predicción para análisis.

## 4. Modelos y estrategia experimental

4.1 Modelos evaluados

- Random Forest Regressor (Scikit-Learn) — modelo seleccionado para producción.
- LSTM (TensorFlow / Keras) — experimento para comparar capacidad temporal.

4.2 Hiperparámetros del modelo seleccionado

- Random Forest (mejor versión):
  - n_estimators: 100
  - max_depth: 15
  - min_samples_split: 5
  - min_samples_leaf: 2
  - random_state: 42
  - n_jobs: -1
- Modelo guardado: `models/rf_model_best.pkl`.
- Metadatos del entrenamiento: `notebooks/model_info.json` (fecha de entrenamiento incluida).

4.3 Protocolo de evaluación

- Métricas principales: RMSE, MAE, R².
- Métricas adicionales: exactitud direccional (signo del cambio), porcentaje de predicciones con error absoluto < $10.
- Curvas de entrenamiento y análisis de errores (guardados en `output/`).

## 5. Resultados principales

- Random Forest (test):
  - RMSE ≈ 9.2404
  - MAE ≈ 6.8549
  - R² ≈ 0.9340
  - % predicciones con error < $10 ≈ 74.19%
- Fuente de métricas: `notebooks/model_info.json` (training_date: 2026-01-20 13:22:32).
- Interpretación: el Random Forest, con features técnicos, generaliza bien sobre el conjunto de prueba; su R² alto indica que explica gran parte de la varianza en el periodo evaluado.
- Comparación con LSTM: con el volumen de datos disponible, el LSTM mostró mayor error y tendencia a overfitting en los experimentos realizados; por tanto, no se seleccionó para producción.

## 6. Análisis crítico y limitaciones

- Volumen de datos: ~1.877 observaciones diarias es relativamente limitado para redes recurrentes profundas; favorece modelos no paramétricos como RF cuando se dispone de features relevantes.
- Ausencia de variables exógenas: noticias, sentimiento, órdenes en libro y macrofactores no se modelaron; su inclusión puede mejorar la capacidad predictiva.
- Horizonte de predicción: modelo enfocado en predicción diaria de cierre; rendimiento puede variar en horizontes intradiarios o multidiarios.
- Riesgo de look-ahead o sesgo temporal: mitigado con split temporal, pero es crítico mantener disciplina experimental en futuras pruebas.
- Robustez en regímenes extremos: eventos "black swan" no predictibles por datos históricos; el modelo puede fallar en periodos de shocks.

## 7. Despliegue y reproducibilidad

- Notebook principal: `Proyecto_Final_Unit25.ipynb` contiene la narrativa, EDA y pasos reproducibles.
- Código modular: funciones y utilidades en `src/` (`data_handler.py`, `indicators.py`, `predictor.py`, `visualizer.py`, `nlp_parser.py`).
- Artefactos guardados:
  - Modelos: `models/rf_model_best.pkl`, `models/rf_model.pkl`, `models/lstm_model.h5` (si aplicable).
  - Escalador: `models/scaler.pkl`.
  - Resultados: `notebooks/model_info.json`, gráficas en `output/`.
- Despliegue actual: demo local basada en Streamlit (opcional). No hay API pública desplegada por defecto; despliegue en producción requiere:
  - Contenerización (Docker),
  - Orquestación o servicio web (FastAPI/Flask),
  - Monitorización de métricas y reentrenamiento automatizado.

## 8. Recomendaciones y trabajo futuro

- Ampliar dataset: incluir datos intradiarios o extender periodo histórico si es posible.
- Incorporar variables exógenas: feeds de noticias, sentimiento en redes sociales, métricas on-chain.
- Pipeline de MLOps básico: monitorización de rendimiento y retraining programado cuando la performance decaiga.
- Evaluar modelos probabilísticos o ensamblados (Gradient Boosting, Ensembles) y métodos de incertidumbre (intervalos de predicción).
- Si se considera LSTM en el futuro: aumentar datos y aplicar regularización más agresiva, validación por ventana deslizante (time-series cross-validation).

## 9. Conclusiones

El enfoque basado en ingeniería de features y Random Forest ofrece, con el dataset y configuración actual, el mejor balance entre precisión, velocidad y explicabilidad. Las métricas muestran que es un candidato válido para uso de investigación y prototipado; su robustez en producción dependerá de incorporar más datos y señal exógena, así como de un plan de monitorización y retraining.

---

## Referencias y recursos del repositorio

- Notebook principal: `Proyecto_Final_Unit25.ipynb`
- Model info / métricas: `notebooks/model_info.json`
- Código: `src/` (`data_handler.py`, `indicators.py`, `predictor.py`, `visualizer.py`, `nlp_parser.py`)
- Modelos serializados: `models/` (`rf_model_best.pkl`, `scaler.pkl`, etc.)
- Outputs: `output/` (gráficas y análisis visual)
- README: resumen del proyecto y pasos de instalación

---

## Apéndices

Appendix A — Implementación y comandos para reproducir:

- Crear entorno, instalar dependencias:
  - `python -m venv venv && source venv/bin/activate`
  - `pip install -r requirements.txt`
- Ejecutar notebook: `jupyter notebook Proyecto_Final_Unit25.ipynb`
- Cargar modelo en Python (ejemplo):

```python
import joblib
rf = joblib.load("models/rf_model_best.pkl")
scaler = joblib.load("models/scaler.pkl")
```

Appendix B — Ubicación de código clave:

- Preprocesamiento e ingreso: `src/data_handler.py`
- Indicadores técnicos: `src/indicators.py`
- Entrenamiento y predicción: `src/predictor.py`
- Visualización: `src/visualizer.py`

Appendix C — Metadatos de entrenamiento

- Ver `notebooks/model_info.json` para fecha, métricas exactas y hiperparámetros usados durante el experimento final.

(El contenido de este informe está pensado para ser conciso y operativo; si deseas, puedo expandir cualquiera de las secciones —p. ej. EDA, metodología detallada o resultados con tablas y gráficos— y añadir los extractos de código y figuras correspondientes.)
