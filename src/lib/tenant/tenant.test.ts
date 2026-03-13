// TDD Red Phase — TASK-003: Tenant context middleware
// Tests StaticTenantResolver, AsyncLocalStorage context, and scoped queries

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { writeFileSync, unlinkSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';
import { eq } from 'drizzle-orm';

import * as schema from '../../db/schema.js';
import { StaticTenantResolver } from './static-tenant-resolver.js';
import { tenantContext, runWithTenant } from './tenant-context.js';
import { scopedQuery } from './scoped-query.js';
import type { Tenant, TenantConfig } from './types.js';

const TEST_TENANTS: TenantConfig = {
  'apikey_tenant_a': {
    id: 'tnt_tenant_a',
    name: 'Tenant A',
    plan: 'agency',
    enabledModules: ['content-engine-config'],
  },
  'apikey_tenant_b': {
    id: 'tnt_tenant_b',
    name: 'Tenant B',
    plan: 'starter',
    enabledModules: ['content-engine-config'],
  },
};

function createTestTenantsFile(): string {
  const path = join(tmpdir(), `tenants-test-${Date.now()}.json`);
  writeFileSync(path, JSON.stringify(TEST_TENANTS));
  return path;
}

function createTestDb() {
  const sqlite = new Database(':memory:');
  sqlite.pragma('foreign_keys = ON');
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
  return { db: drizzle(sqlite, { schema }), sqlite };
}

describe('StaticTenantResolver', () => {
  let configPath: string;
  let resolver: StaticTenantResolver;

  beforeEach(() => {
    configPath = createTestTenantsFile();
    resolver = new StaticTenantResolver(configPath);
  });

  afterEach(() => {
    if (existsSync(configPath)) unlinkSync(configPath);
  });

  it('should resolve a valid API key to a tenant', async () => {
    const result = await resolver.resolve({ apiKey: 'apikey_tenant_a' });

    expect(result.success).toBe(true);
    if (!result.success) return;
    expect(result.data.id).toBe('tnt_tenant_a');
    expect(result.data.name).toBe('Tenant A');
    expect(result.data.plan).toBe('agency');
  });

  it('should return error for invalid API key', async () => {
    const result = await resolver.resolve({ apiKey: 'apikey_invalid' });

    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.error.status).toBe(401);
  });

  it('should return error for empty API key', async () => {
    const result = await resolver.resolve({ apiKey: '' });

    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.error.status).toBe(401);
  });

  it('should load multiple tenants', async () => {
    const resultA = await resolver.resolve({ apiKey: 'apikey_tenant_a' });
    const resultB = await resolver.resolve({ apiKey: 'apikey_tenant_b' });

    expect(resultA.success).toBe(true);
    expect(resultB.success).toBe(true);
    if (!resultA.success || !resultB.success) return;
    expect(resultA.data.id).toBe('tnt_tenant_a');
    expect(resultB.data.id).toBe('tnt_tenant_b');
  });
});

describe('Tenant Context (AsyncLocalStorage)', () => {
  it('should provide tenant ID within runWithTenant scope', async () => {
    let capturedTenantId: string | undefined;

    await runWithTenant('tnt_test123', async () => {
      capturedTenantId = tenantContext.getTenantId();
    });

    expect(capturedTenantId).toBe('tnt_test123');
  });

  it('should return undefined outside of tenant scope', () => {
    const tenantId = tenantContext.getTenantId();
    expect(tenantId).toBeUndefined();
  });

  it('should isolate tenant context between concurrent calls', async () => {
    const results: string[] = [];

    await Promise.all([
      runWithTenant('tnt_first', async () => {
        await new Promise(r => setTimeout(r, 10));
        results.push(tenantContext.getTenantId()!);
      }),
      runWithTenant('tnt_second', async () => {
        results.push(tenantContext.getTenantId()!);
      }),
    ]);

    expect(results).toContain('tnt_first');
    expect(results).toContain('tnt_second');
  });
});

describe('Scoped Query (tenant isolation)', () => {
  let db: ReturnType<typeof drizzle>;
  let sqlite: Database.Database;

  beforeEach(() => {
    const testDb = createTestDb();
    db = testDb.db;
    sqlite = testDb.sqlite;

    // Seed data for two tenants
    db.insert(schema.siteConfig).values({
      id: 'ste_a1', tenantId: 'tnt_tenant_a', url: 'https://a1.com', name: 'A Site 1',
    }).run();
    db.insert(schema.siteConfig).values({
      id: 'ste_a2', tenantId: 'tnt_tenant_a', url: 'https://a2.com', name: 'A Site 2',
    }).run();
    db.insert(schema.siteConfig).values({
      id: 'ste_b1', tenantId: 'tnt_tenant_b', url: 'https://b1.com', name: 'B Site 1',
    }).run();
  });

  afterEach(() => {
    sqlite.close();
  });

  it('should only return rows for the scoped tenant', () => {
    const rows = scopedQuery(db, schema.siteConfig, 'tnt_tenant_a');
    expect(rows).toHaveLength(2);
    expect(rows.every(r => r.tenantId === 'tnt_tenant_a')).toBe(true);
  });

  it('should not return other tenant rows', () => {
    const rows = scopedQuery(db, schema.siteConfig, 'tnt_tenant_b');
    expect(rows).toHaveLength(1);
    expect(rows[0]!.tenantId).toBe('tnt_tenant_b');
  });

  it('should return empty for non-existent tenant', () => {
    const rows = scopedQuery(db, schema.siteConfig, 'tnt_nobody');
    expect(rows).toHaveLength(0);
  });
});
