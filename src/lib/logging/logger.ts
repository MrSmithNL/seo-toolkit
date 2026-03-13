// Structured logging — pino with PII redaction (TASK-F03)
// NFR 21: JSON structured logging, NFR 28: PII redaction at log boundary

import pino from 'pino';

interface LoggerOptions {
  name: string;
  level?: string;
  destination?: { write(msg: string): void };
}

const PII_PATHS = [
  'password',
  'token',
  'secret',
  'accessToken',
  'email',
  'phone',
  'ip',
  '*.password',
  '*.token',
  '*.secret',
  '*.accessToken',
  '*.email',
  '*.phone',
  '*.ip',
];

export function createLogger(options: LoggerOptions) {
  const { name, level = 'debug', destination } = options;

  const pinoOptions: pino.LoggerOptions = {
    name,
    level,
    timestamp: pino.stdTimeFunctions.isoTime,
    redact: {
      paths: PII_PATHS,
      censor: '[REDACTED]',
    },
  };

  if (destination) {
    return pino(pinoOptions, destination as pino.DestinationStream);
  }

  return pino(pinoOptions);
}
