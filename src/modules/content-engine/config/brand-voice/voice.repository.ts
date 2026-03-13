// Voice profile repository (TASK-013)

import { eq, sql } from 'drizzle-orm';
import { voiceProfile } from '../../../../db/schema.js';
import type { DrizzleDB } from '../../../../db/index.js';

export interface VoiceProfileRecord {
  readonly id: string;
  readonly siteId: string;
  readonly brandName: string | null;
  readonly industry: string | null;
  readonly targetAudience: string | null;
  readonly brandValues: string | null;
  readonly keyTopics: string | null;
  readonly tone: string | null;
  readonly sentenceStructure: string | null;
  readonly vocabularyLevel: string | null;
  readonly person: string | null;
  readonly extractedFromUrl: string | null;
  readonly extractedAt: string | null;
  readonly createdAt: string;
  readonly updatedAt: string;
}

export class VoiceRepository {
  constructor(private readonly db: DrizzleDB) {}

  async create(record: Partial<VoiceProfileRecord> & { id: string; siteId: string }): Promise<VoiceProfileRecord> {
    const rows = this.db.insert(voiceProfile).values(record).returning().all();
    const row = rows[0];
    if (!row) throw new Error('Insert returned no rows');
    return row;
  }

  async findBySiteId(siteId: string): Promise<VoiceProfileRecord | undefined> {
    return this.db.select().from(voiceProfile).where(eq(voiceProfile.siteId, siteId)).all()[0];
  }

  async update(siteId: string, fields: Partial<VoiceProfileRecord>): Promise<VoiceProfileRecord> {
    const rows = this.db.update(voiceProfile)
      .set({ ...fields, updatedAt: sql`(datetime('now'))` })
      .where(eq(voiceProfile.siteId, siteId))
      .returning().all();
    const row = rows[0];
    if (!row) throw new Error('Update returned no rows');
    return row;
  }
}
