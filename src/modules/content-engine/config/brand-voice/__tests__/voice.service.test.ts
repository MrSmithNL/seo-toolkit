// TASK-013: Brand voice extraction service
// TDD: Tests first.

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';

import * as schema from '../../../../../db/schema.js';
import { createOperationContext } from '../../../../../lib/context.js';
import { VoiceService, type LlmClient } from '../voice.service.js';
import { VoiceRepository } from '../voice.repository.js';

function createTestDb() {
  const sqlite = new Database(':memory:');
  sqlite.pragma('journal_mode = WAL');
  sqlite.pragma('foreign_keys = ON');
  const db = drizzle(sqlite, { schema });

  sqlite.exec(`
    CREATE TABLE site_config (
      id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, url TEXT NOT NULL,
      name TEXT NOT NULL, cms_type TEXT DEFAULT 'unknown', cms_detected_at TEXT,
      primary_language TEXT DEFAULT 'en', content_count INTEGER DEFAULT 0,
      last_crawled TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    CREATE UNIQUE INDEX site_config_tenant_url_idx ON site_config(tenant_id, url);
    CREATE TABLE voice_profile (
      id TEXT PRIMARY KEY, site_id TEXT NOT NULL UNIQUE REFERENCES site_config(id) ON DELETE CASCADE,
      brand_name TEXT, industry TEXT, target_audience TEXT, brand_values TEXT,
      key_topics TEXT, tone TEXT DEFAULT 'conversational',
      sentence_structure TEXT DEFAULT 'mixed', vocabulary_level TEXT DEFAULT 'intermediate',
      person TEXT DEFAULT 'second', extracted_from_url TEXT, extracted_at TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    INSERT INTO site_config (id, tenant_id, url, name) VALUES ('ste_test1', 'tnt_a', 'https://example.com', 'Test');
  `);

  return { db, sqlite };
}

const mockLlm: LlmClient = {
  async extractVoice(_content: string) {
    return {
      brandName: 'Example Corp',
      industry: 'Technology',
      targetAudience: 'Small businesses',
      brandValues: 'Innovation, Quality',
      keyTopics: 'SaaS, AI, Automation',
      tone: 'professional',
      sentenceStructure: 'complex',
      vocabularyLevel: 'advanced',
      person: 'third',
    };
  },
};

describe('VoiceService', () => {
  let db: ReturnType<typeof drizzle>;
  let sqlite: Database.Database;
  let service: VoiceService;

  beforeEach(() => {
    const testDb = createTestDb();
    db = testDb.db;
    sqlite = testDb.sqlite;
    const repo = new VoiceRepository(db);
    service = new VoiceService(repo, mockLlm);
  });

  afterEach(() => { sqlite.close(); });

  it('extracts and stores a voice profile from LLM', async () => {
    const ctx = createOperationContext('tnt_a');
    const result = await service.extractVoice('ste_test1', 'https://example.com/about', ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;
    expect(result.data.brandName).toBe('Example Corp');
    expect(result.data.tone).toBe('professional');
    expect(result.data.extractedFromUrl).toBe('https://example.com/about');
    expect(result.data.extractedAt).toBeTruthy();
  });

  it('creates defaults when skipping extraction', async () => {
    const ctx = createOperationContext('tnt_a');
    const result = await service.createDefaults('ste_test1', ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;
    expect(result.data.tone).toBe('conversational');
    expect(result.data.vocabularyLevel).toBe('intermediate');
    expect(result.data.person).toBe('second');
  });

  it('retrieves an existing voice profile', async () => {
    const ctx = createOperationContext('tnt_a');
    await service.createDefaults('ste_test1', ctx);

    const result = await service.getProfile('ste_test1', ctx);
    expect(result.success).toBe(true);
    if (!result.success) return;
    expect(result.data.siteId).toBe('ste_test1');
  });

  it('returns 404 for missing profile', async () => {
    const ctx = createOperationContext('tnt_a');
    const result = await service.getProfile('ste_noexist', ctx);
    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.error.status).toBe(404);
  });

  it('updates individual voice parameters', async () => {
    const ctx = createOperationContext('tnt_a');
    await service.createDefaults('ste_test1', ctx);

    const result = await service.updateProfile('ste_test1', { tone: 'casual', person: 'first' }, ctx);
    expect(result.success).toBe(true);
    if (!result.success) return;
    expect(result.data.tone).toBe('casual');
    expect(result.data.person).toBe('first');
  });
});
