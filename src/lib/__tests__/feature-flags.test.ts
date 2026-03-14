import { describe, it, expect } from 'vitest';
import { isEnabled, assertEnabled } from '../feature-flags.js';

describe('Feature Flags', () => {
  it('content-engine-v1 is enabled', () => {
    expect(isEnabled('content-engine-v1')).toBe(true);
  });

  it('assertEnabled does not throw for enabled flags', () => {
    expect(() => assertEnabled('content-engine-v1')).not.toThrow();
  });
});
