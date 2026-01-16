/**
 * ========================================
 * api/utils/indicators.js
 * ========================================
 * 
 * Implementación desde cero de indicadores técnicos
 * Documentación matemática incluida en comentarios
 * 
 * Indicadores implementados:
 * - RSI (Relative Strength Index)
 * - SMA (Simple Moving Average)
 * - EMA (Exponential Moving Average)
 * - Volatilidad Histórica
 * - MACD (Moving Average Convergence Divergence)
 * - Bollinger Bands
 */

class TechnicalIndicators {

  /**
   * ========================================
   * RSI (Relative Strength Index) - 14 periodos
   * ========================================
   * 
   * Fórmula:
   * RSI = 100 - (100 / (1 + RS))
   * RS = Promedio de Ganancias / Promedio de Pérdidas
   * 
   * Interpretación:
   * - RSI > 70: Zona de sobrecompra (posible corrección a la baja)
   * - RSI < 30: Zona de sobreventa (posible rebote al alza)
   * - RSI = 50: Neutro
   * 
   * @param {Array<number>} closes - Array de precios de cierre
   * @param {number} period - Período (default: 14)
   * @returns {Array<number|null>} Array de valores RSI
   * @throws {Error} Si no hay suficientes datos
   */
  static calculateRSI(closes, period = 14) {
    if (!closes || closes.length < period) {
      throw new Error(`RSI requiere al menos ${period} candles. Se proporcionaron ${closes?.length || 0}`);
    }

    // Paso 1: Calcular cambios (deltas)
    const deltas = [];
    for (let i = 1; i < closes.length; i++) {
      deltas.push(closes[i] - closes[i - 1]);
    }

    // Paso 2: Separar ganancias y pérdidas
    const gains = deltas.map(d => d > 0 ? d : 0);
    const losses = deltas.map(d => d < 0 ? Math.abs(d) : 0);

    // Paso 3: Calcular promedio inicial (primeros 'period' valores)
    let avgGain = gains.slice(0, period).reduce((a, b) => a + b, 0) / period;
    let avgLoss = losses.slice(0, period).reduce((a, b) => a + b, 0) / period;

    // Paso 4: Calcular RSI
    const rsi = [];
    
    // Los primeros 'period' valores son null
    for (let i = 0; i < period; i++) {
      rsi.push(null);
    }

    // Calcular RSI para el resto
    for (let i = period; i < closes.length; i++) {
      // Suavizado Wilder's
      avgGain = (avgGain * (period - 1) + gains[i]) / period;
      avgLoss = (avgLoss * (period - 1) + losses[i]) / period;

      const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
      const rsiValue = 100 - (100 / (1 + rs));
      rsi.push(rsiValue);
    }

    return rsi;
  }

  /**
   * ========================================
   * SMA (Simple Moving Average)
   * ========================================
   * 
   * Fórmula:
   * SMA = (Precio1 + Precio2 + ... + PrecioN) / N
   * 
   * Uso:
   * - SMA(20): Tendencia a corto plazo
   * - SMA(50): Tendencia a medio plazo
   * - SMA(200): Tendencia a largo plazo
   * 
   * @param {Array<number>} prices - Array de precios
   * @param {number} period - Período (default: 20)
   * @returns {Array<number|null>} Array de valores SMA
   */
  static calculateSMA(prices, period = 20) {
    if (!prices || prices.length < period) {
      throw new Error(`SMA requiere al menos ${period} datos`);
    }

    const sma = [];
    
    for (let i = 0; i < prices.length; i++) {
      if (i < period - 1) {
        // No hay suficientes datos para calcular
        sma.push(null);
      } else {
        // Suma de los últimos 'period' precios
        const sum = prices.slice(i - period + 1, i + 1)
          .reduce((acc, val) => acc + val, 0);
        sma.push(sum / period);
      }
    }
    
    return sma;
  }

  /**
   * ========================================
   * EMA (Exponential Moving Average)
   * ========================================
   * 
   * Fórmula:
   * Multiplicador = 2 / (N + 1)
   * EMA = Precio * Multiplicador + EMA_anterior * (1 - Multiplicador)
   * 
   * Diferencia vs SMA:
   * - Da más peso a precios recientes
   * - Responde más rápido a cambios
   * 
   * @param {Array<number>} prices - Array de precios
   * @param {number} period - Período (default: 20)
   * @returns {Array<number>} Array de valores EMA
   */
  static calculateEMA(prices, period = 20) {
    if (!prices || prices.length < period) {
      throw new Error(`EMA requiere al menos ${period} datos`);
    }

    const multiplier = 2 / (period + 1);
    const ema = [prices[0]]; // Inicializar con el primer precio

    for (let i = 1; i < prices.length; i++) {
      const emaValue = (prices[i] * multiplier) + (ema[i - 1] * (1 - multiplier));
      ema.push(emaValue);
    }

    return ema;
  }

  /**
   * ========================================
   * Volatilidad Histórica (Desviación Estándar)
   * ========================================
   * 
   * Fórmula:
   * 1. Retornos logarítmicos: ln(Precio_t / Precio_t-1)
   * 2. Desviación estándar de retornos
   * 3. Anualizar: StdDev * sqrt(252) [252 = días de trading en un año]
   * 
   * Interpretación:
   * - Alta volatilidad: Mayor riesgo y oportunidad
   * - Baja volatilidad: Menos riesgo, tendencia más predecible
   * 
   * @param {Array<number>} closes - Array de precios de cierre
   * @param {number} period - Período (default: 20)
   * @returns {number} Volatilidad histórica anualizada (%)
   */
  static calculateVolatility(closes, period = 20) {
    if (!closes || closes.length < period + 1) {
      throw new Error(`Volatilidad requiere al menos ${period + 1} datos`);
    }

    // Usar últimos 'period' datos
    const priceData = closes.slice(-period - 1);

    // Calcular retornos logarítmicos
    const returns = [];
    for (let i = 1; i < priceData.length; i++) {
      const logReturn = Math.log(priceData[i] / priceData[i - 1]);
      returns.push(logReturn);
    }

    // Media de retornos
    const meanReturn = returns.reduce((a, b) => a + b, 0) / returns.length;

    // Varianza
    const variance = returns.reduce((sum, r) => {
      return sum + Math.pow(r - meanReturn, 2);
    }, 0) / returns.length;

    // Desviación estándar
    const stdDev = Math.sqrt(variance);

    // Anualizar (252 días de trading)
    const annualizedVol = stdDev * Math.sqrt(252);

    return annualizedVol;
  }

