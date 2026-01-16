class ResponseFormatter {
  static success(data, metadata = {}) {
    return {
      status: 'success',
      data,
      metadata: {
        timestamp: new Date().toISOString(),
        ...metadata
      }
    };
  }

  static error(message, code = 'UNKNOWN_ERROR') {
    return {
      status: 'error',
      error: { code, message },
      metadata: { timestamp: new Date().toISOString() }
    };
  }

  static chatResponse(message, visualization = null, analysis = null) {
    return {
      status: 'success',
      response: { message, visualization, analysis },
      metadata: { timestamp: new Date().toISOString() }
    };
  }

  static analysisResult(metric, values, statistics = {}) {
    return {
      status: 'success',
      analysis: {
        metric,
        values,
        statistics
      },
      metadata: { timestamp: new Date().toISOString() }
    };
  }
}

module.exports = ResponseFormatter;