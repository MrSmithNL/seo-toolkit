// TASK-014: Topic configuration service — TDD tests
// F-004 US-001 through US-004: Three input modes + clustering + priorities

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';

import * as schema from '../../../../../db/schema.js';
import { createOperationContext } from '../../../../../lib/context.js';
import { TopicRepository } from '../topic.repository.js';
import { TopicService, type LlmClusterer, type ClusterResult } from '../topic.service.js';

function createTestDb() {
  const sqlite = new Database(':memory:');
  sqlite.pragma('journal_mode = WAL');
  sqlite.pragma('foreign_keys = ON');
  const db = drizzle(sqlite, { schema });

  sqlite.exec(`
    CREATE TABLE site_config (
      id TEXT PRIMARY KEY,
      tenant_id TEXT NOT NULL,
      url TEXT NOT NULL,
      name TEXT NOT NULL,
      cms_type TEXT DEFAULT 'unknown',
      cms_detected_at TEXT,
      primary_language TEXT DEFAULT 'en',
      content_count INTEGER DEFAULT 0,
      last_crawled TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    CREATE UNIQUE INDEX site_config_tenant_url_idx ON site_config(tenant_id, url);

    CREATE TABLE topic_config (
      id TEXT PRIMARY KEY,
      site_id TEXT NOT NULL UNIQUE REFERENCES site_config(id) ON DELETE CASCADE,
      source TEXT DEFAULT 'manual',
      seed_keywords TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE topic_cluster (
      id TEXT PRIMARY KEY,
      topic_config_id TEXT NOT NULL REFERENCES topic_config(id) ON DELETE CASCADE,
      name TEXT NOT NULL,
      keywords TEXT NOT NULL,
      priority TEXT DEFAULT 'medium',
      content_count INTEGER DEFAULT 0
    );
  `);

  // Seed a site for topic config
  sqlite.exec(`
    INSERT INTO site_config (id, tenant_id, url, name) VALUES ('ste_testsite1', 'tnt_a', 'https://example.com', 'Test Site');
  `);

  return { db, sqlite };
}

function mockLlm(clusterResponse?: ClusterResult[], inferResponse?: string[]): LlmClusterer {
  return {
    async clusterKeywords(keywords: string[]): Promise<ClusterResult[]> {
      if (clusterResponse) return clusterResponse;
      // Default: split into two clusters
      const mid = Math.ceil(keywords.length / 2);
      return [
        { name: 'Group A', keywords: keywords.slice(0, mid) },
        { name: 'Group B', keywords: keywords.slice(mid) },
      ];
    },
    async inferTopics(pageData: string[]): Promise<string[]> {
      if (inferResponse) return inferResponse;
      return ['seo', 'content marketing', 'link building'];
    },
  };
}

