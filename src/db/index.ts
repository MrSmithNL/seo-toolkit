// src/db/index.ts — Drizzle client initialisation
// R1: SQLite via better-sqlite3. R2: swap to Neon PostgreSQL.

import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';
import * as schema from './schema.js';

export type DrizzleDB = ReturnType<typeof createDatabase>;

export function createDatabase(url: string = './data/seo-toolkit.db') {
  const sqlite = new Database(url);

  // WAL mode for better concurrent read performance
  sqlite.pragma('journal_mode = WAL');
  // Enforce foreign keys
  sqlite.pragma('foreign_keys = ON');

  return drizzle(sqlite, { schema });
}
