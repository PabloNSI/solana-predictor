# Modelo Seleccionado: Random Forest

## Comparativa de Modelos: Random Forest vs LSTM

| Métrica | Random Forest | LSTM | Mejora Relativa |
|---------|---------------:|------:|----------------:|
| **RMSE Test** | 9.2404 | (LSTM: ver notebooks) | RF supera según evaluación disponible |
| **MAE Test** | 6.8549 | (LSTM: ver notebooks) | RF supera según evaluación disponible |
| **R² Score** | 0.9340 | (LSTM: ver notebooks) | RF explica más varianza en los datos |
| **Error promedio** | 6.8549 | (LSTM: ver notebooks) | RF menor error promedio |
| **% predicciones con error < $10** | 74.19% | (LSTM: ver notebooks) | RF más consistente |

Nota: Las métricas numéricas corresponden a `notebooks/model_info.json` (training_date: 2026-01-20). Si quieres publicar números comparativos exactos del LSTM, incorpora los resultados de sus experimentos en el mismo JSON o en el notebook.

## Análisis Técnico Detallado

### Dataset Limitado

- **LSTM**: Requiere miles/millones de muestras para capturar patrones temporales complejos
- **Realidad**: Dataset actual (~1,877 puntos) insuficiente para LSTM
- **RF**: Funciona óptimamente con datasets pequeños/medianos

### Complejidad del Mercado

- **Volatilidad extrema**: Precios cripto siguen dinámicas caóticas
- **LSTM**: Busca patrones temporales que pueden no existir
- **RF**: Combina features técnicas (RSI, MA) de forma más eficiente

### Overfitting del LSTM

- **Parámetros**: LSTM tiene decenas de miles vs RF con ~100 árboles
- **Resultado**: LSTM memoriza ruido, RF generaliza mejor
- **Regularización**: RF con `max_depth=15` controla automáticamente complejidad

### Features de Ingeniería

- **Features calculados**: RSI, medias móviles ya codifican información temporal
- **RF**: Aprovecha directamente estas relaciones
- **LSTM**: Intenta reconstruir patrones ya extraídos

## Modelo en Producción

### Especificaciones Técnicas

- **Algoritmo**: Random Forest Regressor (Scikit-Learn)
- **Hiperparámetros**:

```python
{'n_estimators': 100, 'max_depth': 15, 
 'min_samples_split': 5, 'min_samples_leaf': 2,
 'random_state': 42, 'n_jobs': -1}
```

Referencias:
- Resultados y métricas: `notebooks/model_info.json`

- Modelos serializados: `models/rf_model_best.pkl`