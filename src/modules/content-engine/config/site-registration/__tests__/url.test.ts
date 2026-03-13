// TASK-005: URL normalisation + validation
// TDD: Tests first, based on F-001 US-001 acceptance criteria.

import { describe, it, expect } from 'vitest';
import { normaliseUrl } from '../url.js';

describe('normaliseUrl', () => {
  describe('protocol handling', () => {
    it('adds https:// when no protocol provided', () => {
      const result = normaliseUrl('example.com');
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toMatch(/^https:\/\//);
      }
    });

    it('preserves existing https://', () => {
      const result = normaliseUrl('https://example.com');
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe('https://example.com');
      }
    });

    it('upgrades http:// to https://', () => {
      const result = normaliseUrl('http://example.com');
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe('https://example.com');
      }
    });
  });

  describe('trailing slash', () => {
    it('strips trailing slash from root URL', () => {
      const result = normaliseUrl('https://example.com/');
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe('https://example.com');
      }
    });

    it('strips trailing slash from path URL', () => {
      const result = normaliseUrl('https://example.com/blog/');
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe('https://example.com/blog');
      }
    });
  });

  describe('hostname normalisation', () => {
    it('lowercases hostname', () => {
      const result = normaliseUrl('https://EXAMPLE.COM');
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe('https://example.com');
      }
    });

    it('strips default https port 443', () => {
      const result = normaliseUrl('https://example.com:443');
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe('https://example.com');
      }
    });

    it('strips default http port 80', () => {
      const result = normaliseUrl('http://example.com:80');
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe('https://example.com');
      }
    });

    it('preserves non-default ports', () => {
      const result = normaliseUrl('https://example.com:8080');
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe('https://example.com:8080');
      }
    });
  });

  describe('spec examples (F-001 US-001)', () => {
    it('normalises hairgenetix.com', () => {
      const result = normaliseUrl('hairgenetix.com');
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe('https://hairgenetix.com');
      }
    });

    it('normalises https://digitalbouwers.nl as-is', () => {
      const result = normaliseUrl('https://digitalbouwers.nl');
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe('https://digitalbouwers.nl');
      }
    });

    it('strips trailing slash from https://hairgenetix.com/', () => {
      const result = normaliseUrl('https://hairgenetix.com/');
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe('https://hairgenetix.com');
      }
    });
  });

  describe('invalid URLs', () => {
    it('rejects empty string', () => {
      const result = normaliseUrl('');
      expect(result.success).toBe(false);
    });

    it('rejects nonsense input', () => {
      const result = normaliseUrl('not a url!!!');
      expect(result.success).toBe(false);
    });

    it('rejects bare protocol', () => {
      const result = normaliseUrl('https://');
      expect(result.success).toBe(false);
    });
  });

  describe('idempotency', () => {
    it('normalising an already-normalised URL produces the same result', () => {
      const first = normaliseUrl('hairgenetix.com');
      expect(first.success).toBe(true);
      if (first.success) {
        const second = normaliseUrl(first.data);
        expect(second.success).toBe(true);
        if (second.success) {
          expect(second.data).toBe(first.data);
        }
      }
    });
  });

  describe('edge cases', () => {
    it('preserves path and query params', () => {
      const result = normaliseUrl('https://example.com/shop?ref=abc');
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe('https://example.com/shop?ref=abc');
      }
    });

    it('strips fragment (hash)', () => {
      const result = normaliseUrl('https://example.com/page#section');
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe('https://example.com/page');
      }
    });

    it('handles whitespace around URL', () => {
      const result = normaliseUrl('  example.com  ');
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe('https://example.com');
      }
    });
  });
});
