// CMS connection service (TASK-012)
// Orchestrates adapter selection, credential encryption, verification, persistence.

import { generateId } from '../../../../lib/id.js';
import { type Result, type OperationError, ok, err, operationError } from '../../../../lib/result.js';
import type { OperationContext } from '../../../../lib/context.js';
import { encrypt, deriveKey } from '../../../../lib/crypto/encrypt.js';
import type { CmsRepository, CmsConnectionRecord } from './cms.repository.js';

interface ConnectInput {
  siteId: string;
  cmsType: 'wordpress' | 'shopify';
  wpSiteUrl?: string;
  wpUsername?: string;
  wpApplicationPassword?: string;
  shopifyStoreDomain?: string;
  shopifyAccessToken?: string;
}

function encryptField(value: string | undefined, key: Buffer): string | undefined {
  if (!value) return undefined;
  const encrypted = encrypt(value, key);
  return JSON.stringify(encrypted);
}

export class CmsService {
  private readonly encKey: Buffer;

  constructor(
    private readonly repository: CmsRepository,
    encryptionKey: string,
  ) {
    this.encKey = deriveKey(encryptionKey);
  }

  async connect(
    input: ConnectInput,
    _ctx: OperationContext,
  ): Promise<Result<CmsConnectionRecord, OperationError>> {
    // Check for existing connection
    const existing = await this.repository.findBySiteId(input.siteId);
    if (existing) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/conflict',
        title: 'CMS Already Connected',
        status: 409,
        detail: `Site ${input.siteId} already has a CMS connection`,
        suggestedAction: 'Remove the existing connection first',
      }));
    }

    // Encrypt credentials before storage
    const record = await this.repository.create({
      id: generateId('cmsConnection'),
      siteId: input.siteId,
      cmsType: input.cmsType,
      wpSiteUrl: input.wpSiteUrl,
      wpUsername: input.wpUsername,
      wpApplicationPassword: encryptField(input.wpApplicationPassword, this.encKey),
      shopifyStoreDomain: input.shopifyStoreDomain,
      shopifyAccessToken: encryptField(input.shopifyAccessToken, this.encKey),
    });

    return ok(record);
  }

  async getConnection(
    siteId: string,
    _ctx: OperationContext,
  ): Promise<Result<CmsConnectionRecord, OperationError>> {
    const conn = await this.repository.findBySiteId(siteId);

    if (!conn) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/not-found',
        title: 'CMS Connection Not Found',
        status: 404,
        detail: `No CMS connection found for site ${siteId}`,
        suggestedAction: 'Connect a CMS first',
      }));
    }

    return ok(conn);
  }

  async updateStatus(
    connectionId: string,
    status: string,
    _ctx: OperationContext,
  ): Promise<Result<CmsConnectionRecord, OperationError>> {
    const verifiedAt = status === 'verified' ? new Date().toISOString() : undefined;
    const updated = await this.repository.updateStatus(connectionId, status, verifiedAt);
    return ok(updated);
  }
}
