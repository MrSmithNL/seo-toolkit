// Tenant types — shared between StaticTenantResolver (R1) and DatabaseTenantResolver (R2)

export interface Tenant {
  readonly id: string;
  readonly name: string;
  readonly plan: 'agency' | 'starter' | 'pro';
  readonly enabledModules: readonly string[];
}

export interface TenantConfig {
  readonly [apiKey: string]: Tenant;
}

export interface ResolveContext {
  readonly apiKey: string;
}
