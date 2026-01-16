/**
 * ========================================
 * api/utils/nlpParser.js
 * ========================================
 * 
 * Parser NLP Híbrido:
 * - Reglas basadas en patrones (regex)
 * - Extracción de intenciones
 * - Resolución de parámetros temporales
 * - Manejo de ambigüedades
 * 
 * Enfoque: Simple pero efectivo
 * NO usa ML, solo pattern matching
 * Fácil de debugear y mantener
 */

class NLPParser {
  constructor() {
    // Mapeo de palabras clave → intenciones
    this.intentPatterns = {
      price: {
        keywords: ['precio', 'cierre', 'close', 'costo', 'valor', 'cotización'],
        regex: /precio|cierre|close|costo|valor|cotización/i
      },
      volume: {
        keywords: ['volumen', 'trading volume', 'operaciones', 'transacciones'],
        regex: /volumen|volume|operaciones|transacciones/i
      },
      rsi: {
        keywords: ['rsi', 'fortaleza relativa', 'índice de fuerza relativa'],
        regex: /rsi|fortaleza relativa|índice de fuerza/i
      },
      sma: {
        keywords: ['media móvil', 'sma', 'promedio', 'moving average'],
        regex: /media móvil|sma|promedio|moving average/i
      },
      ema: {
        keywords: ['ema', 'media exponencial'],
        regex: /ema|media exponencial/i
      },
      volatility: {
        keywords: ['volatilidad', 'desviación', 'variabilidad', 'volatility'],
        regex: /volatilidad|desviación|variabilidad|volatility/i
      },
      macd: {
        keywords: ['macd', 'convergencia divergencia'],
        regex: /macd|convergencia|divergencia/i
      },
      bollinger: {
        keywords: ['bollinger', 'bandas'],
        regex: /bollinger|bandas/i
      },
      comparison: {
        keywords: ['comparar', 'versus', 'vs', 'diferencia entre'],
        regex: /comparar|versus|vs|diferencia entre/i
      },
      correlation: {
        keywords: ['correlación', 'relación', 'entre'],
        regex: /correlación|relación entre/i
      }
    };

    // Patrones de tiempo
    this.timePatterns = {
      // Últimos N días
      'últimos 7 días': 7,
      'últimas 7 días': 7,
      'últimos 7d': 7,
      '7 días': 7,
      '7d': 7,
      'una semana': 7,

      'últimos 14 días': 14,
      'últimas 14 días': 14,
      'dos semanas': 14,

      'últimos 30 días': 30,
      'últimas 4 semanas': 30,
      'un mes': 30,
      'este mes': 30,

      'últimos 90 días': 90,
      'trimestre': 90,

      'últimos 365 días': 365,
      'un año': 365,
      'este año': 365,
      'anual': 365,

      // Años específicos
      '2020': { year: 2020 },
      '2021': { year: 2021 },
      '2022': { year: 2022 },
      '2023': { year: 2023 },
      '2024': { year: 2024 },
      '2025': { year: 2025 }
    };

    this.defaultPeriod = 30; // días
  }

  /**
   * Parsea un prompt en español y extrae:
   * - Intención (qué quiere el usuario)
   * - Métrica (precio, RSI, SMA, etc)
   * - Período temporal
   * - Confianza
   * 
   * @param {string} prompt - Texto del usuario
   * @returns {Object} {intent, metric, period, confidence, rawPrompt}
   */
  parse(prompt) {
    if (!prompt || typeof prompt !== 'string') {
      return {
        intent: null,
        metric: null,
        period: null,
        confidence: 0,
        rawPrompt: prompt
      };
    }

    const normalized = prompt.toLowerCase().trim();

    const result = {
      intent: null,
      metric: null,
      period: this.defaultPeriod,
      confidence: 0,
      rawPrompt: prompt,
      debug: {}
    };

    // ========================================
    // PASO 1: Detectar intención
    // ========================================
    let maxConfidence = 0;
    let matchedIntent = null;

    for (const [intent, pattern] of Object.entries(this.intentPatterns)) {
      if (pattern.regex.test(normalized)) {
        // Contar coincidencias de palabras clave
        const keywordMatches = pattern.keywords.filter(kw => 
          normalized.includes(kw.toLowerCase())
        ).length;

        const confidence = Math.min(0.5 + (keywordMatches * 0.1), 1.0);

        if (confidence > maxConfidence) {
          maxConfidence = confidence;
          matchedIntent = intent;
        }
      }
    }

    if (matchedIntent) {
      result.intent = matchedIntent;
      result.metric = matchedIntent;
      result.confidence = maxConfidence;
      result.debug.intent = `Detectada intención: ${matchedIntent} (confianza: ${maxConfidence.toFixed(2)})`;
    }

    // ========================================
    // PASO 2: Detectar período temporal
    // ========================================
    let foundPeriod = false;

    for (const [pattern, days] of Object.entries(this.timePatterns)) {
      if (normalized.includes(pattern)) {
        if (typeof days === 'number') {
          result.period = days;
        } else if (typeof days === 'object') {
          result.period = days; // {year: 2021}
        }
        foundPeriod = true;
        result.debug.period = `Período detectado: ${pattern} → ${days}`;
        break;
      }
    }

    // Si no encuentra período explícito, busca números
    if (!foundPeriod) {
      const numberMatch = normalized.match(/(\d+)\s*(días?|d\b|semanas?|meses?|años?)/);
      if (numberMatch) {
        const num = parseInt(numberMatch[1]);
        const unit = numberMatch[2].toLowerCase();

        if (unit.startsWith('d')) result.period = num;
        else if (unit.startsWith('semana')) result.period = num * 7;
        else if (unit.startsWith('mes')) result.period = num * 30;
        else if (unit.startsWith('año')) result.period = num * 365;

        result.debug.period = `Período calculado: ${num} ${unit} → ${result.period} días`;
      }
    }

    // ========================================
    // PASO 3: Validar resultado
    // ========================================
    if (!result.intent) {
      result.intent = 'explore';
      result.confidence = 0.2;
      result.debug.warning = 'No se detectó intención clara. Modo exploración.';
    }

    return result;
  }

