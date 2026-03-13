// TASK-011: Site registration pipeline — orchestrate URL normalisation + crawl
// TDD: Tests first with mocked HTTP for CMS/language/sitemap detection.

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';

import * as schema from '../../../../../db/schema.js';
import { createOperationContext } from '../../../../../lib/context.js';
import { SiteRepository } from '../site.repository.js';
import { SiteService } from '../site.service.js';
import type { HttpFetcher, HttpResponse } from '../detectors/types.js';

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
    CREATE INDEX site_config_tenant_idx ON site_config(tenant_id);

    CREATE TABLE site_language (
      id TEXT PRIMARY KEY,
      site_id TEXT NOT NULL REFERENCES site_config(id) ON DELETE CASCADE,
      code TEXT NOT NULL,
      name TEXT NOT NULL,
      url_pattern TEXT
    );
    CREATE UNIQUE INDEX site_language_site_code_idx ON site_language(site_id, code);
  `);

  return { db, sqlite };
}

function mockFetcher(responses: Record<string, HttpResponse>): HttpFetcher {
  return {
    async get(url: string): Promise<HttpResponse> {
      const resp = responses[url];
      if (resp) return resp;
      return { status: 404, body: '' };
    },
  };
}

describe('SiteService — Registration Pipeline (TASK-011)', () => {
  let db: ReturnType<typeof drizzle>;
  let sqlite: Database.Database;
  let repository: SiteRepository;

  const tenantA = 'tnt_tenant_a';

  beforeEach(() => {
    const testDb = createTestDb();
    db = testDb.db;
    sqlite = testDb.sqlite;
    repository = new SiteRepository(db);
  });

  afterEach(() => {
    sqlite.close();
  });

  it('registers a WordPress site with full crawl pipeline', async () => {
    const fetcher = mockFetcher({
      'https://example.com/wp-json/wp/v2/': {
        status: 200,
        body: '{"name":"Example WP"}',
      },
      'https://example.com': {
        status: 200,
        body: '<html lang="en"><head><link rel="alternate" hreflang="nl" href="https://example.com/nl/"></head></html>',
      },
      'https://example.com/sitemap.xml': {
        status: 200,
        body: `<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/</loc></url>
  <url><loc>https://example.com/about</loc></url>
  <url><loc>https://example.com/blog/post-1</loc></url>
</urlset>`,
      },
    });

    const service = new SiteService(repository, fetcher);
    const ctx = createOperationContext(tenantA);
    const result = await service.registerAndCrawl(
      { url: 'example.com', name: 'Example' },
      ctx,
    );

    expect(result.success).toBe(true);
    if (!result.success) return;

    expect(result.data.site.cmsType).toBe('wordpress');
    expect(result.data.site.contentCount).toBe(3);
    expect(result.data.site.lastCrawled).toBeTruthy();
    expect(result.data.languages).toHaveLength(2);
    expect(result.data.languages.map(l => l.code)).toContain('en');
    expect(result.data.languages.map(l => l.code)).toContain('nl');
  });

  it('registers a Shopify site correctly', async () => {
    const fetcher = mockFetcher({
      'https://myshop.com/wp-json/wp/v2/': { status: 404, body: '' },
      'https://myshop.com/wp-login.php': { status: 404, body: '' },
      'https://myshop.com': {
        status: 200,
        body: '<html lang="en"><head><link href="https://cdn.shopify.com/s/files/theme.css"></head></html>',
      },
      'https://myshop.com/sitemap.xml': { status: 404, body: '' },
      'https://myshop.com/sitemap_index.xml': { status: 404, body: '' },
    });

    const service = new SiteService(repository, fetcher);
    const ctx = createOperationContext(tenantA);
    const result = await service.registerAndCrawl(
      { url: 'https://myshop.com', name: 'My Shop' },
      ctx,
    );

    expect(result.success).toBe(true);
    if (!result.success) return;

    expect(result.data.site.cmsType).toBe('shopify');
    expect(result.data.site.contentCount).toBe(0);
  });

  it('handles unknown CMS gracefully', async () => {
    const fetcher = mockFetcher({
      'https://custom.com/wp-json/wp/v2/': { status: 404, body: '' },
      'https://custom.com/wp-login.php': { status: 404, body: '' },
      'https://custom.com': {
        status: 200,
        body: '<html lang="en"><title>Custom CMS</title></html>',
      },
      'https://custom.com/sitemap.xml': { status: 404, body: '' },
      'https://custom.com/sitemap_index.xml': { status: 404, body: '' },
    });

    const service = new SiteService(repository, fetcher);
    const ctx = createOperationContext(tenantA);
    const result = await service.registerAndCrawl(
      { url: 'https://custom.com', name: 'Custom' },
      ctx,
    );

    expect(result.success).toBe(true);
    if (!result.success) return;

    expect(result.data.site.cmsType).toBe('unknown');
  });

  it('normalises the URL before storing', async () => {
    const fetcher = mockFetcher({
      'https://example.com/wp-json/wp/v2/': { status: 404, body: '' },
      'https://example.com/wp-login.php': { status: 404, body: '' },
      'https://example.com': {
        status: 200,
        body: '<html lang="en"></html>',
      },
      'https://example.com/sitemap.xml': { status: 404, body: '' },
      'https://example.com/sitemap_index.xml': { status: 404, body: '' },
    });

    const service = new SiteService(repository, fetcher);
    const ctx = createOperationContext(tenantA);
    const result = await service.registerAndCrawl(
      { url: '  EXAMPLE.COM/  ', name: 'Test' },
      ctx,
    );

    expect(result.success).toBe(true);
    if (!result.success) return;

    expect(result.data.site.url).toBe('https://example.com');
  });

  it('rejects invalid URL', async () => {
    const fetcher = mockFetcher({});
    const service = new SiteService(repository, fetcher);
    const ctx = createOperationContext(tenantA);
    const result = await service.registerAndCrawl(
      { url: '', name: 'Bad' },
      ctx,
    );

    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.error.status).toBe(400);
  });

  it('persists languages to site_language table', async () => {
    const fetcher = mockFetcher({
      'https://multi.com/wp-json/wp/v2/': { status: 404, body: '' },
      'https://multi.com/wp-login.php': { status: 404, body: '' },
      'https://multi.com': {
        status: 200,
        body: `<html lang="en"><head>
          <link rel="alternate" hreflang="en" href="https://multi.com/" />
          <link rel="alternate" hreflang="de" href="https://multi.com/de/" />
          <link rel="alternate" hreflang="fr" href="https://multi.com/fr/" />
        </head></html>`,
      },
      'https://multi.com/sitemap.xml': { status: 404, body: '' },
      'https://multi.com/sitemap_index.xml': { status: 404, body: '' },
    });

    const service = new SiteService(repository, fetcher);
    const ctx = createOperationContext(tenantA);
    const result = await service.registerAndCrawl(
      { url: 'https://multi.com', name: 'Multi' },
      ctx,
    );

    expect(result.success).toBe(true);
    if (!result.success) return;

    // Verify languages are persisted
    expect(result.data.languages).toHaveLength(3);
    expect(result.data.languages.map(l => l.code).sort()).toEqual(['de', 'en', 'fr']);
  });
});
