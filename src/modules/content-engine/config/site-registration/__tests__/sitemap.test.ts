// TASK-008: Sitemap parser — content inventory
// TDD: Tests first with mocked HTTP.

import { describe, it, expect } from 'vitest';
import { parseSitemap } from '../sitemap.js';
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

describe('parseSitemap', () => {
  it('counts URLs from a simple sitemap.xml', async () => {
    const fetcher = mockFetcher({
      'https://example.com/sitemap.xml': {
        status: 200,
        body: `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/</loc></url>
  <url><loc>https://example.com/about</loc></url>
  <url><loc>https://example.com/blog/post-1</loc></url>
</urlset>`,
      },
    });

    const result = await parseSitemap('https://example.com', fetcher);
    expect(result.contentCount).toBe(3);
    expect(result.sitemapFound).toBe(true);
  });

  it('follows sitemap index to child sitemaps', async () => {
    const fetcher = mockFetcher({
      'https://example.com/sitemap.xml': {
        status: 200,
        body: `<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>https://example.com/sitemap-posts.xml</loc></sitemap>
  <sitemap><loc>https://example.com/sitemap-pages.xml</loc></sitemap>
</sitemapindex>`,
      },
      'https://example.com/sitemap-posts.xml': {
        status: 200,
        body: `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/blog/post-1</loc></url>
  <url><loc>https://example.com/blog/post-2</loc></url>
</urlset>`,
      },
      'https://example.com/sitemap-pages.xml': {
        status: 200,
        body: `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/about</loc></url>
</urlset>`,
      },
    });

    const result = await parseSitemap('https://example.com', fetcher);
    expect(result.contentCount).toBe(3);
    expect(result.sitemapFound).toBe(true);
  });

  it('returns 0 with sitemapFound=false when no sitemap exists', async () => {
    const fetcher = mockFetcher({});

    const result = await parseSitemap('https://example.com', fetcher);
    expect(result.contentCount).toBe(0);
    expect(result.sitemapFound).toBe(false);
  });

  it('handles fetch error gracefully', async () => {
    const fetcher: HttpFetcher = {
      async get(): Promise<HttpResponse> {
        throw new Error('Network error');
      },
    };

    const result = await parseSitemap('https://example.com', fetcher);
    expect(result.contentCount).toBe(0);
    expect(result.sitemapFound).toBe(false);
  });

  it('excludes image and asset URLs', async () => {
    const fetcher = mockFetcher({
      'https://example.com/sitemap.xml': {
        status: 200,
        body: `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/about</loc></url>
  <url><loc>https://example.com/images/logo.png</loc></url>
  <url><loc>https://example.com/assets/style.css</loc></url>
  <url><loc>https://example.com/blog/post-1</loc></url>
</urlset>`,
      },
    });

    const result = await parseSitemap('https://example.com', fetcher);
    expect(result.contentCount).toBe(2); // excludes .png and .css
  });

  it('tries sitemap_index.xml as fallback', async () => {
    const fetcher = mockFetcher({
      'https://example.com/sitemap.xml': { status: 404, body: '' },
      'https://example.com/sitemap_index.xml': {
        status: 200,
        body: `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/page-1</loc></url>
</urlset>`,
      },
    });

    const result = await parseSitemap('https://example.com', fetcher);
    expect(result.contentCount).toBe(1);
    expect(result.sitemapFound).toBe(true);
  });
});
