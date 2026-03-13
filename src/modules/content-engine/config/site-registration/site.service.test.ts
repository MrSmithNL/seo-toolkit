// TDD Red Phase — Walking skeleton tests
// TASK-001: registerSite() creates a row, getSite() retrieves it

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';
import { migrate } from 'drizzle-orm/better-sqlite3/migrator';
import { sql } from 'drizzle-orm';

import * as schema from '../../../../db/schema.js';
import { createOperationContext } from '../../../../lib/context.js';
import { SiteRepository } from './site.repository.js';
import { SiteService } from './site.service.js';

function createTestDb() {
  const sqlite = new Database(':memory:');
  sqlite.pragma('journal_mode = WAL');
  sqlite.pragma('foreign_keys = ON');
  const db = drizzle(sqlite, { schema });

  // Create tables directly for tests (no migration files yet)
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
    CREATE INDEX site_config_tenant_idx ON site_config(tenant_id);
  `);

  return { db, sqlite };
}

describe('SiteService — Walking Skeleton', () => {
  let db: ReturnType<typeof drizzle>;
  let sqlite: Database.Database;
  let repository: SiteRepository;
  let service: SiteService;

  const tenantA = 'tnt_tenant_a';
  const tenantB = 'tnt_tenant_b';

  beforeEach(() => {
    const testDb = createTestDb();
    db = testDb.db;
    sqlite = testDb.sqlite;
    repository = new SiteRepository(db);
    service = new SiteService(repository);
  });

  afterEach(() => {
    sqlite.close();
  });

  describe('registerSite', () => {
    it('should create a site and return it with a prefixed ID', async () => {
      const ctx = createOperationContext(tenantA);
      const result = await service.registerSite(
        { url: 'https://example.com', name: 'Example' },
        ctx,
      );

      expect(result.success).toBe(true);
      if (!result.success) return;

      expect(result.data.id).toMatch(/^ste_/);
      expect(result.data.tenantId).toBe(tenantA);
      expect(result.data.url).toBe('https://example.com');
      expect(result.data.name).toBe('Example');
    });

    it('should reject invalid URL', async () => {
      const ctx = createOperationContext(tenantA);
      const result = await service.registerSite(
        { url: 'not-a-url', name: 'Bad' },
        ctx,
      );

      expect(result.success).toBe(false);
      if (result.success) return;
      expect(result.error.status).toBe(400);
    });

    it('should reject duplicate URL for same tenant', async () => {
      const ctx = createOperationContext(tenantA);
      await service.registerSite({ url: 'https://example.com', name: 'First' }, ctx);
      const result = await service.registerSite({ url: 'https://example.com', name: 'Duplicate' }, ctx);

      expect(result.success).toBe(false);
      if (result.success) return;
      expect(result.error.status).toBe(409);
    });

    it('should allow same URL for different tenants', async () => {
      const ctxA = createOperationContext(tenantA);
      const ctxB = createOperationContext(tenantB);

      const resultA = await service.registerSite({ url: 'https://example.com', name: 'A' }, ctxA);
      const resultB = await service.registerSite({ url: 'https://example.com', name: 'B' }, ctxB);

      expect(resultA.success).toBe(true);
      expect(resultB.success).toBe(true);
    });
  });

  describe('getSite', () => {
    it('should return a registered site by ID within tenant scope', async () => {
      const ctx = createOperationContext(tenantA);
      const registered = await service.registerSite(
        { url: 'https://example.com', name: 'Example' },
        ctx,
      );
      if (!registered.success) throw new Error('Setup failed');

      const result = await service.getSite(registered.data.id, ctx);

      expect(result.success).toBe(true);
      if (!result.success) return;
      expect(result.data.id).toBe(registered.data.id);
      expect(result.data.url).toBe('https://example.com');
    });

    it('should return 404 for non-existent site', async () => {
      const ctx = createOperationContext(tenantA);
      const result = await service.getSite('ste_doesnotexist', ctx);

      expect(result.success).toBe(false);
      if (result.success) return;
      expect(result.error.status).toBe(404);
    });

    it('should return 404 when accessing another tenant\'s site (tenant isolation)', async () => {
      const ctxA = createOperationContext(tenantA);
      const ctxB = createOperationContext(tenantB);

      const registered = await service.registerSite(
        { url: 'https://example.com', name: 'A Site' },
        ctxA,
      );
      if (!registered.success) throw new Error('Setup failed');

      // Tenant B tries to access Tenant A's site — should get 404, not 403
      const result = await service.getSite(registered.data.id, ctxB);

      expect(result.success).toBe(false);
      if (result.success) return;
      expect(result.error.status).toBe(404);
    });
  });
});
