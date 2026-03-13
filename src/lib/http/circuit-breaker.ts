// Circuit breaker for external HTTP calls (TASK-F04)
// NFR 29: Resilience pattern — prevents cascading failures from unreachable services.
// States: Closed (normal) → Open (blocking) → Half-Open (probe) → Closed/Open

export enum CircuitState {
  Closed = 'closed',
  Open = 'open',
  HalfOpen = 'half-open',
}

interface CircuitBreakerOptions {
  /** Number of failures within window to trip the breaker */
  failureThreshold: number;
  /** Time window for counting failures (ms) */
  windowMs: number;
  /** Time to wait before allowing a probe request (ms) */
  resetTimeoutMs: number;
  /** Name for logging/error messages */
  name: string;
}

export class CircuitBreaker {
  private _state = CircuitState.Closed;
  private failureCount = 0;
  private lastFailureTime = 0;
  private openedAt = 0;

  constructor(private readonly options: CircuitBreakerOptions) {}

  get state(): CircuitState {
    if (this._state === CircuitState.Open) {
      const elapsed = Date.now() - this.openedAt;
      if (elapsed > this.options.resetTimeoutMs) {
        this._state = CircuitState.HalfOpen;
      }
    }
    return this._state;
  }

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    const currentState = this.state;

    if (currentState === CircuitState.Open) {
      throw new Error(`Circuit breaker "${this.options.name}" is open`);
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onSuccess(): void {
    this.failureCount = 0;
    this._state = CircuitState.Closed;
  }

  private onFailure(): void {
    const now = Date.now();

    // Reset counter if outside the failure window
    if (this.lastFailureTime > 0 && now - this.lastFailureTime > this.options.windowMs) {
      this.failureCount = 0;
    }

    this.failureCount++;
    this.lastFailureTime = now;

    if (this.failureCount >= this.options.failureThreshold) {
      this._state = CircuitState.Open;
      this.openedAt = now;
    }
  }
}
