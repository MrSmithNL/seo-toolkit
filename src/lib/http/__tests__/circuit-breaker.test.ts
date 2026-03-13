// TASK-F04: Circuit breaker for external HTTP calls
// TDD: Tests first — verify open/closed/half-open state transitions.

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { CircuitBreaker, CircuitState } from '../circuit-breaker.js';

describe('CircuitBreaker', () => {
  let breaker: CircuitBreaker;

  beforeEach(() => {
    vi.useFakeTimers();
    breaker = new CircuitBreaker({
      failureThreshold: 3,    // fewer for faster tests
      windowMs: 60_000,       // 60s failure window
      resetTimeoutMs: 30_000, // 30s open → half-open
      name: 'test-breaker',
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('closed state (normal operation)', () => {
    it('starts in closed state', () => {
      expect(breaker.state).toBe(CircuitState.Closed);
    });

    it('executes function successfully when closed', async () => {
      const result = await breaker.execute(() => Promise.resolve('ok'));
      expect(result).toBe('ok');
    });

    it('stays closed on success', async () => {
      await breaker.execute(() => Promise.resolve('ok'));
      expect(breaker.state).toBe(CircuitState.Closed);
    });

    it('stays closed below failure threshold', async () => {
      // 2 failures, threshold is 3
      for (let i = 0; i < 2; i++) {
        await breaker.execute(() => Promise.reject(new Error('fail'))).catch(() => {});
      }
      expect(breaker.state).toBe(CircuitState.Closed);
    });
  });

  describe('transition to open state', () => {
    it('opens after reaching failure threshold', async () => {
      for (let i = 0; i < 3; i++) {
        await breaker.execute(() => Promise.reject(new Error('fail'))).catch(() => {});
      }
      expect(breaker.state).toBe(CircuitState.Open);
    });

    it('rejects calls immediately when open', async () => {
      // Trip the breaker
      for (let i = 0; i < 3; i++) {
        await breaker.execute(() => Promise.reject(new Error('fail'))).catch(() => {});
      }

      await expect(
        breaker.execute(() => Promise.resolve('should not run')),
      ).rejects.toThrow('Circuit breaker "test-breaker" is open');
    });

    it('does not call the function when open', async () => {
      for (let i = 0; i < 3; i++) {
        await breaker.execute(() => Promise.reject(new Error('fail'))).catch(() => {});
      }

      const fn = vi.fn(() => Promise.resolve('nope'));
      await breaker.execute(fn).catch(() => {});
      expect(fn).not.toHaveBeenCalled();
    });
  });

  describe('half-open state (recovery probe)', () => {
    it('transitions to half-open after reset timeout', async () => {
      // Trip the breaker
      for (let i = 0; i < 3; i++) {
        await breaker.execute(() => Promise.reject(new Error('fail'))).catch(() => {});
      }
      expect(breaker.state).toBe(CircuitState.Open);

      // Advance past reset timeout
      vi.advanceTimersByTime(30_001);

      expect(breaker.state).toBe(CircuitState.HalfOpen);
    });

    it('closes on successful probe in half-open', async () => {
      // Trip → wait → half-open
      for (let i = 0; i < 3; i++) {
        await breaker.execute(() => Promise.reject(new Error('fail'))).catch(() => {});
      }
      vi.advanceTimersByTime(30_001);

      // Successful call in half-open → back to closed
      await breaker.execute(() => Promise.resolve('recovered'));
      expect(breaker.state).toBe(CircuitState.Closed);
    });

    it('re-opens on failure in half-open', async () => {
      // Trip → wait → half-open
      for (let i = 0; i < 3; i++) {
        await breaker.execute(() => Promise.reject(new Error('fail'))).catch(() => {});
      }
      vi.advanceTimersByTime(30_001);
      expect(breaker.state).toBe(CircuitState.HalfOpen);

      // Failure in half-open → back to open
      await breaker.execute(() => Promise.reject(new Error('still broken'))).catch(() => {});
      expect(breaker.state).toBe(CircuitState.Open);
    });
  });

  describe('failure window expiry', () => {
    it('resets failure count when window expires', async () => {
      // 2 failures
      await breaker.execute(() => Promise.reject(new Error('fail'))).catch(() => {});
      await breaker.execute(() => Promise.reject(new Error('fail'))).catch(() => {});

      // Window expires
      vi.advanceTimersByTime(60_001);

      // 1 more failure should NOT trip (counter reset)
      await breaker.execute(() => Promise.reject(new Error('fail'))).catch(() => {});
      expect(breaker.state).toBe(CircuitState.Closed);
    });
  });

  describe('success resets failure count', () => {
    it('resets failures on successful call', async () => {
      // 2 failures
      await breaker.execute(() => Promise.reject(new Error('fail'))).catch(() => {});
      await breaker.execute(() => Promise.reject(new Error('fail'))).catch(() => {});

      // Success resets
      await breaker.execute(() => Promise.resolve('ok'));

      // 2 more failures should NOT trip
      await breaker.execute(() => Promise.reject(new Error('fail'))).catch(() => {});
      await breaker.execute(() => Promise.reject(new Error('fail'))).catch(() => {});
      expect(breaker.state).toBe(CircuitState.Closed);
    });
  });

  describe('error propagation', () => {
    it('propagates the original error when closed', async () => {
      await expect(
        breaker.execute(() => Promise.reject(new Error('original error'))),
      ).rejects.toThrow('original error');
    });

    it('wraps circuit open error with breaker name', async () => {
      for (let i = 0; i < 3; i++) {
        await breaker.execute(() => Promise.reject(new Error('fail'))).catch(() => {});
      }

      try {
        await breaker.execute(() => Promise.resolve('nope'));
        expect.fail('should have thrown');
      } catch (e) {
        expect((e as Error).message).toContain('test-breaker');
        expect((e as Error).message).toContain('open');
      }
    });
  });
});
