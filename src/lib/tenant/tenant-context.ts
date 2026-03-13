// Tenant context via AsyncLocalStorage — per-request tenant isolation
// R1: set by StaticTenantResolver. R2: set by DatabaseTenantResolver.

import { AsyncLocalStorage } from 'node:async_hooks';

interface TenantStore {
  readonly tenantId: string;
}

const asyncLocalStorage = new AsyncLocalStorage<TenantStore>();

export const tenantContext = {
  getTenantId(): string | undefined {
    return asyncLocalStorage.getStore()?.tenantId;
  },
} as const;

export function runWithTenant<T>(tenantId: string, fn: () => T): T {
  return asyncLocalStorage.run({ tenantId }, fn);
}
