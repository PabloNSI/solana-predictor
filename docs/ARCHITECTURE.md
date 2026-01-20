# System Architecture

## Data Flow Diagram

This section presents the data flow of the system, either using an ASCII diagram or a graphical representation.

The diagram illustrates how raw market data is ingested, processed, transformed into features, used for model inference, and finally delivered as predictions.

## Technology Stack

- Backend: Python 3.9 or higher
- Web interface: Streamlit (demo opcional)
- Machine Learning: scikit-learn, TensorFlow, Keras
- Visualization: Plotly, Matplotlib
- Data processing: Pandas, NumPy

## Key Design Decisions

1. Streamlit versus Flask  
   Streamlit was selected to enable rapid prototyping and experimentation, prioritizing development speed over traditional web service deployment.

2. Combination of Random Forest and LSTM models  
   The use of both models allows capturing complementary patterns, combining non-linear regression with temporal dependency modeling.

3. No external APIs (por ahora)  
   The system evita dependencia en APIs externas para asegurar reproducibilidad y ejecución offline. La exposición vía API o despliegue en cloud es una posible evolución.

4. Use of pre-trained models  
   Models are trained offline and loaded at runtime, enabling fast inference and reduced computational overhead.

## Scalability Considerations

- Data caching mechanisms to reduce redundant computations
- Batch processing of predictions for improved performance
- Potential integration of a database to store historical predictions and results

graph TD
    A[Usuario] --> B[Streamlit App]
    B --> D[Modelos Locales]
    D --> F[Predicción]
    F --> G[Feedback System]
    G --> H[Re-entrenamiento]

Nota: La arquitectura actual del repositorio incluye una demo/visualizador local (Streamlit) y modelos serializados en `models/`. La integración con APIs externas o despliegue en cloud (Vercel u otros) se considera una posible extensión, no una implementación actual en este repo.