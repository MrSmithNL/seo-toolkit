// StaticTenantResolver — R1 tenant authentication via tenants.json
// Same interface as future DatabaseTenantResolver (swap via constructor injection)

import { readFileSync } from 'node:fs';
import { type Result, type OperationError, ok, err, operationError } from '../result.js';
import type { Tenant, TenantConfig, ResolveContext } from './types.js';

export class StaticTenantResolver {
  private readonly tenants: ReadonlyMap<string, Tenant>;

  constructor(configPath: string = './tenants.json') {
    const raw = readFileSync(configPath, 'utf-8');
    const parsed = JSON.parse(raw) as TenantConfig;
    this.tenants = new Map(Object.entries(parsed));
  }

  async resolve(ctx: ResolveContext): Promise<Result<Tenant, OperationError>> {
    if (!ctx.apiKey) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/authentication',
        title: 'Authentication Required',
        status: 401,
        detail: 'API key is required',
        suggestedAction: 'Provide X-Api-Key header',
      }));
    }

    const tenant = this.tenants.get(ctx.apiKey);
    if (!tenant) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/authentication',
        title: 'Invalid API Key',
        status: 401,
        detail: 'The provided API key is not valid',
        suggestedAction: 'Check your API key',
      }));
    }

    return ok(tenant);
  }
}
