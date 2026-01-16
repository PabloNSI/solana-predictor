/**
 * ========================================
 * api/v1/chat.js
 * ========================================
 * 
 * Serverless Function (Vercel)
 * 
 * Flujo:
 * 1. Recibe prompt del usuario (POST)
 * 2. Parsea con NLP
 * 3. Carga datos históricos
 * 4. Calcula indicadores
 * 5. Formatea respuesta JSON
 * 6. Devuelve al frontend
 * 
 * Uso:
 * POST /api/v1/chat
 * Content-Type: application/json
 * 
 * {
 *   "prompt": "Muestra RSI últimos 14 días",
 *   "userId": "opcional-para-logging"
 * }
 * 
 * Respuesta:
 * {
 *   "status": "success|error",
 *   "response": {
 *     "message": "...",
 *     "visualization": {...},
 *     "analysis": {...}
 *   },
 *   "metadata": {...}
 * }
 */

const dataLoader = require('../utils/dataLoader');
const nlpParser = require('../utils/nlpParser');
const indicators = require('../utils/indicators');
const responseFormatter = require('../utils/responseFormatter');

// ========================================
// CORS + Headers
// ========================================
function setCORSHeaders(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Cache-Control', 'public, max-age=300'); // Cache 5 min
}

// ========================================
// Manejador Principal
// ========================================
module.exports = async (req, res) => {
  try {
    setCORSHeaders(res);

    // Preflight request (CORS)
    if (req.method === 'OPTIONS') {
      return res.status(200).end();
    }

    // Solo aceptar POST
    if (req.method !== 'POST') {
      return res.status(405).json(
        responseFormatter.error('Solo se aceptan requests POST', 'METHOD_NOT_ALLOWED')
      );
    }

    // ========================================
    // VALIDACIÓN DE INPUT
    // ========================================
    const { prompt, userId = 'anonymous' } = req.body;

    if (!prompt) {
      return res.status(400).json(
        responseFormatter.error('Campo "prompt" es requerido', 'MISSING_PROMPT')
      );
    }

    if (typeof prompt !== 'string' || prompt.length === 0) {
      return res.status(400).json(
        responseFormatter.error('Prompt debe ser un string no vacío', 'INVALID_PROMPT')
      );
    }

    if (prompt.length > 500) {
      return res.status(400).json(
        responseFormatter.error('Prompt muy largo (máx 500 caracteres)', 'PROMPT_TOO_LONG')
      );
    }

    console.log(`[CHAT] Usuario: ${userId} | Prompt: ${prompt.substring(0, 100)}`);

    // ========================================
    // PASO 1: Parsear con NLP
    // ========================================
    const parsed = nlpParser.parse(prompt);
    console.log(`[NLP] Intent: ${parsed.intent} | Confidence: ${parsed.confidence.toFixed(2)}`);

    if (!nlpParser.isValid(parsed, 0.2)) {
      const clarification = nlpParser.askForClarification(parsed);
      return res.status(400).json(
        responseFormatter.chatResponse(clarification)
      );
    }

    // ========================================
    // PASO 2: Cargar datos
    // ========================================
    let data;
    try {
      if (parsed.period && typeof parsed.period === 'object' && parsed.period.year) {
        // Cargar año específico
        data = dataLoader.getDataByYear(parsed.period.year);
      } else {
        // Cargar últimos N días
        const days = parsed.period || 30;
        data = dataLoader.getLastDays(days);
      }
    } catch (error) {
      return res.status(500).json(
        responseFormatter.error(`Error cargando datos: ${error.message}`, 'DATA_LOAD_ERROR')
      );
    }

    if (!data || data.length === 0) {
      return res.status(404).json(
        responseFormatter.error('No hay datos para ese período', 'NO_DATA')
      );
    }

    console.log(`[DATA] Cargados ${data.length} registros`);

    // ========================================
    // PASO 3: Calcular indicadores según intención
    // ========================================
    let analysis = null;
    let visualization = null;
    let message = '';

    try {
      const closes = data.map(d => d.close);
      const volumes = data.map(d => d.volume);
      const candleData = data.map(d => ({
        high: d.high,
        low: d.low,
        close: d.close
      }));

      switch (parsed.intent) {
        // ========================================
        // RSI (Relative Strength Index)
        // ========================================
        case 'rsi': {
          const rsiPeriod = nlpParser.extractNumber(prompt) || 14;
          const rsiValues = indicators.calculateRSI(closes, rsiPeriod);

          analysis = {
            metric: `RSI (${rsiPeriod})`,
            period: data.length,
            values: rsiValues,
            summary: {
              current: rsiValues[rsiValues.length - 1],
              min: Math.min(...rsiValues.filter(v => v !== null)),
              max: Math.max(...rsiValues.filter(v => v !== null)),
              mean: rsiValues
                .filter(v => v !== null)
                .reduce((a, b) => a + b) / rsiValues.filter(v => v !== null).length
            }
          };

          visualization = {
            type: 'line',
            title: `RSI (${rsiPeriod})`,
            data: data.map((d, i) => ({
              date: d.timestamp.toISOString().split('T')[0],
              value: rsiValues[i],
              overbought: 70,
              oversold: 30
            }))
          };

          // Interpretación
          const current = analysis.summary.current;
          if (current > 70) {
            message = `🔴 RSI en ${current.toFixed(1)}: Zona de **SOBRECOMPRA**. Posible corrección a la baja.`;
          } else if (current < 30) {
            message = `🟢 RSI en ${current.toFixed(1)}: Zona de **SOBREVENTA**. Posible rebote al alza.`;
          } else {
            message = `⚪ RSI en ${current.toFixed(1)}: Neutro. Tendencia indefinida.`;
          }
          break;
        }

        // ========================================
        // SMA (Simple Moving Average)
        // ========================================
        case 'sma': {
          const smaPeriod = nlpParser.extractNumber(prompt) || 20;
          const smaValues = indicators.calculateSMA(closes, smaPeriod);

          analysis = {
            metric: `SMA (${smaPeriod})`,
            period: data.length,
            values: smaValues,
            summary: {
              current: smaValues[smaValues.length - 1],
              vs_price: closes[closes.length - 1] - smaValues[smaValues.length - 1],
              trend: closes[closes.length - 1] > smaValues[smaValues.length - 1] ? 'alcista' : 'bajista'
            }
          };

          visualization = {
            type: 'line',
            title: `SMA (${smaPeriod})`,
            data: data.map((d, i) => ({
              date: d.timestamp.toISOString().split('T')[0],
              price: d.close,
              sma: smaValues[i]
            }))
          };

          const currentPrice = closes[closes.length - 1];
          const currentSMA = smaValues[smaValues.length - 1];
          const diff = ((currentPrice - currentSMA) / currentSMA * 100).toFixed(2);

          message = `📈 Precio actual: $${currentPrice.toFixed(3)} | SMA(${smaPeriod}): $${currentSMA.toFixed(3)} (${diff}% diferencia)`;
          break;
        }

        // ========================================
        // VOLATILIDAD
        // ========================================
        case 'volatility': {
          const volatility = indicators.calculateVolatility(closes, 20);
          
          analysis = {
            metric: 'Volatilidad Histórica',
            period: data.length,
            values: [volatility],
            summary: {
              volatility: volatility,
              annualized: (volatility * 100).toFixed(2) + '%',
              interpretation: volatility > 0.5 ? 'Alta' : volatility > 0.3 ? 'Media' : 'Baja'
            }
          };

          message = `📊 Volatilidad histórica (anualizada): **${(volatility * 100).toFixed(2)}%**\n` +
                    `Riesgo: ${analysis.summary.interpretation}`;
          break;
        }

        // ========================================
        // VOLUMEN
        // ========================================
        case 'volume': {
          analysis = {
            metric: 'Volumen de Trading',
            period: data.length,
            values: volumes,
            summary: {
              current: volumes[volumes.length - 1],
              average: volumes.reduce((a, b) => a + b) / volumes.length,
              total: volumes.reduce((a, b) => a + b),
              max: Math.max(...volumes)
            }
          };

          visualization = {
            type: 'bar',
            title: 'Volumen de Trading',
            data: data.map((d, i) => ({
              date: d.timestamp.toISOString().split('T')[0],
              volume: d.volume,
              trades: d.trades
            }))
          };

          const avgVol = analysis.summary.average;
          const currentVol = analysis.summary.current;
          const vs_avg = ((currentVol - avgVol) / avgVol * 100).toFixed(1);

          message = `📊 Volumen actual: ${currentVol.toLocaleString()} | ` +
                    `Promedio: ${avgVol.toLocaleString()} (${vs_avg}%)`;
          break;
        }

        // ========================================
        // MACD
        // ========================================
        case 'macd': {
          const macdData = indicators.calculateMACD(closes);

          analysis = {
            metric: 'MACD',
            period: data.length,
            values: macdData,
            summary: {
              macdCurrent: macdData.macd[macdData.macd.length - 1],
              signalCurrent: macdData.signal[macdData.signal.length - 1],
              histogramCurrent: macdData.histogram[macdData.histogram.length - 1]
            }
          };

          visualization = {
            type: 'line',
            title: 'MACD',
            data: data.map((d, i) => ({
              date: d.timestamp.toISOString().split('T')[0],
              macd: macdData.macd[i],
              signal: macdData.signal[i],
              histogram: macdData.histogram[i]
            }))
          };

          message = `📈 MACD: ${analysis.summary.macdCurrent?.toFixed(6)} | ` +
                    `Signal: ${analysis.summary.signalCurrent?.toFixed(6)} | ` +
                    `Histogram: ${analysis.summary.histogramCurrent?.toFixed(6)}`;
          break;
        }

        // ========================================
        // Por defecto: resumen
        // ========================================
        default: {
          const lastPrice = closes[closes.length - 1];
          const firstPrice = closes[0];
          const change = ((lastPrice - firstPrice) / firstPrice * 100).toFixed(2);

          analysis = {
            metric: 'Resumen Período',
            period: data.length,
            summary: {
              startDate: data[0].timestamp.toISOString().split('T')[0],
              endDate: data[data.length - 1].timestamp.toISOString().split('T')[0],
              startPrice: firstPrice,
              endPrice: lastPrice,
              change: change,
              high: Math.max(...closes),
              low: Math.min(...closes),
              avgVolume: volumes.reduce((a, b) => a + b) / volumes.length
            }
          };

          message = `📊 Resumen ${data.length} días: Precio ${firstPrice.toFixed(3)} → ${lastPrice.toFixed(3)} (${change}%)`;
        }
      }

    } catch (error) {
      console.error('[ERROR]', error);
      return res.status(500).json(
        responseFormatter.error(`Error calculando indicadores: ${error.message}`, 'CALCULATION_ERROR')
      );
    }

    // ========================================
    // PASO 4: Formatear y devolver respuesta
    // ========================================
    const response = {
      status: 'success',
      response: {
        message: message || `Análisis completado para ${data.length} registros`,
        visualization,
        analysis
      },
      metadata: {
        timestamp: new Date().toISOString(),
        recordsAnalyzed: data.length,
        parseConfidence: (parsed.confidence * 100).toFixed(0) + '%',
        intent: parsed.intent,
        period: typeof parsed.period === 'number' ? `${parsed.period} días` : parsed.period
      }
    };

    console.log(`[RESPONSE] Status: ${response.status} | Metric: ${parsed.intent}`);
    return res.status(200).json(response);

  } catch (error) {
    console.error('[FATAL ERROR]', error);
    return res.status(500).json(
      responseFormatter.error(
        `Error interno del servidor: ${error.message}`,
        'INTERNAL_SERVER_ERROR'
      )
    );
  }
};