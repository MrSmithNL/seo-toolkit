// TASK-012: CMS connection service — connect, verify, manage
// TDD: Tests first with mocked adapters and in-memory DB.

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';

import * as schema from '../../../../../db/schema.js';
import { createOperationContext } from '../../../../../lib/context.js';
import { CmsService } from '../cms.service.js';
import { CmsRepository } from '../cms.repository.js';

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
  `);

  sqlite.exec(`
    INSERT INTO site_config (id, tenant_id, url, name)
    VALUES ('ste_test1', 'tnt_a', 'https://example.com', 'Test Site');
  `);

  return { db, sqlite };
}

const tenantA = 'tnt_a';
const ENCRYPTION_KEY = 'test-encryption-key-for-unit-tests';

describe('CmsService', () => {
  let db: ReturnType<typeof drizzle>;
  let sqlite: Database.Database;
  let service: CmsService;

  beforeEach(() => {
    const testDb = createTestDb();
    db = testDb.db;
    sqlite = testDb.sqlite;
    const repository = new CmsRepository(db);
    service = new CmsService(repository, ENCRYPTION_KEY);
  });

  afterEach(() => {
    sqlite.close();
  });

  describe('connectWordPress', () => {
    it('creates a CMS connection with encrypted credentials', async () => {
      const ctx = createOperationContext(tenantA);
      const result = await service.connect(
        {
          siteId: 'ste_test1',
          cmsType: 'wordpress',
          wpSiteUrl: 'https://example.com',
          wpUsername: 'admin',
          wpApplicationPassword: 'xxxx xxxx xxxx xxxx',
        },
        ctx,
      );

      expect(result.success).toBe(true);
      if (!result.success) return;

      expect(result.data.id).toMatch(/^cms_/);
      expect(result.data.cmsType).toBe('wordpress');
      expect(result.data.status).toBe('pending');
      expect(result.data.wpApplicationPassword).not.toBe('xxxx xxxx xxxx xxxx');
      expect(result.data.wpApplicationPassword).toBeTruthy();
    });

    it('rejects duplicate connection for same site', async () => {
      const ctx = createOperationContext(tenantA);
      await service.connect(
        { siteId: 'ste_test1', cmsType: 'wordpress', wpSiteUrl: 'https://example.com', wpUsername: 'admin', wpApplicationPassword: 'pass' },
        ctx,
      );

      const result = await service.connect(
        { siteId: 'ste_test1', cmsType: 'wordpress', wpSiteUrl: 'https://example.com', wpUsername: 'admin', wpApplicationPassword: 'pass2' },
        ctx,
      );

      expect(result.success).toBe(false);
      if (result.success) return;
      expect(result.error.status).toBe(409);
    });
  });

  describe('connectShopify', () => {
    it('creates a Shopify CMS connection with encrypted token', async () => {
      const ctx = createOperationContext(tenantA);
      const result = await service.connect(
        {
          siteId: 'ste_test1',
          cmsType: 'shopify',
          shopifyStoreDomain: 'test.myshopify.com',
          shopifyAccessToken: 'shpat_secret_token',
        },
        ctx,
      );

      expect(result.success).toBe(true);
      if (!result.success) return;

      expect(result.data.cmsType).toBe('shopify');
      expect(result.data.shopifyAccessToken).not.toBe('shpat_secret_token');
    });
  });

  describe('getConnection', () => {
    it('returns connection for a site', async () => {
      const ctx = createOperationContext(tenantA);
      await service.connect(
        { siteId: 'ste_test1', cmsType: 'wordpress', wpSiteUrl: 'https://example.com', wpUsername: 'admin', wpApplicationPassword: 'pass' },
        ctx,
      );

      const result = await service.getConnection('ste_test1', ctx);

      expect(result.success).toBe(true);
      if (!result.success) return;
      expect(result.data.siteId).toBe('ste_test1');
    });

    it('returns 404 for site without connection', async () => {
      const ctx = createOperationContext(tenantA);
      const result = await service.getConnection('ste_noconn', ctx);

      expect(result.success).toBe(false);
      if (result.success) return;
      expect(result.error.status).toBe(404);
    });
  });

  describe('updateStatus', () => {
    it('updates connection status to verified', async () => {
      const ctx = createOperationContext(tenantA);
      const conn = await service.connect(
        { siteId: 'ste_test1', cmsType: 'wordpress', wpSiteUrl: 'https://example.com', wpUsername: 'admin', wpApplicationPassword: 'pass' },
        ctx,
      );
      if (!conn.success) throw new Error('Setup failed');

      const result = await service.updateStatus(conn.data.id, 'verified', ctx);

      expect(result.success).toBe(true);
      if (!result.success) return;
      expect(result.data.status).toBe('verified');
      expect(result.data.verifiedAt).toBeTruthy();
    });
  });
});
