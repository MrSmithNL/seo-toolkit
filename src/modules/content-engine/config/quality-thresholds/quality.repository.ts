// Quality thresholds repository (TASK-015)

import { eq, sql } from 'drizzle-orm';
import { qualityThresholds } from '../../../../db/schema.js';
import type { DrizzleDB } from '../../../../db/index.js';

export interface QualityThresholdsRecord {
  readonly id: string;
  readonly siteId: string;
  readonly seoScoreMin: number | null;
  readonly aisoScoreMin: number | null;
  readonly readabilityTarget: string | null;
  readonly wordCountMin: number | null;
  readonly wordCountMax: number | null;
  readonly publishMode: string | null;
  readonly createdAt: string;
  readonly updatedAt: string;
}

export class QualityRepository {
  constructor(private readonly db: DrizzleDB) {}

  async create(record: {
    id: string;
    siteId: string;
    seoScoreMin?: number;
    aisoScoreMin?: number;
    readabilityTarget?: string;
    wordCountMin?: number;
    wordCountMax?: number;
    publishMode?: string;
  }): Promise<QualityThresholdsRecord> {
    const rows = this.db.insert(qualityThresholds).values(record).returning().all();
    const row = rows[0];
    if (!row) throw new Error('Insert returned no rows');
    return row;
  }

  async findBySiteId(siteId: string): Promise<QualityThresholdsRecord | undefined> {
    return this.db.select().from(qualityThresholds)
      .where(eq(qualityThresholds.siteId, siteId)).all()[0];
  }

  async update(siteId: string, fields: Partial<Omit<QualityThresholdsRecord, 'id' | 'siteId' | 'createdAt' | 'updatedAt'>>): Promise<QualityThresholdsRecord> {
    const rows = this.db.update(qualityThresholds)
      .set({ ...fields, updatedAt: sql`(datetime('now'))` })
      .where(eq(qualityThresholds.siteId, siteId))
      .returning().all();
    const row = rows[0];
    if (!row) throw new Error('Update returned no rows');
    return row;
  }
}
