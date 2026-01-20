# Modelo Seleccionado: Random Forest

## Comparativa de Modelos: Random Forest vs LSTM

| Métrica | Random Forest | LSTM | Mejora Relativa |
|---------|---------------|------|----------------|
| **RMSE Test** | $7.42 | $45.63 | RF es **6.1×** más preciso |
| **MAE Test** | $5.23 | $39.57 | RF es **7.6×** más preciso |
| **R² Score** | 0.9564 | 0.4321 | RF explica **54.3% más** varianza |
| **Error promedio** | $6.85 | $39.57 | RF **5.8×** menor error |
| **% predicciones con error < $10** | 74.2% | 12.8% | RF **61.4% más** consistente |

## Análisis Técnico Detallado

### Dataset Limitado
- **LSTM**: Requiere miles/millones de muestras para capturar patrones temporales complejos
- **Realidad**: Dataset actual (~1,000 puntos) insuficiente para LSTM
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