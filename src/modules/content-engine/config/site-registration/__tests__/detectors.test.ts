// TASK-006: CMS detection — WordPress + Shopify detectors
// TDD: Tests first with mocked HTTP.

import { describe, it, expect } from 'vitest';
import { WordPressDetector } from '../detectors/wordpress.js';
import { ShopifyDetector } from '../detectors/shopify.js';
import { detectCms } from '../detectors/detect.js';
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

describe('WordPressDetector', () => {
  const detector = new WordPressDetector();

  it('detects WordPress via wp-json endpoint', async () => {
    const fetcher = mockFetcher({
      'https://example.com/wp-json/wp/v2/': {
        status: 200,
        body: '{"name":"Example Site","description":"Just another WordPress site"}',
      },
    });

    const result = await detector.detect('https://example.com', fetcher);
    expect(result).not.toBeNull();
    expect(result!.cmsType).toBe('wordpress');
    expect(result!.confidence).toBeGreaterThanOrEqual(0.9);
  });

  it('detects WordPress via wp-login.php fallback', async () => {
    const fetcher = mockFetcher({
      'https://example.com/wp-json/wp/v2/': { status: 404, body: '' },
      'https://example.com/wp-login.php': {
        status: 200,
        body: '<html><body>WordPress login</body></html>',
      },
    });

    const result = await detector.detect('https://example.com', fetcher);
    expect(result).not.toBeNull();
    expect(result!.cmsType).toBe('wordpress');
    expect(result!.confidence).toBeGreaterThanOrEqual(0.7);
  });

  it('returns null when no WordPress signals found', async () => {
    const fetcher = mockFetcher({
      'https://example.com/wp-json/wp/v2/': { status: 404, body: '' },
      'https://example.com/wp-login.php': { status: 404, body: '' },
    });

    const result = await detector.detect('https://example.com', fetcher);
    expect(result).toBeNull();
  });

  it('handles network errors gracefully', async () => {
    const fetcher: HttpFetcher = {
      async get(): Promise<HttpResponse> {
        throw new Error('Network error');
      },
    };

    const result = await detector.detect('https://example.com', fetcher);
    expect(result).toBeNull();
  });
});

describe('ShopifyDetector', () => {
  const detector = new ShopifyDetector();

  it('detects Shopify via cdn.shopify.com in HTML', async () => {
    const fetcher = mockFetcher({
      'https://example.com': {
        status: 200,
        body: '<html><head><link href="https://cdn.shopify.com/s/files/1/theme.css"></head></html>',
      },
    });

    const result = await detector.detect('https://example.com', fetcher);
    expect(result).not.toBeNull();
    expect(result!.cmsType).toBe('shopify');
    expect(result!.confidence).toBeGreaterThanOrEqual(0.9);
  });

  it('detects Shopify via Shopify.theme in script', async () => {
    const fetcher = mockFetcher({
      'https://example.com': {
        status: 200,
        body: '<html><script>Shopify.theme = {name: "Dawn"};</script></html>',
      },
    });

    const result = await detector.detect('https://example.com', fetcher);
    expect(result).not.toBeNull();
    expect(result!.cmsType).toBe('shopify');
  });

  it('returns null when no Shopify signals found', async () => {
    const fetcher = mockFetcher({
      'https://example.com': {
        status: 200,
        body: '<html><head><title>Plain site</title></head></html>',
      },
    });

    const result = await detector.detect('https://example.com', fetcher);
    expect(result).toBeNull();
  });

  it('handles fetch failure gracefully', async () => {
    const fetcher: HttpFetcher = {
      async get(): Promise<HttpResponse> {
        throw new Error('Connection refused');
      },
    };

    const result = await detector.detect('https://example.com', fetcher);
    expect(result).toBeNull();
  });
});

describe('detectCms (orchestrator)', () => {
  it('returns wordpress when WordPress signals detected', async () => {
    const fetcher = mockFetcher({
      'https://example.com/wp-json/wp/v2/': {
        status: 200,
        body: '{"name":"WP Site"}',
      },
      'https://example.com': {
        status: 200,
        body: '<html><title>WP Site</title></html>',
      },
    });

    const result = await detectCms('https://example.com', fetcher);
    expect(result.cmsType).toBe('wordpress');
  });

  it('returns shopify when Shopify signals detected', async () => {
    const fetcher = mockFetcher({
      'https://example.com/wp-json/wp/v2/': { status: 404, body: '' },
      'https://example.com/wp-login.php': { status: 404, body: '' },
      'https://example.com': {
        status: 200,
        body: '<html><link href="https://cdn.shopify.com/s/files/theme.css"></html>',
      },
    });

    const result = await detectCms('https://example.com', fetcher);
    expect(result.cmsType).toBe('shopify');
  });

  it('returns unknown when no CMS detected', async () => {
    const fetcher = mockFetcher({
      'https://example.com/wp-json/wp/v2/': { status: 404, body: '' },
      'https://example.com/wp-login.php': { status: 404, body: '' },
      'https://example.com': {
        status: 200,
        body: '<html><title>Static site</title></html>',
      },
    });

    const result = await detectCms('https://example.com', fetcher);
    expect(result.cmsType).toBe('unknown');
  });

  it('picks highest confidence when multiple detectors match', async () => {
    // Both WP and Shopify signals — WP should win with higher confidence from wp-json
    const fetcher = mockFetcher({
      'https://example.com/wp-json/wp/v2/': {
        status: 200,
        body: '{"name":"Weird site"}',
      },
      'https://example.com': {
        status: 200,
        body: '<html><link href="https://cdn.shopify.com/s/files/theme.css"></html>',
      },
    });

    const result = await detectCms('https://example.com', fetcher);
    // wp-json gives 0.95 confidence, Shopify CDN gives 0.9
    expect(result.cmsType).toBe('wordpress');
  });
});
