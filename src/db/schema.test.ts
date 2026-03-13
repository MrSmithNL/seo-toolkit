// TDD Red Phase — TASK-002: Full schema verification
// Tests all 8 tables, relations, cascading deletes, and constraints

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';
import { eq } from 'drizzle-orm';
import * as schema from './schema.js';

// SQL to create all tables — mirrors the Drizzle schema exactly
const CREATE_TABLES_SQL = `
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
  CREATE INDEX site_config_tenant_idx ON site_config(tenant_id);

  CREATE TABLE site_language (
    id TEXT PRIMARY KEY,
    site_id TEXT NOT NULL REFERENCES site_config(id) ON DELETE CASCADE,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    url_pattern TEXT
  );
  CREATE UNIQUE INDEX site_language_site_code_idx ON site_language(site_id, code);

  CREATE TABLE cms_connection (
    id TEXT PRIMARY KEY,
    site_id TEXT NOT NULL UNIQUE REFERENCES site_config(id) ON DELETE CASCADE,
    cms_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    wp_site_url TEXT,
    wp_username TEXT,
    wp_application_password TEXT,
    shopify_store_domain TEXT,
    shopify_access_token TEXT,
    default_publish_status TEXT DEFAULT 'draft',
    verified_at TEXT,
    last_used_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
  );

  CREATE TABLE voice_profile (
    id TEXT PRIMARY KEY,
    site_id TEXT NOT NULL UNIQUE REFERENCES site_config(id) ON DELETE CASCADE,
    brand_name TEXT,
    industry TEXT,
    target_audience TEXT,
    brand_values TEXT,
    key_topics TEXT,
    tone TEXT DEFAULT 'conversational',
    sentence_structure TEXT DEFAULT 'mixed',
    vocabulary_level TEXT DEFAULT 'intermediate',
    person TEXT DEFAULT 'second',
    extracted_from_url TEXT,
    extracted_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
  );

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
`;

function createTestDb() {
  const sqlite = new Database(':memory:');
  sqlite.pragma('foreign_keys = ON');
  sqlite.exec(CREATE_TABLES_SQL);
  const db = drizzle(sqlite, { schema });
  return { db, sqlite };
}

