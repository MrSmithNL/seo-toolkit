// AES-256-GCM encryption utility — Constitutional Constraint #1
// CMS credentials (WordPress passwords, Shopify tokens) encrypted at rest.
// Uses Node.js built-in crypto — no external dependencies.

import { createCipheriv, createDecipheriv, randomBytes, createHash } from 'node:crypto';

const ALGORITHM = 'aes-256-gcm' as const;
const IV_LENGTH = 12; // 96 bits — recommended for GCM
const TAG_LENGTH = 16; // 128 bits

export interface EncryptedData {
  readonly iv: string;         // hex-encoded 12 bytes
  readonly ciphertext: string; // hex-encoded
  readonly tag: string;        // hex-encoded 16 bytes
}

export function encrypt(plaintext: string, key: Buffer): EncryptedData {
  const iv = randomBytes(IV_LENGTH);
  const cipher = createCipheriv(ALGORITHM, key, iv, { authTagLength: TAG_LENGTH });

  const encrypted = Buffer.concat([
    cipher.update(plaintext, 'utf8'),
    cipher.final(),
  ]);

  return {
    iv: iv.toString('hex'),
    ciphertext: encrypted.toString('hex'),
    tag: cipher.getAuthTag().toString('hex'),
  };
}

export function decrypt(data: EncryptedData, key: Buffer): string {
  const decipher = createDecipheriv(
    ALGORITHM,
    key,
    Buffer.from(data.iv, 'hex'),
    { authTagLength: TAG_LENGTH },
  );

  decipher.setAuthTag(Buffer.from(data.tag, 'hex'));

  const decrypted = Buffer.concat([
    decipher.update(Buffer.from(data.ciphertext, 'hex')),
    decipher.final(),
  ]);

  return decrypted.toString('utf8');
}

export function deriveKey(passphrase: string): Buffer {
  // SHA-256 produces exactly 32 bytes = 256 bits for AES-256
  return createHash('sha256').update(passphrase).digest();
}
