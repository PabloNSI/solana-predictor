# Technical Report: Solana Price Prediction System

## Abstract

This section provides a summary of approximately 150 words.  
It should include the problem context, the methodology employed (Random Forest and LSTM), the dataset used, the main evaluation metrics, and the key conclusions.

---

## 1. Introduction

This section has an approximate length of two pages.

### Context

- Analysis of cryptocurrencies as highly volatile financial assets
- Importance of forecasting in digital markets
- Relevance of Solana within the blockchain ecosystem

### Problem Statement

- Difficulty of predicting financial prices
- High non-stationarity and volatility
- Limitations of traditional models

### Objectives

- Build a predictive system based on Machine Learning
- Compare non-linear models and sequential models
- Evaluate predictive capacity under different market scenarios

### Contributions

- End-to-end financial data pipeline
- Comparison between Random Forest and LSTM models
- Honest critical analysis of limitations
- Reproducible and extensible system

---

## 2. Related Work

This section has an approximate length of one and a half pages.

- State of the art in financial forecasting
- Classical models: ARIMA, GARCH
- Machine Learning applied to time series
- Deep Learning in financial markets
- Predictive systems in algorithmic trading
- Differences with respect to previous work

---

## 3. Dataset Description

This section has an approximate length of one page.

- Source: Binance (historical OHLCV data)
- Asset: Solana (SOL/USDT)
- Period: 2020-08-11 to 2025-09-29
- Number of records: 1,877 daily observations

### Variables

| Field | Description |
| ------ | ------------- |
| Open | Opening price |
| High | Maximum price |
| Low | Minimum price |
| Close | Closing price |
| Volume | Traded volume |

Additional considerations include data quality checks and the absence of exogenous variables such as news or sentiment indicators.

---

## 4. Exploratory Data Analysis

This section has an approximate length of three pages.

### Visualizations

- Figure 1: Historical price with simple moving averages (SMA)
- Figure 2: Distribution of daily returns
- Figure 3: Price–volume relationship

### Key Statistics

- Daily and annualized volatility
- Average returns
- Maximum drawdown
- Price–volume correlation

### Main Findings

- High volatility
- Non-stationarity
- Non-normal distribution
- Presence of extreme events

---

## 5. System Architecture

This section has an approximate length of two pages.

### General Architecture

- End-to-end data flow
- Separation between EDA, training, and evaluation stages

### Technology Stack

- Python
- Pandas, NumPy
- Scikit-learn
- TensorFlow / Keras
- Matplotlib

### Design Decisions

- Independent models
- Model persistence
- Feature scaling prior to training

### Scalability

- Periodic retraining
- Future integration into production environments

---

## 6. Methodology

This section has an approximate length of three pages.

### 6.1 Data Preprocessing

- Data cleaning
- Feature engineering
- Normalization using StandardScaler
- Train/Test split (80/20 respecting temporal order)

### 6.2 Models Implemented

#### Random Forest

- Justification: non-linear and robust model
- Main hyperparameters
- Advantages and limitations

#### LSTM

- Justification: ability to capture temporal dependencies
- Network architecture
- Training strategy
- Early stopping

### 6.3 Evaluation Metrics

- RMSE
- MAE
- R²
- Directional Accuracy
- Approximate Sharpe Ratio

---

## 7. Results

This section has an approximate length of four pages.

- Comparative table of models
- Metrics on training and test sets
- LSTM training curves
- Predictions versus actual values
- Analysis by market regime
- Analysis by volatility levels

---

## 8. Critical Analysis

This section has an approximate length of three pages.

### Why Does the Model Fail?

- Efficient market hypothesis
- Unmodeled exogenous events
- Regime changes
- Non-stationary data

### When Does It Work Well?

- Periods of low volatility
- Clear trends
- Price consolidation phases

### Limitations

- Limited dataset (~5 years)
- Insufficient variables
- Risk of overfitting
- Forward-looking bias

---

## 9. Deployment and Production

This section has an approximate length of one page.

- Model serialization
- Prediction latency
- Performance monitoring
- Retraining strategy

---

## 10. Conclusions

This section has an approximate length of one and a half pages.

- Main findings
- Technical lessons learned
- Feasibility of the approach
- Real-world applicability
- Future work

---

## 11. References

### Harvard Reference Format

At least 20 academic references, including journal articles, books, and conference papers.

---

## Appendices

### Appendix A: Complete Model Code

- Full Random Forest implementation
- Full LSTM implementation

### Appendix B: Hyperparameter Tuning

- Parameter justification
- Discarded experiments

### Appendix C: Full Predictions Table

- Complete prediction results
- Comparison with actual values
