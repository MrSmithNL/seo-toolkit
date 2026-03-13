// TDD Red Phase — TASK-004: AES-256-GCM encryption utility
// Constitutional Constraint #1: CMS credentials must be encrypted at rest

import { describe, it, expect } from 'vitest';
import { encrypt, decrypt, deriveKey } from './encrypt.js';

describe('AES-256-GCM Encryption (TASK-004)', () => {
  const testKey = deriveKey('test-encryption-key-for-unit-tests');

  describe('encrypt', () => {
    it('should return iv, ciphertext, and tag', () => {
      const result = encrypt('my secret password', testKey);

      expect(result.iv).toBeDefined();
      expect(result.ciphertext).toBeDefined();
      expect(result.tag).toBeDefined();
      // IV should be 12 bytes = 24 hex chars
      expect(result.iv).toHaveLength(24);
      // Tag should be 16 bytes = 32 hex chars
      expect(result.tag).toHaveLength(32);
    });

    it('should produce different ciphertext for same plaintext (random IV)', () => {
      const a = encrypt('same input', testKey);
      const b = encrypt('same input', testKey);

      expect(a.ciphertext).not.toBe(b.ciphertext);
      expect(a.iv).not.toBe(b.iv);
    });

    it('should produce different ciphertext with different keys', () => {
      const keyA = deriveKey('key-alpha');
      const keyB = deriveKey('key-beta');

      const a = encrypt('same input', keyA);
      const b = encrypt('same input', keyB);

      expect(a.ciphertext).not.toBe(b.ciphertext);
    });
  });

  describe('decrypt', () => {
    it('should roundtrip — decrypt returns original plaintext', () => {
      const plaintext = 'wp_application_password_12345';
      const encrypted = encrypt(plaintext, testKey);
      const decrypted = decrypt(encrypted, testKey);

      expect(decrypted).toBe(plaintext);
    });

    it('should roundtrip with unicode content', () => {
      const plaintext = 'pässwörd_with_ünïcödé_🔐';
      const encrypted = encrypt(plaintext, testKey);
      const decrypted = decrypt(encrypted, testKey);

      expect(decrypted).toBe(plaintext);
    });

    it('should roundtrip with empty string', () => {
      const encrypted = encrypt('', testKey);
      const decrypted = decrypt(encrypted, testKey);

      expect(decrypted).toBe('');
    });

    it('should fail with wrong key (tamper detection)', () => {
      const encrypted = encrypt('secret', testKey);
      const wrongKey = deriveKey('wrong-key');

      expect(() => decrypt(encrypted, wrongKey)).toThrow();
    });

    it('should fail with modified ciphertext (integrity check)', () => {
      const encrypted = encrypt('secret', testKey);
      // Flip a character in the ciphertext
      const tampered = {
        ...encrypted,
        ciphertext: encrypted.ciphertext.slice(0, -2) + 'ff',
      };

      expect(() => decrypt(tampered, testKey)).toThrow();
    });

    it('should fail with modified tag', () => {
      const encrypted = encrypt('secret', testKey);
      const tampered = {
        ...encrypted,
        tag: '0'.repeat(32),
      };

      expect(() => decrypt(tampered, testKey)).toThrow();
    });
  });

  describe('deriveKey', () => {
    it('should produce a 32-byte key (256 bits)', () => {
      const key = deriveKey('any-passphrase');
      expect(key).toHaveLength(32);
    });

    it('should produce deterministic output for same input', () => {
      const a = deriveKey('same');
      const b = deriveKey('same');
      expect(a.equals(b)).toBe(true);
    });

    it('should produce different output for different input', () => {
      const a = deriveKey('alpha');
      const b = deriveKey('beta');
      expect(a.equals(b)).toBe(false);
    });
  });
});
