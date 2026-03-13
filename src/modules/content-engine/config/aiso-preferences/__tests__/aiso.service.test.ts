// TASK-016: AISO preferences service — TDD tests
// F-006 US-001 through US-003: Recommended defaults, custom factors, schema types

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';

import * as schema from '../../../../../db/schema.js';
import { createOperationContext } from '../../../../../lib/context.js';
import { AisoRepository } from '../aiso.repository.js';
import { AisoService } from '../aiso.service.js';
import { FactorRegistry } from '../factor-registry.js';

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

    CREATE TABLE aiso_preferences (
      id TEXT PRIMARY KEY,
      site_id TEXT NOT NULL UNIQUE REFERENCES site_config(id) ON DELETE CASCADE,
      use_recommended INTEGER DEFAULT 1,
      priority_factors TEXT,
      schema_types TEXT,
      ai_platform_targets TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `);

  sqlite.exec(`
    INSERT INTO site_config (id, tenant_id, url, name) VALUES ('ste_aiso1', 'tnt_a', 'https://example.com', 'Test Site');
  `);

  return { db, sqlite };
}

describe('AisoService — AISO Preferences (TASK-016)', () => {
  let db: ReturnType<typeof drizzle>;
  let sqlite: Database.Database;
  let repository: AisoRepository;
  let service: AisoService;

  const ctx = createOperationContext('tnt_a');
  const siteId = 'ste_aiso1';

  beforeEach(() => {
    const testDb = createTestDb();
    db = testDb.db;
    sqlite = testDb.sqlite;
    repository = new AisoRepository(db);
    service = new AisoService(repository);
  });

  afterEach(() => {
    sqlite.close();
  });

  it('creates defaults with use_recommended=true (US-001)', async () => {
    const result = await service.createDefaults(siteId, ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;

    expect(result.data.id).toMatch(/^asp_/);
    expect(result.data.useRecommended).toBe(true);
    const schemaTypes = JSON.parse(result.data.schemaTypes!);
    expect(schemaTypes).toEqual(['Article', 'FAQPage', 'BreadcrumbList']);
    const platforms = JSON.parse(result.data.aiPlatformTargets!);
    expect(platforms).toEqual(['chatgpt', 'perplexity', 'gemini']);
  });

  it('returns existing on duplicate create (idempotent)', async () => {
    await service.createDefaults(siteId, ctx);
    const result = await service.createDefaults(siteId, ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;
    expect(result.data.useRecommended).toBe(true);
  });

  it('returns 404 for missing preferences', async () => {
    const result = await service.getPreferences(siteId, ctx);

    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.error.status).toBe(404);
  });

  it('retrieves existing preferences', async () => {
    await service.createDefaults(siteId, ctx);
    const result = await service.getPreferences(siteId, ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;
    expect(result.data.siteId).toBe(siteId);
  });

  it('updates to custom factors (US-002)', async () => {
    await service.createDefaults(siteId, ctx);

    const result = await service.updatePreferences(siteId, {
      useRecommended: false,
      priorityFactors: ['schema_faq', 'citation_authority', 'concise_answers'],
    }, ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;

    expect(result.data.useRecommended).toBe(false);
    const factors = JSON.parse(result.data.priorityFactors!);
    expect(factors).toHaveLength(3);
    expect(factors).toContain('schema_faq');
  });

  it('rejects unknown factor IDs', async () => {
    await service.createDefaults(siteId, ctx);

    const result = await service.updatePreferences(siteId, {
      priorityFactors: ['schema_faq', 'nonexistent_factor'],
    }, ctx);

    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.error.status).toBe(400);
    expect(result.error.detail).toContain('nonexistent_factor');
  });

  it('updates schema types (US-003)', async () => {
    await service.createDefaults(siteId, ctx);

    const result = await service.updatePreferences(siteId, {
      schemaTypes: ['Article', 'Product', 'FAQPage', 'BreadcrumbList'],
    }, ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;

    const types = JSON.parse(result.data.schemaTypes!);
    expect(types).toHaveLength(4);
    expect(types).toContain('Product');
  });

  it('rejects invalid schema types', async () => {
    await service.createDefaults(siteId, ctx);

    const result = await service.updatePreferences(siteId, {
      schemaTypes: ['Article', 'InvalidSchema'],
    }, ctx);

    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.error.status).toBe(400);
    expect(result.error.detail).toContain('InvalidSchema');
  });

  it('rejects invalid platform targets', async () => {
    await service.createDefaults(siteId, ctx);

    const result = await service.updatePreferences(siteId, {
      aiPlatformTargets: ['chatgpt', 'bard'],
    }, ctx);

    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.error.status).toBe(400);
    expect(result.error.detail).toContain('bard');
  });

  it('resets to recommended defaults', async () => {
    await service.createDefaults(siteId, ctx);
    await service.updatePreferences(siteId, {
      useRecommended: false,
      priorityFactors: ['schema_faq'],
      schemaTypes: ['Product'],
    }, ctx);

    const result = await service.resetToRecommended(siteId, ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;
    expect(result.data.useRecommended).toBe(true);
    expect(result.data.priorityFactors).toBeNull();
    const types = JSON.parse(result.data.schemaTypes!);
    expect(types).toEqual(['Article', 'FAQPage', 'BreadcrumbList']);
  });
});

describe('FactorRegistry', () => {
  const registry = new FactorRegistry();

  it('contains 36 factors', () => {
    expect(registry.count).toBe(36);
  });

  it('groups factors into 6 categories', () => {
    const categories = registry.getCategories();
    expect(categories).toHaveLength(6);
  });

  it('validates known factor IDs', () => {
    const result = registry.validate(['schema_faq', 'citation_authority']);
    expect(result.valid).toBe(true);
    expect(result.unknown).toHaveLength(0);
  });

  it('detects unknown factor IDs', () => {
    const result = registry.validate(['schema_faq', 'fake_factor']);
    expect(result.valid).toBe(false);
    expect(result.unknown).toEqual(['fake_factor']);
  });

  it('has correct distribution across categories', () => {
    expect(registry.getByCategory('structured_data')).toHaveLength(8);
    expect(registry.getByCategory('content_structure')).toHaveLength(7);
    expect(registry.getByCategory('authority_signals')).toHaveLength(6);
    expect(registry.getByCategory('technical_seo')).toHaveLength(5);
    expect(registry.getByCategory('ai_discoverability')).toHaveLength(6);
    expect(registry.getByCategory('user_experience')).toHaveLength(4);
  });
});
