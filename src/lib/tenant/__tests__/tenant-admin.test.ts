// TASK-005a: Tenant administration — add, list, remove, rotate-key
// TDD: Tests first.

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { TenantAdmin } from '../tenant-admin.js';
import { writeFileSync, mkdirSync, rmSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { randomBytes } from 'node:crypto';

describe('TenantAdmin', () => {
  let admin: TenantAdmin;
  let tenantsPath: string;
  let tmpDir: string;

  beforeEach(() => {
    tmpDir = join(tmpdir(), `tenant-admin-test-${randomBytes(4).toString('hex')}`);
    mkdirSync(tmpDir, { recursive: true });
    tenantsPath = join(tmpDir, 'tenants.json');
    admin = new TenantAdmin(tenantsPath);
  });

  afterEach(() => {
    if (existsSync(tmpDir)) {
      rmSync(tmpDir, { recursive: true });
    }
  });

  describe('add', () => {
    it('creates a new tenant with prefixed ID and API key', () => {
      const result = admin.add({ name: 'Test Tenant', plan: 'agency' });

      expect(result.tenant.id).toMatch(/^tnt_/);
      expect(result.tenant.name).toBe('Test Tenant');
      expect(result.tenant.plan).toBe('agency');
      expect(result.tenant.enabledModules).toEqual([]);
      expect(result.apiKey).toMatch(/^apikey_/);
      expect(result.apiKey.length).toBeGreaterThan(20);
    });

    it('persists tenant to JSON file', () => {
      const result = admin.add({ name: 'Persisted', plan: 'starter' });

      // Reload from disk
      const freshAdmin = new TenantAdmin(tenantsPath);
      const tenants = freshAdmin.list();

      expect(tenants).toHaveLength(1);
      expect(tenants[0]!.id).toBe(result.tenant.id);
      expect(tenants[0]!.name).toBe('Persisted');
    });

    it('can add multiple tenants', () => {
      admin.add({ name: 'Tenant A', plan: 'agency' });
      admin.add({ name: 'Tenant B', plan: 'pro' });
      admin.add({ name: 'Tenant C', plan: 'starter' });

      expect(admin.list()).toHaveLength(3);
    });

    it('generates unique API keys for each tenant', () => {
      const a = admin.add({ name: 'A', plan: 'agency' });
      const b = admin.add({ name: 'B', plan: 'agency' });

      expect(a.apiKey).not.toBe(b.apiKey);
    });

    it('defaults plan to starter when not specified', () => {
      const result = admin.add({ name: 'Default Plan' });

      expect(result.tenant.plan).toBe('starter');
    });
  });

  describe('list', () => {
    it('returns empty array when no tenants exist', () => {
      expect(admin.list()).toEqual([]);
    });

    it('returns all tenants', () => {
      admin.add({ name: 'A', plan: 'agency' });
      admin.add({ name: 'B', plan: 'pro' });

      const tenants = admin.list();
      expect(tenants).toHaveLength(2);
      expect(tenants.map(t => t.name)).toContain('A');
      expect(tenants.map(t => t.name)).toContain('B');
    });

    it('works with pre-existing tenants.json', () => {
      // Write a manual tenants.json
      writeFileSync(tenantsPath, JSON.stringify({
        'apikey_manual123': {
          id: 'tnt_manual',
          name: 'Manual Tenant',
          plan: 'agency',
          enabledModules: ['content-engine'],
        },
      }));

      const freshAdmin = new TenantAdmin(tenantsPath);
      const tenants = freshAdmin.list();

      expect(tenants).toHaveLength(1);
      expect(tenants[0]!.name).toBe('Manual Tenant');
    });
  });

  describe('remove', () => {
    it('removes a tenant by ID', () => {
      const result = admin.add({ name: 'To Remove', plan: 'agency' });
      admin.add({ name: 'To Keep', plan: 'pro' });

      const removed = admin.remove(result.tenant.id);

      expect(removed).toBe(true);
      expect(admin.list()).toHaveLength(1);
      expect(admin.list()[0]!.name).toBe('To Keep');
    });

    it('returns false for non-existent tenant', () => {
      const removed = admin.remove('tnt_nonexistent');

      expect(removed).toBe(false);
    });

    it('persists removal to disk', () => {
      const result = admin.add({ name: 'Gone', plan: 'agency' });
      admin.remove(result.tenant.id);

      const freshAdmin = new TenantAdmin(tenantsPath);
      expect(freshAdmin.list()).toHaveLength(0);
    });
  });

  describe('rotateKey', () => {
    it('returns a new API key for existing tenant', () => {
      const original = admin.add({ name: 'Rotate Me', plan: 'agency' });
      const newKey = admin.rotateKey(original.tenant.id);

      expect(newKey).not.toBeNull();
      expect(newKey).toMatch(/^apikey_/);
      expect(newKey).not.toBe(original.apiKey);
    });

    it('old key no longer resolves', () => {
      const original = admin.add({ name: 'Old Key', plan: 'agency' });
      admin.rotateKey(original.tenant.id);

      // Reload and check old key is gone
      const freshAdmin = new TenantAdmin(tenantsPath);
      const config = freshAdmin.getConfig();

      expect(config[original.apiKey]).toBeUndefined();
    });

    it('new key resolves to same tenant', () => {
      const original = admin.add({ name: 'Same Tenant', plan: 'agency' });
      const newKey = admin.rotateKey(original.tenant.id)!;

      const freshAdmin = new TenantAdmin(tenantsPath);
      const config = freshAdmin.getConfig();

      expect(config[newKey]!.id).toBe(original.tenant.id);
      expect(config[newKey]!.name).toBe('Same Tenant');
    });

    it('returns null for non-existent tenant', () => {
      const result = admin.rotateKey('tnt_nonexistent');

      expect(result).toBeNull();
    });

    it('persists key rotation to disk', () => {
      const original = admin.add({ name: 'Persist', plan: 'agency' });
      const newKey = admin.rotateKey(original.tenant.id)!;

      const freshAdmin = new TenantAdmin(tenantsPath);
      const config = freshAdmin.getConfig();

      expect(config[original.apiKey]).toBeUndefined();
      expect(config[newKey]).toBeDefined();
    });
  });
});