describe('TopicService — Topic Configuration (TASK-014)', () => {
  let db: ReturnType<typeof drizzle>;
  let sqlite: Database.Database;
  let repository: TopicRepository;

  const ctx = createOperationContext('tnt_a');
  const siteId = 'ste_testsite1';

  beforeEach(() => {
    const testDb = createTestDb();
    db = testDb.db;
    sqlite = testDb.sqlite;
    repository = new TopicRepository(db);
  });

  afterEach(() => {
    sqlite.close();
  });

  it('sets manual keywords and clusters them (US-002)', async () => {
    const llm = mockLlm([
      { name: 'Hair Growth', keywords: ['hair growth', 'biotin', 'hair regrowth', 'minoxidil'] },
      { name: 'Hair Loss', keywords: ['hair loss', 'thinning hair', 'dht blocker'] },
      { name: 'Supplements', keywords: ['hair vitamins', 'hair supplements', 'keratin'] },
    ]);
    const service = new TopicService(repository, llm);

    const result = await service.setTopics(
      siteId,
      ['hair growth, biotin, hair loss, keratin, hair vitamins, thinning hair, hair regrowth, dht blocker, minoxidil, hair supplements'],
      ctx,
    );

    expect(result.success).toBe(true);
    if (!result.success) return;

    expect(result.data.config.source).toBe('manual');
    expect(result.data.config.siteId).toBe(siteId);
    expect(result.data.config.id).toMatch(/^tpc_/);
    expect(result.data.clusters).toHaveLength(3);
    expect(result.data.clusters[0]!.id).toMatch(/^tcl_/);
    expect(result.data.clusters[0]!.priority).toBe('high');   // first cluster = high
    expect(result.data.clusters[1]!.priority).toBe('medium'); // rest = medium
  });

  it('creates single cluster for ≤5 keywords (small set)', async () => {
    const llm = mockLlm();
    const service = new TopicService(repository, llm);

    const result = await service.setTopics(
      siteId,
      ['seo', 'content', 'backlinks'],
      ctx,
    );

    expect(result.success).toBe(true);
    if (!result.success) return;

    expect(result.data.clusters).toHaveLength(1);
    expect(result.data.clusters[0]!.name).toBe('Primary Topics');
    const keywords = JSON.parse(result.data.clusters[0]!.keywords);
    expect(keywords).toContain('seo');
  });

  it('infers topics from page data (US-001)', async () => {
    const llm = mockLlm(undefined, ['hair growth', 'supplements', 'natural ingredients']);
    const service = new TopicService(repository, llm);

    const result = await service.inferTopics(
      siteId,
      ['<title>Hair Growth Tips</title>', '<h1>Best Hair Supplements</h1>'],
      ctx,
    );

    expect(result.success).toBe(true);
    if (!result.success) return;

    expect(result.data.config.source).toBe('auto_inferred');
    expect(result.data.clusters).toHaveLength(1); // 3 keywords ≤5, single cluster
    expect(result.data.clusters[0]!.name).toBe('Primary Topics');
  });

  it('returns 404 for missing topic config', async () => {
    const llm = mockLlm();
    const service = new TopicService(repository, llm);

    const result = await service.getTopics(siteId, ctx);

    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.error.status).toBe(404);
  });

  it('retrieves existing topic config with clusters', async () => {
    const llm = mockLlm();
    const service = new TopicService(repository, llm);

    await service.setTopics(siteId, ['seo', 'marketing'], ctx);
    const result = await service.getTopics(siteId, ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;

    expect(result.data.config.siteId).toBe(siteId);
    expect(result.data.clusters.length).toBeGreaterThan(0);
  });

  it('updates cluster priority (US-004)', async () => {
    const llm = mockLlm();
    const service = new TopicService(repository, llm);

    const created = await service.setTopics(siteId, ['seo', 'marketing'], ctx);
    if (!created.success) throw new Error('Setup failed');

    const clusterId = created.data.clusters[0]!.id;
    const result = await service.updateClusterPriority(clusterId, 'low', ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;
    expect(result.data.priority).toBe('low');
  });

  it('rejects empty keyword list', async () => {
    const llm = mockLlm();
    const service = new TopicService(repository, llm);

    const result = await service.setTopics(siteId, [], ctx);

    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.error.status).toBe(400);
  });

  it('deduplicates and normalises keywords', async () => {
    const llm = mockLlm();
    const service = new TopicService(repository, llm);

    const result = await service.setTopics(
      siteId,
      ['SEO', 'seo', '  Content Marketing  ', 'content marketing'],
      ctx,
    );

    expect(result.success).toBe(true);
    if (!result.success) return;

    const seedKeywords = JSON.parse(result.data.config.seedKeywords!);
    expect(seedKeywords).toHaveLength(2); // deduplicated
    expect(seedKeywords).toContain('seo');
    expect(seedKeywords).toContain('content marketing');
  });

  it('replaces existing config on re-run (idempotent)', async () => {
    const llm = mockLlm();
    const service = new TopicService(repository, llm);

    await service.setTopics(siteId, ['first topic'], ctx);
    const result = await service.setTopics(siteId, ['second topic'], ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;

    const seedKeywords = JSON.parse(result.data.config.seedKeywords!);
    expect(seedKeywords).toEqual(['second topic']);

    // Only one config should exist
    const get = await service.getTopics(siteId, ctx);
    expect(get.success).toBe(true);
  });
});
