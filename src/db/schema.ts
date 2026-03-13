// src/db/schema.ts — content-engine-config module
// Walking skeleton: siteConfig table only. Full schema in TASK-002.

import { sqliteTable, text, integer, uniqueIndex, index } from 'drizzle-orm/sqlite-core';
import { sql } from 'drizzle-orm';

export const siteConfig = sqliteTable('site_config', {
  id:              text('id').primaryKey(),
  tenantId:        text('tenant_id').notNull(),
  url:             text('url').notNull(),
  name:            text('name').notNull(),
  cmsType:         text('cms_type').default('unknown'),
  cmsDetectedAt:   text('cms_detected_at'),
  primaryLanguage: text('primary_language').default('en'),
  contentCount:    integer('content_count').default(0),
  lastCrawled:     text('last_crawled'),
  createdAt:       text('created_at').notNull().default(sql`(datetime('now'))`),
  updatedAt:       text('updated_at').notNull().default(sql`(datetime('now'))`),
}, (table) => [
  uniqueIndex('site_config_tenant_url_idx').on(table.tenantId, table.url),
  index('site_config_tenant_idx').on(table.tenantId),
]);
