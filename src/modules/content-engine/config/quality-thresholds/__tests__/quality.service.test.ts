// TASK-015: Quality thresholds service — TDD tests
// F-005 US-001 through US-003: Defaults, validation, update, publish mode

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';

import * as schema from '../../../../../db/schema.js';
import { createOperationContext } from '../../../../../lib/context.js';
import { QualityRepository } from '../quality.repository.js';
import { QualityService, getDefaults } from '../quality.service.js';

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

    CREATE TABLE quality_thresholds (
      id TEXT PRIMARY KEY,
      site_id TEXT NOT NULL UNIQUE REFERENCES site_config(id) ON DELETE CASCADE,
      seo_score_min INTEGER DEFAULT 65,
      aiso_score_min REAL DEFAULT 7.0,
      readability_target TEXT DEFAULT 'grade_8',
      word_count_min INTEGER DEFAULT 1500,
      word_count_max INTEGER DEFAULT 3000,
      publish_mode TEXT DEFAULT 'draft_review',
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `);

  sqlite.exec(`
    INSERT INTO site_config (id, tenant_id, url, name, cms_type) VALUES ('ste_wp1', 'tnt_a', 'https://example.com', 'WP Site', 'wordpress');
    INSERT INTO site_config (id, tenant_id, url, name, cms_type) VALUES ('ste_shop1', 'tnt_a', 'https://shop.com', 'Shop Site', 'shopify');
  `);

  return { db, sqlite };
}

describe('QualityService — Quality Thresholds (TASK-015)', () => {
  let db: ReturnType<typeof drizzle>;
  let sqlite: Database.Database;
  let repository: QualityRepository;
  let service: QualityService;

  const ctx = createOperationContext('tnt_a');

  beforeEach(() => {
    const testDb = createTestDb();
    db = testDb.db;
    sqlite = testDb.sqlite;
    repository = new QualityRepository(db);
    service = new QualityService(repository);
  });

  afterEach(() => {
    sqlite.close();
  });

  it('creates defaults for WordPress site (US-001)', async () => {
    const result = await service.createDefaults('ste_wp1', 'wordpress', ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;

    expect(result.data.id).toMatch(/^qty_/);
    expect(result.data.seoScoreMin).toBe(65);
    expect(result.data.aisoScoreMin).toBe(7.0);
    expect(result.data.readabilityTarget).toBe('grade_8');
    expect(result.data.wordCountMin).toBe(1500);
    expect(result.data.wordCountMax).toBe(3000);
    expect(result.data.publishMode).toBe('draft_review');
  });

  it('creates Shopify-specific defaults (shorter content, simpler readability)', async () => {
    const result = await service.createDefaults('ste_shop1', 'shopify', ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;

    expect(result.data.wordCountMin).toBe(800);
    expect(result.data.wordCountMax).toBe(2000);
    expect(result.data.readabilityTarget).toBe('grade_6');
  });

  it('returns existing thresholds on duplicate create (idempotent)', async () => {
    await service.createDefaults('ste_wp1', 'wordpress', ctx);
    const result = await service.createDefaults('ste_wp1', 'wordpress', ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;
    expect(result.data.seoScoreMin).toBe(65);
  });

  it('updates individual threshold values (US-001 partial update)', async () => {
    await service.createDefaults('ste_wp1', 'wordpress', ctx);

    const result = await service.updateThresholds('ste_wp1', { seoScoreMin: 80 }, ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;

    expect(result.data.seoScoreMin).toBe(80);
    expect(result.data.aisoScoreMin).toBe(7.0); // unchanged
    expect(result.data.publishMode).toBe('draft_review'); // unchanged
  });

  it('returns 404 for missing thresholds', async () => {
    const result = await service.getThresholds('ste_wp1', ctx);

    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.error.status).toBe(404);
  });

  it('retrieves existing thresholds', async () => {
    await service.createDefaults('ste_wp1', 'wordpress', ctx);
    const result = await service.getThresholds('ste_wp1', ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;
    expect(result.data.siteId).toBe('ste_wp1');
  });

  it('rejects invalid SEO score range', async () => {
    await service.createDefaults('ste_wp1', 'wordpress', ctx);
    const result = await service.updateThresholds('ste_wp1', { seoScoreMin: 150 }, ctx);

    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.error.status).toBe(400);
    expect(result.error.detail).toContain('seoScoreMin');
  });

  it('rejects invalid publish mode', async () => {
    await service.createDefaults('ste_wp1', 'wordpress', ctx);
    const result = await service.updateThresholds('ste_wp1', { publishMode: 'yolo' }, ctx);

    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.error.status).toBe(400);
    expect(result.error.detail).toContain('publishMode');
  });

  it('rejects wordCountMin > wordCountMax', async () => {
    await service.createDefaults('ste_wp1', 'wordpress', ctx);
    const result = await service.updateThresholds('ste_wp1', { wordCountMin: 5000, wordCountMax: 1000 }, ctx);

    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.error.status).toBe(400);
  });

  it('resets to defaults', async () => {
    await service.createDefaults('ste_wp1', 'wordpress', ctx);
    await service.updateThresholds('ste_wp1', { seoScoreMin: 90, publishMode: 'auto_publish' }, ctx);

    const result = await service.resetToDefaults('ste_wp1', 'wordpress', ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;
    expect(result.data.seoScoreMin).toBe(65);
    expect(result.data.publishMode).toBe('draft_review');
  });

  it('changes publish mode (US-003)', async () => {
    await service.createDefaults('ste_wp1', 'wordpress', ctx);
    const result = await service.updateThresholds('ste_wp1', { publishMode: 'auto_publish' }, ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;
    expect(result.data.publishMode).toBe('auto_publish');
  });
});

describe('getDefaults', () => {
  it('returns standard defaults', () => {
    const d = getDefaults();
    expect(d.seoScoreMin).toBe(65);
    expect(d.wordCountMin).toBe(1500);
  });

  it('returns shopify-adjusted defaults', () => {
    const d = getDefaults('shopify');
    expect(d.wordCountMin).toBe(800);
    expect(d.readabilityTarget).toBe('grade_6');
  });
});
