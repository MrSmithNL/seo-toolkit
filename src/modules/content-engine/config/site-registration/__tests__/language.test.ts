// TASK-007: Language detection — hreflang, Shopify locales, html lang
// TDD: Tests first with mocked HTTP.

import { describe, it, expect } from 'vitest';
import { detectLanguages } from '../detectors/language.js';
import type { HttpFetcher, HttpResponse } from '../detectors/types.js';

function mockFetcher(responses: Record<string, HttpResponse>): HttpFetcher {
  return {
    async get(url: string): Promise<HttpResponse> {
      const resp = responses[url];
      if (resp) return resp;
      return { status: 404, body: '' };
    },
  };
}

describe('detectLanguages', () => {
  describe('hreflang tags', () => {
    it('detects languages from hreflang link elements', async () => {
      const fetcher = mockFetcher({
        'https://example.com': {
          status: 200,
          body: `<html>
            <head>
              <link rel="alternate" hreflang="en" href="https://example.com" />
              <link rel="alternate" hreflang="nl" href="https://example.com/nl/" />
              <link rel="alternate" hreflang="de" href="https://example.com/de/" />
            </head>
          </html>`,
        },
      });

      const langs = await detectLanguages('https://example.com', fetcher);
      expect(langs).toHaveLength(3);
      expect(langs.map(l => l.code)).toContain('en');
      expect(langs.map(l => l.code)).toContain('nl');
      expect(langs.map(l => l.code)).toContain('de');
    });

    it('extracts URL pattern from hreflang', async () => {
      const fetcher = mockFetcher({
        'https://example.com': {
          status: 200,
          body: `<html><head>
            <link rel="alternate" hreflang="nl" href="https://example.com/nl/" />
          </head></html>`,
        },
      });

      const langs = await detectLanguages('https://example.com', fetcher);
      const nl = langs.find(l => l.code === 'nl');
      expect(nl?.urlPattern).toBe('https://example.com/nl/');
    });
  });

  describe('html lang attribute', () => {
    it('detects language from html lang attribute', async () => {
      const fetcher = mockFetcher({
        'https://example.com': {
          status: 200,
          body: '<html lang="fr"><head><title>Site Français</title></head></html>',
        },
      });

      const langs = await detectLanguages('https://example.com', fetcher);
      expect(langs).toHaveLength(1);
      expect(langs[0]!.code).toBe('fr');
    });

    it('handles lang with region code (en-US → en)', async () => {
      const fetcher = mockFetcher({
        'https://example.com': {
          status: 200,
          body: '<html lang="en-US"><head></head></html>',
        },
      });

      const langs = await detectLanguages('https://example.com', fetcher);
      expect(langs[0]!.code).toBe('en');
    });
  });

  describe('Shopify locale URLs', () => {
    it('detects Shopify locale alternates', async () => {
      const fetcher = mockFetcher({
        'https://example.com': {
          status: 200,
          body: `<html lang="en">
            <head>
              <link rel="alternate" hreflang="en" href="https://example.com/" />
              <link rel="alternate" hreflang="nl" href="https://example.com/nl" />
            </head>
          </html>`,
        },
      });

      const langs = await detectLanguages('https://example.com', fetcher);
      expect(langs).toHaveLength(2);
      expect(langs.map(l => l.code)).toContain('en');
      expect(langs.map(l => l.code)).toContain('nl');
    });
  });

  describe('fallback', () => {
    it('returns en as default when no language signals found', async () => {
      const fetcher = mockFetcher({
        'https://example.com': {
          status: 200,
          body: '<html><head><title>No lang</title></head></html>',
        },
      });

      const langs = await detectLanguages('https://example.com', fetcher);
      expect(langs).toHaveLength(1);
      expect(langs[0]!.code).toBe('en');
      expect(langs[0]!.name).toBe('English');
    });

    it('returns en on fetch failure', async () => {
      const fetcher: HttpFetcher = {
        async get(): Promise<HttpResponse> {
          throw new Error('Network error');
        },
      };

      const langs = await detectLanguages('https://example.com', fetcher);
      expect(langs).toHaveLength(1);
      expect(langs[0]!.code).toBe('en');
    });
  });

  describe('deduplication', () => {
    it('deduplicates languages from multiple sources', async () => {
      const fetcher = mockFetcher({
        'https://example.com': {
          status: 200,
          body: `<html lang="en">
            <head>
              <link rel="alternate" hreflang="en" href="https://example.com/" />
            </head>
          </html>`,
        },
      });

      const langs = await detectLanguages('https://example.com', fetcher);
      const enCount = langs.filter(l => l.code === 'en').length;
      expect(enCount).toBe(1);
    });
  });
});
