// TenantAdmin — CRUD for tenants.json (TASK-005a)
// Bridges manual JSON editing and future PROD-004 SaaS tenant management.

import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { randomBytes } from 'node:crypto';
import { generateId } from '../id.js';
import type { Tenant, TenantConfig } from './types.js';

interface AddTenantInput {
  name: string;
  plan?: 'agency' | 'starter' | 'pro';
}

interface AddTenantResult {
  tenant: Tenant;
  apiKey: string;
}

function generateApiKey(): string {
  return `apikey_${randomBytes(32).toString('hex')}`;
}

export class TenantAdmin {
  private config: TenantConfig;

  constructor(private readonly filePath: string) {
    this.config = this.load();
  }

  add(input: AddTenantInput): AddTenantResult {
    const tenant: Tenant = {
      id: generateId('tenant'),
      name: input.name,
      plan: input.plan ?? 'starter',
      enabledModules: [],
    };

    const apiKey = generateApiKey();
    this.config = { ...this.config, [apiKey]: tenant };
    this.save();

    return { tenant, apiKey };
  }

  list(): Tenant[] {
    return Object.values(this.config);
  }

  remove(tenantId: string): boolean {
    const entry = Object.entries(this.config).find(([, t]) => t.id === tenantId);
    if (!entry) return false;

    const { [entry[0]]: _, ...rest } = this.config;
    this.config = rest;
    this.save();
    return true;
  }

  rotateKey(tenantId: string): string | null {
    const entry = Object.entries(this.config).find(([, t]) => t.id === tenantId);
    if (!entry) return null;

    const [oldKey, tenant] = entry;
    const newKey = generateApiKey();

    const { [oldKey]: _, ...rest } = this.config;
    this.config = { ...rest, [newKey]: tenant };
    this.save();

    return newKey;
  }

  getConfig(): TenantConfig {
    return { ...this.config };
  }

  private load(): TenantConfig {
    if (!existsSync(this.filePath)) return {};
    const raw = readFileSync(this.filePath, 'utf-8');
    return JSON.parse(raw) as TenantConfig;
  }

  private save(): void {
    writeFileSync(this.filePath, JSON.stringify(this.config, null, 2) + '\n');
  }
}
