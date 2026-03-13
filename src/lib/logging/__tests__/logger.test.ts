// TASK-F03: Structured logging — pino with PII redaction
// TDD: Write tests first, confirm they fail, then implement.

import { describe, it, expect, beforeEach } from 'vitest';
import { createLogger } from '../logger.js';

describe('Structured Logger', () => {
  // Capture pino output by using a writable stream
  let output: string[];
  let logger: ReturnType<typeof createLogger>;

  beforeEach(() => {
    output = [];
    logger = createLogger({
      name: 'test-service',
      destination: {
        write(msg: string) {
          output.push(msg);
        },
      },
    });
  });

  function lastLog(): Record<string, unknown> {
    const last = output.at(-1);
    if (!last) throw new Error('No log output captured');
    return JSON.parse(last) as Record<string, unknown>;
  }

  describe('basic logging', () => {
    it('outputs JSON with standard fields', () => {
      logger.info('hello world');
      const log = lastLog();

      expect(log).toHaveProperty('level');
      expect(log).toHaveProperty('time');
      expect(log).toHaveProperty('msg', 'hello world');
      expect(log).toHaveProperty('name', 'test-service');
    });

    it('supports structured data alongside message', () => {
      logger.info({ userId: 'usr_123', action: 'login' }, 'user logged in');
      const log = lastLog();

      expect(log).toHaveProperty('userId', 'usr_123');
      expect(log).toHaveProperty('action', 'login');
      expect(log).toHaveProperty('msg', 'user logged in');
    });

    it('supports all log levels', () => {
      logger.debug('debug msg');
      logger.info('info msg');
      logger.warn('warn msg');
      logger.error('error msg');

      expect(output.length).toBe(4);
    });
  });

  describe('PII redaction', () => {
    it('redacts password fields', () => {
      logger.info({ password: 'secret123' }, 'login attempt');
      const log = lastLog();

      expect(log).toHaveProperty('password', '[REDACTED]');
    });

    it('redacts token fields', () => {
      logger.info({ token: 'abc-token-xyz' }, 'auth check');
      const log = lastLog();

      expect(log).toHaveProperty('token', '[REDACTED]');
    });

    it('redacts secret fields', () => {
      logger.info({ secret: 'my-secret' }, 'config loaded');
      const log = lastLog();

      expect(log).toHaveProperty('secret', '[REDACTED]');
    });

    it('redacts accessToken fields', () => {
      logger.info({ accessToken: 'shopify-token' }, 'cms connect');
      const log = lastLog();

      expect(log).toHaveProperty('accessToken', '[REDACTED]');
    });

    it('redacts email fields', () => {
      logger.info({ email: 'user@example.com' }, 'user registered');
      const log = lastLog();

      expect(log).toHaveProperty('email', '[REDACTED]');
    });

    it('redacts phone fields', () => {
      logger.info({ phone: '+31612345678' }, 'contact info');
      const log = lastLog();

      expect(log).toHaveProperty('phone', '[REDACTED]');
    });

    it('redacts ip fields', () => {
      logger.info({ ip: '192.168.1.1' }, 'request received');
      const log = lastLog();

      expect(log).toHaveProperty('ip', '[REDACTED]');
    });

    it('redacts nested PII fields', () => {
      logger.info({ credentials: { password: 'secret', token: 'tok' } }, 'nested');
      const log = lastLog();
      const creds = log['credentials'] as Record<string, unknown>;

      expect(creds).toHaveProperty('password', '[REDACTED]');
      expect(creds).toHaveProperty('token', '[REDACTED]');
    });

    it('does not redact non-PII fields', () => {
      logger.info({ siteId: 'ste_abc123', action: 'register' }, 'safe data');
      const log = lastLog();

      expect(log).toHaveProperty('siteId', 'ste_abc123');
      expect(log).toHaveProperty('action', 'register');
    });
  });

  describe('operation context', () => {
    it('includes tenantId and correlationId when provided via child logger', () => {
      const child = logger.child({ tenantId: 'tnt_abc', correlationId: 'corr_123' });
      child.info('tenant operation');
      const log = lastLog();

      expect(log).toHaveProperty('tenantId', 'tnt_abc');
      expect(log).toHaveProperty('correlationId', 'corr_123');
      expect(log).toHaveProperty('msg', 'tenant operation');
    });
  });

  describe('ISO 8601 timestamps', () => {
    it('outputs ISO 8601 formatted time', () => {
      logger.info('timestamp test');
      const log = lastLog();
      const time = log['time'] as string;

      // ISO 8601 pattern: YYYY-MM-DDTHH:mm:ss.sssZ
      expect(time).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/);
    });
  });
});
