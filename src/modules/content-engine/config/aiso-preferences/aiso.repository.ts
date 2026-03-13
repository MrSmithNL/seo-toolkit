// AISO preferences repository (TASK-016)

import { eq, sql } from 'drizzle-orm';
import { aisoPreferences } from '../../../../db/schema.js';
import type { DrizzleDB } from '../../../../db/index.js';

export interface AisoPreferencesRecord {
  readonly id: string;
  readonly siteId: string;
  readonly useRecommended: boolean | null;
  readonly priorityFactors: string | null;
  readonly schemaTypes: string | null;
  readonly aiPlatformTargets: string | null;
  readonly createdAt: string;
  readonly updatedAt: string;
}

export class AisoRepository {
  constructor(private readonly db: DrizzleDB) {}

  async create(record: {
    id: string;
    siteId: string;
    useRecommended?: boolean;
    priorityFactors?: string;
    schemaTypes?: string;
    aiPlatformTargets?: string;
  }): Promise<AisoPreferencesRecord> {
    const rows = this.db.insert(aisoPreferences).values(record).returning().all();
    const row = rows[0];
    if (!row) throw new Error('Insert returned no rows');
    return row;
  }

  async findBySiteId(siteId: string): Promise<AisoPreferencesRecord | undefined> {
    return this.db.select().from(aisoPreferences)
      .where(eq(aisoPreferences.siteId, siteId)).all()[0];
  }

  async update(siteId: string, fields: Partial<Omit<AisoPreferencesRecord, 'id' | 'siteId' | 'createdAt' | 'updatedAt'>>): Promise<AisoPreferencesRecord> {
    const rows = this.db.update(aisoPreferences)
      .set({ ...fields, updatedAt: sql`(datetime('now'))` })
      .where(eq(aisoPreferences.siteId, siteId))
      .returning().all();
    const row = rows[0];
    if (!row) throw new Error('Update returned no rows');
    return row;
  }
}
