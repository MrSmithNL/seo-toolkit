// src/db/schema.ts — content-engine-config module
// Full data model: 8 tables for all 6 E-001 features.
// R1: SQLite tables. R2: swap imports to 'drizzle-orm/pg-core' (pgTable, pgPolicy, etc.)

import { sqliteTable, text, integer, real, uniqueIndex, index } from 'drizzle-orm/sqlite-core';
import { relations, sql } from 'drizzle-orm';

// === Root aggregate ===

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

// === F-001: Site Registration — detected languages ===

export const siteLanguage = sqliteTable('site_language', {
  id:         text('id').primaryKey(),
  siteId:     text('site_id').notNull().references(() => siteConfig.id, { onDelete: 'cascade' }),
  code:       text('code').notNull(),
  name:       text('name').notNull(),
  urlPattern: text('url_pattern'),
}, (table) => [
  uniqueIndex('site_language_site_code_idx').on(table.siteId, table.code),
]);

// === F-002: CMS Connection ===

export const cmsConnection = sqliteTable('cms_connection', {
  id:                    text('id').primaryKey(),
  siteId:                text('site_id').notNull().unique().references(() => siteConfig.id, { onDelete: 'cascade' }),
  cmsType:               text('cms_type').notNull(),
  status:                text('status').default('pending'),
  wpSiteUrl:             text('wp_site_url'),
  wpUsername:             text('wp_username'),
  wpApplicationPassword: text('wp_application_password'),
  shopifyStoreDomain:    text('shopify_store_domain'),
  shopifyAccessToken:    text('shopify_access_token'),
  defaultPublishStatus:  text('default_publish_status').default('draft'),
  verifiedAt:            text('verified_at'),
  lastUsedAt:            text('last_used_at'),
  createdAt:             text('created_at').notNull().default(sql`(datetime('now'))`),
  updatedAt:             text('updated_at').notNull().default(sql`(datetime('now'))`),
});

// === F-003: Brand Voice ===

export const voiceProfile = sqliteTable('voice_profile', {
  id:                text('id').primaryKey(),
  siteId:            text('site_id').notNull().unique().references(() => siteConfig.id, { onDelete: 'cascade' }),
  brandName:         text('brand_name'),
  industry:          text('industry'),
  targetAudience:    text('target_audience'),
  brandValues:       text('brand_values'),
  keyTopics:         text('key_topics'),
  tone:              text('tone').default('conversational'),
  sentenceStructure: text('sentence_structure').default('mixed'),
  vocabularyLevel:   text('vocabulary_level').default('intermediate'),
  person:            text('person').default('second'),
  extractedFromUrl:  text('extracted_from_url'),
  extractedAt:       text('extracted_at'),
  createdAt:         text('created_at').notNull().default(sql`(datetime('now'))`),
  updatedAt:         text('updated_at').notNull().default(sql`(datetime('now'))`),
});

// === F-004: Topic Configuration ===

export const topicConfig = sqliteTable('topic_config', {
  id:           text('id').primaryKey(),
  siteId:       text('site_id').notNull().unique().references(() => siteConfig.id, { onDelete: 'cascade' }),
  source:       text('source').default('manual'),
  seedKeywords: text('seed_keywords'),
  createdAt:    text('created_at').notNull().default(sql`(datetime('now'))`),
  updatedAt:    text('updated_at').notNull().default(sql`(datetime('now'))`),
});

export const topicCluster = sqliteTable('topic_cluster', {
  id:            text('id').primaryKey(),
  topicConfigId: text('topic_config_id').notNull().references(() => topicConfig.id, { onDelete: 'cascade' }),
  name:          text('name').notNull(),
  keywords:      text('keywords').notNull(),
  priority:      text('priority').default('medium'),
  contentCount:  integer('content_count').default(0),
});

// === F-005: Quality Thresholds ===

export const qualityThresholds = sqliteTable('quality_thresholds', {
  id:                text('id').primaryKey(),
  siteId:            text('site_id').notNull().unique().references(() => siteConfig.id, { onDelete: 'cascade' }),
  seoScoreMin:       integer('seo_score_min').default(65),
  aisoScoreMin:      real('aiso_score_min').default(7.0),
  readabilityTarget: text('readability_target').default('grade_8'),
  wordCountMin:      integer('word_count_min').default(1500),
  wordCountMax:      integer('word_count_max').default(3000),
  publishMode:       text('publish_mode').default('draft_review'),
  createdAt:         text('created_at').notNull().default(sql`(datetime('now'))`),
  updatedAt:         text('updated_at').notNull().default(sql`(datetime('now'))`),
});

// === F-006: AISO Preferences ===

export const aisoPreferences = sqliteTable('aiso_preferences', {
  id:                text('id').primaryKey(),
  siteId:            text('site_id').notNull().unique().references(() => siteConfig.id, { onDelete: 'cascade' }),
  useRecommended:    integer('use_recommended', { mode: 'boolean' }).default(true),
  priorityFactors:   text('priority_factors'),
  schemaTypes:       text('schema_types'),
  aiPlatformTargets: text('ai_platform_targets'),
  createdAt:         text('created_at').notNull().default(sql`(datetime('now'))`),
  updatedAt:         text('updated_at').notNull().default(sql`(datetime('now'))`),
});

// === Relations (for Drizzle relational queries) ===

export const siteConfigRelations = relations(siteConfig, ({ many, one }) => ({
  languages:         many(siteLanguage),
  cmsConnection:     one(cmsConnection),
  voiceProfile:      one(voiceProfile),
  topicConfig:       one(topicConfig),
  qualityThresholds: one(qualityThresholds),
  aisoPreferences:   one(aisoPreferences),
}));

export const siteLanguageRelations = relations(siteLanguage, ({ one }) => ({
  site: one(siteConfig, { fields: [siteLanguage.siteId], references: [siteConfig.id] }),
}));

export const cmsConnectionRelations = relations(cmsConnection, ({ one }) => ({
  site: one(siteConfig, { fields: [cmsConnection.siteId], references: [siteConfig.id] }),
}));

export const voiceProfileRelations = relations(voiceProfile, ({ one }) => ({
  site: one(siteConfig, { fields: [voiceProfile.siteId], references: [siteConfig.id] }),
}));

export const topicConfigRelations = relations(topicConfig, ({ one, many }) => ({
  site:     one(siteConfig, { fields: [topicConfig.siteId], references: [siteConfig.id] }),
  clusters: many(topicCluster),
}));

export const topicClusterRelations = relations(topicCluster, ({ one }) => ({
  config: one(topicConfig, { fields: [topicCluster.topicConfigId], references: [topicConfig.id] }),
}));

export const qualityThresholdsRelations = relations(qualityThresholds, ({ one }) => ({
  site: one(siteConfig, { fields: [qualityThresholds.siteId], references: [siteConfig.id] }),
}));

export const aisoPreferencesRelations = relations(aisoPreferences, ({ one }) => ({
  site: one(siteConfig, { fields: [aisoPreferences.siteId], references: [siteConfig.id] }),
}));
