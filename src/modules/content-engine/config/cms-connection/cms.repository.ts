// CMS connection repository (TASK-012)

import { eq, sql } from 'drizzle-orm';
import { cmsConnection } from '../../../../db/schema.js';
import type { DrizzleDB } from '../../../../db/index.js';

export interface CmsConnectionRecord {
  readonly id: string;
  readonly siteId: string;
  readonly cmsType: string;
  readonly status: string | null;
  readonly wpSiteUrl: string | null;
  readonly wpUsername: string | null;
  readonly wpApplicationPassword: string | null;
  readonly shopifyStoreDomain: string | null;
  readonly shopifyAccessToken: string | null;
  readonly defaultPublishStatus: string | null;
  readonly verifiedAt: string | null;
  readonly lastUsedAt: string | null;
  readonly createdAt: string;
  readonly updatedAt: string;
}

export class CmsRepository {
  constructor(private readonly db: DrizzleDB) {}

  async create(record: {
    id: string;
    siteId: string;
    cmsType: string;
    wpSiteUrl?: string;
    wpUsername?: string;
    wpApplicationPassword?: string;
    shopifyStoreDomain?: string;
    shopifyAccessToken?: string;
  }): Promise<CmsConnectionRecord> {
    const rows = this.db
      .insert(cmsConnection)
      .values(record)
      .returning()
      .all();

    const row = rows[0];
    if (!row) throw new Error('Insert returned no rows');
    return row;
  }

  async findBySiteId(siteId: string): Promise<CmsConnectionRecord | undefined> {
    const rows = this.db
      .select()
      .from(cmsConnection)
      .where(eq(cmsConnection.siteId, siteId))
      .all();

    return rows[0];
  }

  async updateStatus(id: string, status: string, verifiedAt?: string): Promise<CmsConnectionRecord> {
    const rows = this.db
      .update(cmsConnection)
      .set({
        status,
        verifiedAt: verifiedAt ?? null,
        updatedAt: sql`(datetime('now'))`,
      })
      .where(eq(cmsConnection.id, id))
      .returning()
      .all();

    const row = rows[0];
    if (!row) throw new Error('Update returned no rows');
    return row;
  }
}
