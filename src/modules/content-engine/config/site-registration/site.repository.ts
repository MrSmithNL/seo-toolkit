// Repository pattern — all database access for site_config goes through here
// No raw Drizzle calls in service logic (coding guardrail)

import { eq, and } from 'drizzle-orm';
import { siteConfig } from '../../../../db/schema.js';
import type { DrizzleDB } from '../../../../db/index.js';

export interface SiteRecord {
  readonly id: string;
  readonly tenantId: string;
  readonly url: string;
  readonly name: string;
  readonly cmsType: string | null;
  readonly cmsDetectedAt: string | null;
  readonly primaryLanguage: string | null;
  readonly contentCount: number | null;
  readonly lastCrawled: string | null;
  readonly createdAt: string;
  readonly updatedAt: string;
}

export class SiteRepository {
  constructor(private readonly db: DrizzleDB) {}

  async create(record: {
    id: string;
    tenantId: string;
    url: string;
    name: string;
  }): Promise<SiteRecord> {
    const rows = this.db
      .insert(siteConfig)
      .values({
        id: record.id,
        tenantId: record.tenantId,
        url: record.url,
        name: record.name,
      })
      .returning()
      .all();

    const row = rows[0];
    if (!row) throw new Error('Insert returned no rows');
    return row;
  }

  async findById(id: string, tenantId: string): Promise<SiteRecord | undefined> {
    const rows = this.db
      .select()
      .from(siteConfig)
      .where(and(eq(siteConfig.id, id), eq(siteConfig.tenantId, tenantId)))
      .all();

    return rows[0];
  }

  async findByUrl(url: string, tenantId: string): Promise<SiteRecord | undefined> {
    const rows = this.db
      .select()
      .from(siteConfig)
      .where(and(eq(siteConfig.url, url), eq(siteConfig.tenantId, tenantId)))
      .all();

    return rows[0];
  }
}
