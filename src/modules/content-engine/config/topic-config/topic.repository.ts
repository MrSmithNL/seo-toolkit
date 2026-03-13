// Topic configuration repository (TASK-014)

import { eq } from 'drizzle-orm';
import { topicConfig, topicCluster } from '../../../../db/schema.js';
import type { DrizzleDB } from '../../../../db/index.js';

export interface TopicConfigRecord {
  readonly id: string;
  readonly siteId: string;
  readonly source: string | null;
  readonly seedKeywords: string | null;
  readonly createdAt: string;
  readonly updatedAt: string;
}

export interface TopicClusterRecord {
  readonly id: string;
  readonly topicConfigId: string;
  readonly name: string;
  readonly keywords: string;
  readonly priority: string | null;
  readonly contentCount: number | null;
}

export class TopicRepository {
  constructor(private readonly db: DrizzleDB) {}

  async createConfig(record: {
    id: string;
    siteId: string;
    source: string;
    seedKeywords?: string;
  }): Promise<TopicConfigRecord> {
    const rows = this.db.insert(topicConfig).values(record).returning().all();
    const row = rows[0];
    if (!row) throw new Error('Insert returned no rows');
    return row;
  }

  async findConfigBySiteId(siteId: string): Promise<TopicConfigRecord | undefined> {
    return this.db.select().from(topicConfig).where(eq(topicConfig.siteId, siteId)).all()[0];
  }

  async addCluster(record: {
    id: string;
    topicConfigId: string;
    name: string;
    keywords: string;
    priority?: string;
    contentCount?: number;
  }): Promise<TopicClusterRecord> {
    const rows = this.db.insert(topicCluster).values(record).returning().all();
    const row = rows[0];
    if (!row) throw new Error('Insert returned no rows');
    return row;
  }

  async findClustersByConfigId(configId: string): Promise<TopicClusterRecord[]> {
    return this.db.select().from(topicCluster)
      .where(eq(topicCluster.topicConfigId, configId)).all();
  }

  async updateClusterPriority(clusterId: string, priority: string): Promise<TopicClusterRecord> {
    const rows = this.db.update(topicCluster)
      .set({ priority })
      .where(eq(topicCluster.id, clusterId))
      .returning().all();
    const row = rows[0];
    if (!row) throw new Error('Update returned no rows');
    return row;
  }

  async deleteConfigBySiteId(siteId: string): Promise<void> {
    this.db.delete(topicConfig).where(eq(topicConfig.siteId, siteId)).run();
  }
}