describe('Schema — Full Data Model (TASK-002)', () => {
  let db: ReturnType<typeof drizzle>;
  let sqlite: Database.Database;

  beforeEach(() => {
    const testDb = createTestDb();
    db = testDb.db;
    sqlite = testDb.sqlite;
  });

  afterEach(() => {
    sqlite.close();
  });

  it('should insert and read siteConfig', () => {
    db.insert(schema.siteConfig).values({
      id: 'ste_test001',
      tenantId: 'tnt_t1',
      url: 'https://example.com',
      name: 'Example',
    }).run();

    const rows = db.select().from(schema.siteConfig).all();
    expect(rows).toHaveLength(1);
    expect(rows[0]!.id).toBe('ste_test001');
    expect(rows[0]!.cmsType).toBe('unknown');
    expect(rows[0]!.primaryLanguage).toBe('en');
  });

  it('should insert and read siteLanguage', () => {
    db.insert(schema.siteConfig).values({
      id: 'ste_lang01', tenantId: 'tnt_t1', url: 'https://ex.com', name: 'Ex',
    }).run();
    db.insert(schema.siteLanguage).values({
      id: 'slg_test001', siteId: 'ste_lang01', code: 'en', name: 'English',
    }).run();
    db.insert(schema.siteLanguage).values({
      id: 'slg_test002', siteId: 'ste_lang01', code: 'nl', name: 'Dutch', urlPattern: '/nl/',
    }).run();

    const rows = db.select().from(schema.siteLanguage).where(eq(schema.siteLanguage.siteId, 'ste_lang01')).all();
    expect(rows).toHaveLength(2);
  });

  it('should enforce unique language code per site', () => {
    db.insert(schema.siteConfig).values({
      id: 'ste_uniq01', tenantId: 'tnt_t1', url: 'https://uniq.com', name: 'U',
    }).run();
    db.insert(schema.siteLanguage).values({
      id: 'slg_dup01', siteId: 'ste_uniq01', code: 'en', name: 'English',
    }).run();

    expect(() => {
      db.insert(schema.siteLanguage).values({
        id: 'slg_dup02', siteId: 'ste_uniq01', code: 'en', name: 'English Again',
      }).run();
    }).toThrow();
  });

  it('should insert and read cmsConnection', () => {
    db.insert(schema.siteConfig).values({
      id: 'ste_cms01', tenantId: 'tnt_t1', url: 'https://cms.com', name: 'CMS',
    }).run();
    db.insert(schema.cmsConnection).values({
      id: 'cms_test001', siteId: 'ste_cms01', cmsType: 'wordpress',
      wpSiteUrl: 'https://cms.com/wp-json', wpUsername: 'admin',
    }).run();

    const rows = db.select().from(schema.cmsConnection).all();
    expect(rows).toHaveLength(1);
    expect(rows[0]!.status).toBe('pending');
    expect(rows[0]!.defaultPublishStatus).toBe('draft');
  });

  it('should insert and read voiceProfile', () => {
    db.insert(schema.siteConfig).values({
      id: 'ste_vp01', tenantId: 'tnt_t1', url: 'https://voice.com', name: 'Voice',
    }).run();
    db.insert(schema.voiceProfile).values({
      id: 'vce_test001', siteId: 'ste_vp01', brandName: 'TestBrand',
      tone: 'professional', person: 'third',
    }).run();

    const rows = db.select().from(schema.voiceProfile).all();
    expect(rows).toHaveLength(1);
    expect(rows[0]!.tone).toBe('professional');
    expect(rows[0]!.vocabularyLevel).toBe('intermediate');
  });

  it('should insert and read topicConfig with clusters', () => {
    db.insert(schema.siteConfig).values({
      id: 'ste_tc01', tenantId: 'tnt_t1', url: 'https://topic.com', name: 'Topic',
    }).run();
    db.insert(schema.topicConfig).values({
      id: 'tpc_test001', siteId: 'ste_tc01', source: 'manual',
      seedKeywords: JSON.stringify(['seo', 'content', 'ai']),
    }).run();
    db.insert(schema.topicCluster).values({
      id: 'tcl_test001', topicConfigId: 'tpc_test001', name: 'SEO Basics',
      keywords: JSON.stringify(['seo tips', 'seo guide']), priority: 'high',
    }).run();

    const configs = db.select().from(schema.topicConfig).all();
    const clusters = db.select().from(schema.topicCluster).all();
    expect(configs).toHaveLength(1);
    expect(clusters).toHaveLength(1);
    expect(clusters[0]!.priority).toBe('high');
  });

  it('should insert and read qualityThresholds with defaults', () => {
    db.insert(schema.siteConfig).values({
      id: 'ste_qt01', tenantId: 'tnt_t1', url: 'https://quality.com', name: 'Quality',
    }).run();
    db.insert(schema.qualityThresholds).values({
      id: 'qty_test001', siteId: 'ste_qt01',
    }).run();

    const rows = db.select().from(schema.qualityThresholds).all();
    expect(rows).toHaveLength(1);
    expect(rows[0]!.seoScoreMin).toBe(65);
    expect(rows[0]!.aisoScoreMin).toBe(7.0);
    expect(rows[0]!.wordCountMin).toBe(1500);
    expect(rows[0]!.wordCountMax).toBe(3000);
    expect(rows[0]!.publishMode).toBe('draft_review');
  });

  it('should insert and read aisoPreferences', () => {
    db.insert(schema.siteConfig).values({
      id: 'ste_ap01', tenantId: 'tnt_t1', url: 'https://aiso.com', name: 'AISO',
    }).run();
    db.insert(schema.aisoPreferences).values({
      id: 'asp_test001', siteId: 'ste_ap01',
      priorityFactors: JSON.stringify(['citations', 'structured_data']),
      schemaTypes: JSON.stringify(['Article', 'FAQPage']),
    }).run();

    const rows = db.select().from(schema.aisoPreferences).all();
    expect(rows).toHaveLength(1);
    expect(rows[0]!.useRecommended).toBe(true);
  });

  describe('Cascading deletes', () => {
    const siteId = 'ste_cascade01';

    beforeEach(() => {
      db.insert(schema.siteConfig).values({
        id: siteId, tenantId: 'tnt_t1', url: 'https://cascade.com', name: 'Cascade',
      }).run();
      db.insert(schema.siteLanguage).values({
        id: 'slg_c01', siteId, code: 'en', name: 'English',
      }).run();
      db.insert(schema.cmsConnection).values({
        id: 'cms_c01', siteId, cmsType: 'shopify',
      }).run();
      db.insert(schema.voiceProfile).values({
        id: 'vce_c01', siteId, brandName: 'CascadeBrand',
      }).run();
      db.insert(schema.topicConfig).values({
        id: 'tpc_c01', siteId,
      }).run();
      db.insert(schema.topicCluster).values({
        id: 'tcl_c01', topicConfigId: 'tpc_c01', name: 'Cluster', keywords: '["kw1"]',
      }).run();
      db.insert(schema.qualityThresholds).values({
        id: 'qty_c01', siteId,
      }).run();
      db.insert(schema.aisoPreferences).values({
        id: 'asp_c01', siteId,
      }).run();
    });

    it('should cascade delete all child entities when site is deleted', () => {
      expect(db.select().from(schema.siteLanguage).all()).toHaveLength(1);
      expect(db.select().from(schema.cmsConnection).all()).toHaveLength(1);
      expect(db.select().from(schema.voiceProfile).all()).toHaveLength(1);
      expect(db.select().from(schema.topicConfig).all()).toHaveLength(1);
      expect(db.select().from(schema.topicCluster).all()).toHaveLength(1);
      expect(db.select().from(schema.qualityThresholds).all()).toHaveLength(1);
      expect(db.select().from(schema.aisoPreferences).all()).toHaveLength(1);

      db.delete(schema.siteConfig).where(eq(schema.siteConfig.id, siteId)).run();

      expect(db.select().from(schema.siteConfig).all()).toHaveLength(0);
      expect(db.select().from(schema.siteLanguage).all()).toHaveLength(0);
      expect(db.select().from(schema.cmsConnection).all()).toHaveLength(0);
      expect(db.select().from(schema.voiceProfile).all()).toHaveLength(0);
      expect(db.select().from(schema.topicConfig).all()).toHaveLength(0);
      expect(db.select().from(schema.topicCluster).all()).toHaveLength(0);
      expect(db.select().from(schema.qualityThresholds).all()).toHaveLength(0);
      expect(db.select().from(schema.aisoPreferences).all()).toHaveLength(0);
    });

    it('should cascade delete topic clusters when topicConfig is deleted', () => {
      expect(db.select().from(schema.topicCluster).all()).toHaveLength(1);

      db.delete(schema.topicConfig).where(eq(schema.topicConfig.id, 'tpc_c01')).run();

      expect(db.select().from(schema.topicCluster).all()).toHaveLength(0);
      expect(db.select().from(schema.siteConfig).all()).toHaveLength(1);
    });
  });

  it('should enforce unique tenant+URL constraint', () => {
    db.insert(schema.siteConfig).values({
      id: 'ste_dup01', tenantId: 'tnt_t1', url: 'https://dup.com', name: 'First',
    }).run();

    expect(() => {
      db.insert(schema.siteConfig).values({
        id: 'ste_dup02', tenantId: 'tnt_t1', url: 'https://dup.com', name: 'Second',
      }).run();
    }).toThrow();
  });

  it('should allow same URL for different tenants', () => {
    db.insert(schema.siteConfig).values({
      id: 'ste_mt01', tenantId: 'tnt_t1', url: 'https://multi.com', name: 'T1',
    }).run();
    db.insert(schema.siteConfig).values({
      id: 'ste_mt02', tenantId: 'tnt_t2', url: 'https://multi.com', name: 'T2',
    }).run();

    const rows = db.select().from(schema.siteConfig).all();
    expect(rows).toHaveLength(2);
  });
});
