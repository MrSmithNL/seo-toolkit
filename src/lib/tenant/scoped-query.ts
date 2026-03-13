// Scoped query — auto-adds WHERE tenant_id = ? to all queries
// This is the R1 equivalent of PostgreSQL RLS policies

import { eq } from 'drizzle-orm';
import type { SQLiteColumn } from 'drizzle-orm/sqlite-core';
import type { DrizzleDB } from '../../db/index.js';

interface TenantScopedTable {
  tenantId: SQLiteColumn;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function scopedQuery<T extends TenantScopedTable>(
  db: DrizzleDB,
  table: T,
  tenantId: string,
) {
  return db
    .select()
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    .from(table as any)
    .where(eq(table.tenantId, tenantId))
    .all();
}
