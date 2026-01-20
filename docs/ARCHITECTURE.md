# System Architecture

## Data Flow Diagram

This section presents the data flow of the system, either using an ASCII diagram or a graphical representation.

The diagram illustrates how raw market data is ingested, processed, transformed into features, used for model inference, and finally delivered as predictions.

## Technology Stack

- Backend: Python 3.9 or higher
- Web interface: Streamlit
- Machine Learning: scikit-learn, TensorFlow, Keras
- Visualization: Plotly, Matplotlib
- Data processing: Pandas, NumPy

## Key Design Decisions

1. Streamlit versus Flask  
   Streamlit was selected to enable rapid prototyping and experimentation, prioritizing development speed over traditional web service deployment.

2. Combination of Random Forest and LSTM models  
   The use of both models allows capturing complementary patterns, combining non-linear regression with temporal dependency modeling.

3. No external APIs  
   The system avoids reliance on third-party APIs to ensure full reproducibility and offline execution.

4. Use of pre-trained models  
   Models are trained offline and loaded at runtime, enabling fast inference and reduced computational overhead.

## Scalability Considerations

- Data caching mechanisms to reduce redundant computations
- Batch processing of predictions for improved performance
- Potential integration of a database to store historical predictions and results

graph TD
    A[Usuario] --> B[Streamlit App]
    A --> C[API Vercel]
    B --> D[Modelos Locales]
    C --> E[Modelos en Cloud]
    D --> F[Predicción]
    E --> F
    F --> G[Feedback System]
    G --> H[Re-entrenamiento]