  /**
   * Valida si el parse tiene confianza suficiente
   * 
   * @param {Object} parsed - Resultado del parse
   * @param {number} threshold - Confianza mínima (default: 0.3)
   * @returns {boolean}
   */
  isValid(parsed, threshold = 0.3) {
    return parsed.confidence >= threshold;
  }

  /**
   * Genera una pregunta de clarificación
   * 
   * @param {Object} parsed - Resultado del parse
   * @returns {string}
   */
  askForClarification(parsed) {
    if (parsed.confidence < 0.3) {
      return `No entendí bien tu pregunta.\n\nPuedes preguntarme sobre:\n` +
             `• "Precio del último mes"\n` +
             `• "RSI últimos 14 días"\n` +
             `• "Volumen en 2023"\n` +
             `• "Volatilidad últimos 90 días"\n\n` +
             `¿Qué te gustaría analizar?`;
    }

    if (!parsed.metric) {
      return `Detecté que quieres explorar, pero no especificaste la métrica.\n` +
             `¿Prefieres: precio, volumen, RSI, SMA, volatilidad o MACD?`;
    }

    return `Entendí "${parsed.metric}", pero el período es ambiguo.\n` +
           `Especifica: "últimos 7 días", "últimos 30 días", "2023", etc.`;
  }

  /**
   * Extrae solo números del prompt
   * Útil para parámetros como período RSI
   * 
   * @param {string} prompt - Texto
   * @returns {number|null}
   */
  extractNumber(prompt) {
    const match = prompt.match(/\d+/);
    return match ? parseInt(match[0]) : null;
  }

  /**
   * Genera una traducción "legible" del parse
   * Útil para debugging y feedback al usuario
   * 
   * @param {Object} parsed - Resultado del parse
   * @returns {string}
   */
  explain(parsed) {
    const parts = [];

    if (parsed.intent) {
      parts.push(`📊 Analizaré: ${parsed.metric || parsed.intent}`);
    }

    if (parsed.period && typeof parsed.period === 'number') {
      parts.push(`📅 Período: últimos ${parsed.period} días`);
    } else if (parsed.period && parsed.period.year) {
      parts.push(`📅 Período: año ${parsed.period.year}`);
    }

    parts.push(`🎯 Confianza: ${(parsed.confidence * 100).toFixed(0)}%`);

    return parts.join('\n');
  }

  /**
   * Sugiere la próxima pregunta basada en la anterior
   * 
   * @param {Object} parsed - Resultado anterior
   * @returns {Array<string>}
   */
  suggestFollowUp(parsed) {
    const suggestions = [];

    if (parsed.intent === 'price') {
      suggestions.push('¿Quieres ver la volatilidad en ese período?');
      suggestions.push('¿Y el RSI? Para detectar sobreventa/sobrecompra');
    }

    if (parsed.intent === 'rsi') {
      suggestions.push('¿Ves zonas de sobreventa (RSI < 30)?');
      suggestions.push('¿Comparamos con SMA para confirmación?');
    }

    if (parsed.intent === 'volume') {
      suggestions.push('¿Quieres correlacionar volumen con precio?');
      suggestions.push('¿Hay picos de volumen significativos?');
    }

    return suggestions;
  }
}

module.exports = new NLPParser();