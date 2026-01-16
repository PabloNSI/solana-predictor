/**
 * ========================================
 * api/utils/dataLoader.js
 * ========================================
 * 
 * Módulo Singleton para cargar y cachear datos OHLCV
 * Optimizado para serverless (Vercel cold-start)
 * 
 * Responsabilidades:
 * - Carga CSV (una sola vez)
 * - Parseo y validación de datos
 * - Filtrado por rango de fechas
 * - Caché en memoria
 */

const fs = require('fs');
const path = require('path');
const Papa = require('papaparse');

class DataLoader {
  constructor() {
    this.data = null;
    this.lastLoaded = null;
    this.cacheTimeout = 3600000; // 1 hora
  }

  /**
   * Carga el dataset CSV del filesystem
   * Ejecuta una sola vez gracias al patrón Singleton
   * 
   * @returns {Array<Object>} Array de registros OHLCV normalizados
   * @throws {Error} Si no puede leer el archivo
   */
  loadData() {
    // Si está en caché y es reciente, devuelve caché
    if (this.data && Date.now() - this.lastLoaded < this.cacheTimeout) {
      console.log('[DataLoader] Usando datos en caché');
      return this.data;
    }

    try {
      const csvPath = path.join(__dirname, '../data/solana_ohlcv.csv');
      
      // Validar que el archivo existe
      if (!fs.existsSync(csvPath)) {
        throw new Error(`Dataset no encontrado en ${csvPath}`);
      }

      const csvContent = fs.readFileSync(csvPath, 'utf-8');
      
      // Parsear CSV con PapaParse
      const parsed = Papa.parse(csvContent, {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true,
        transformHeader: (h) => h.trim() // Elimina espacios en headers
      });

      if (parsed.errors && parsed.errors.length > 0) {
        console.warn('[DataLoader] Warnings al parsear CSV:', parsed.errors);
      }

      // Normalizar y validar datos
      this.data = parsed.data
        .filter(row => {
          // Validar que tenga los campos obligatorios
          return row['Open time'] && 
                 row['Close'] && 
                 !isNaN(parseFloat(row['Close']));
        })
        .map(row => {
          // Normalizar tipos y nombres de campos
          return {
            timestamp: new Date(row['Open time']),
            open: parseFloat(row['Open']) || 0,
            high: parseFloat(row['High']) || 0,
            low: parseFloat(row['Low']) || 0,
            close: parseFloat(row['Close']) || 0,
            volume: parseFloat(row['Volume']) || 0,
            trades: parseInt(row['Number of trades']) || 0,
            takerBuyVolume: parseFloat(row['Taker buy base asset volume']) || 0,
            takerBuyQuoteVolume: parseFloat(row['Taker buy quote asset volume']) || 0
          };
        })
        .sort((a, b) => a.timestamp - b.timestamp);

      this.lastLoaded = Date.now();
      
      console.log(`[DataLoader] Cargados ${this.data.length} registros desde ${this.data[0].timestamp.toISOString()} hasta ${this.data[this.data.length-1].timestamp.toISOString()}`);
      
      return this.data;

    } catch (error) {
      throw new Error(`[DataLoader] Error cargando datos: ${error.message}`);
    }
  }

  /**
   * Obtiene datos dentro de un rango de fechas
   * 
   * @param {Date} startDate - Fecha inicio (inclusive)
   * @param {Date} endDate - Fecha fin (inclusive)
   * @returns {Array<Object>} Registros filtrados
   */
  getDataRange(startDate, endDate) {
    const data = this.loadData();
    return data.filter(d => 
      d.timestamp >= startDate && d.timestamp <= endDate
    );
  }

  /**
   * Obtiene los últimos N días de datos
   * 
   * @param {number} days - Número de días (default: 30)
   * @returns {Array<Object>} Últimos N registros
   */
  getLastDays(days = 30) {
    const data = this.loadData();
    const result = data.slice(-days);
    
    if (result.length === 0) {
      throw new Error(`No hay datos para los últimos ${days} días`);
    }
    
    return result;
  }

  /**
   * Obtiene datos de un año específico
   * 
   * @param {number} year - Año (ej: 2021, 2022)
   * @returns {Array<Object>} Registros del año
   */
  getDataByYear(year) {
    const data = this.loadData();
    return data.filter(d => d.timestamp.getFullYear() === year);
  }

  /**
   * Obtiene estadísticas del dataset
   * 
   * @returns {Object} {recordCount, startDate, endDate, yearsAvailable}
   */
  getStats() {
    const data = this.loadData();
    const years = new Set(data.map(d => d.timestamp.getFullYear()));
    
    return {
      recordCount: data.length,
      startDate: data[0].timestamp,
      endDate: data[data.length - 1].timestamp,
      yearsAvailable: Array.from(years).sort(),
      priceRange: {
        min: Math.min(...data.map(d => d.low)),
        max: Math.max(...data.map(d => d.high))
      }
    };
  }

  /**
   * Limpia el caché (útil para testing)
   */
  clearCache() {
    this.data = null;
    this.lastLoaded = null;
    console.log('[DataLoader] Caché limpiado');
  }
}

// Exportar como Singleton
module.exports = new DataLoader();