  /**
   * ========================================
   * MACD (Moving Average Convergence Divergence)
   * ========================================
   * 
   * Componentes:
   * 1. MACD = EMA(12) - EMA(26)
   * 2. Signal = EMA(9) del MACD
   * 3. Histogram = MACD - Signal
   * 
   * Señales:
   * - MACD cruza sobre Signal (alcista)
   * - MACD cruza bajo Signal (bajista)
   * - Divergencia: divergencia entre precio y MACD
   * 
   * @param {Array<number>} closes - Array de precios de cierre
   * @returns {Object} {macd, signal, histogram}
   */
  static calculateMACD(closes) {
    if (!closes || closes.length < 26) {
      throw new Error('MACD requiere al menos 26 datos');
    }

    const ema12 = this.calculateEMA(closes, 12);
    const ema26 = this.calculateEMA(closes, 26);

    // Calcular línea MACD
    const macd = ema12.map((val12, i) => val12 - ema26[i]);

    // Calcular línea Signal (EMA del MACD)
    const signal = this.calculateEMA(macd, 9);

    // Calcular Histogram
    const histogram = macd.map((val, i) => val - (signal[i] || 0));

    return { macd, signal, histogram };
  }

  /**
   * ========================================
   * Bollinger Bands
   * ========================================
   * 
   * Componentes:
   * 1. Media Móvil Central = SMA(20)
   * 2. Banda Superior = SMA + (StdDev * 2)
   * 3. Banda Inferior = SMA - (StdDev * 2)
   * 
   * Interpretación:
   * - Precio toca banda superior: Posible sobreventa
   * - Precio toca banda inferior: Posible rebote
   * - Bandas anchas: Alta volatilidad
   * - Bandas estrechas: Baja volatilidad (antes de movimiento)
   * 
   * @param {Array<number>} closes - Array de precios de cierre
   * @param {number} period - Período (default: 20)
   * @param {number} stdDev - Número de desviaciones estándar (default: 2)
   * @returns {Object} {upper, middle, lower, bandwidth}
   */
  static calculateBollingerBands(closes, period = 20, stdDev = 2) {
    if (!closes || closes.length < period) {
      throw new Error(`Bollinger Bands requiere al menos ${period} datos`);
    }

    const middle = this.calculateSMA(closes, period);
    const upper = [];
    const lower = [];
    const bandwidth = [];

    for (let i = 0; i < closes.length; i++) {
      if (i < period - 1) {
        upper.push(null);
        lower.push(null);
        bandwidth.push(null);
      } else {
        // Calcular desviación estándar para este período
        const prices = closes.slice(i - period + 1, i + 1);
        const mean = prices.reduce((a, b) => a + b) / period;
        const variance = prices.reduce((sum, p) => sum + Math.pow(p - mean, 2), 0) / period;
        const std = Math.sqrt(variance);

        const m = middle[i];
        upper.push(m + (std * stdDev));
        lower.push(m - (std * stdDev));
        bandwidth.push(upper[i] - lower[i]);
      }
    }

    return { upper, middle, lower, bandwidth };
  }

  /**
   * ========================================
   * ATR (Average True Range)
   * ========================================
   * 
   * Mide la volatilidad promedio del mercado
   * Útil para stop-loss dinámicos
   * 
   * @param {Array<Object>} candleData - Array de {high, low, close}
   * @param {number} period - Período (default: 14)
   * @returns {Array<number|null>} Array de valores ATR
   */
  static calculateATR(candleData, period = 14) {
    if (!candleData || candleData.length < period) {
      throw new Error(`ATR requiere al menos ${period} datos`);
    }

    // Calcular True Range
    const trueRanges = [];
    for (let i = 0; i < candleData.length; i++) {
      const current = candleData[i];
      const previous = i > 0 ? candleData[i - 1] : null;

      const hl = current.high - current.low;
      const hc = Math.abs(current.high - (previous?.close || current.close));
      const lc = Math.abs(current.low - (previous?.close || current.close));

      trueRanges.push(Math.max(hl, hc, lc));
    }

    // Calcular ATR (EMA del True Range)
    const atr = this.calculateEMA(trueRanges, period);
    return atr;
  }

  /**
   * Calcula todas las métricas en una sola llamada
   * Útil para dashboards completos
   * 
   * @param {Array<Object>} data - Datos OHLCV
   * @returns {Object} {rsi, sma, volatility, macd, bollinger}
   */
  static calculateAll(data) {
    const closes = data.map(d => d.close);
    
    return {
      rsi: this.calculateRSI(closes, 14),
      sma20: this.calculateSMA(closes, 20),
      sma50: this.calculateSMA(closes, 50),
      ema12: this.calculateEMA(closes, 12),
      volatility: this.calculateVolatility(closes, 20),
      macd: this.calculateMACD(closes),
      bollinger: this.calculateBollingerBands(closes, 20, 2),
      atr: this.calculateATR(data, 14)
    };
  }
}

module.exports = TechnicalIndicators;