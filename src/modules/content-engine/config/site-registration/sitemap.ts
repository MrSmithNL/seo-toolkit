// Sitemap parser — content inventory (TASK-008)
// F-001 US-004: Count content URLs from sitemap.xml / sitemap_index.xml

import type { HttpFetcher } from './detectors/types.js';

export interface SitemapResult {
  readonly contentCount: number;
  readonly sitemapFound: boolean;
}

const ASSET_EXTENSIONS = /\.(png|jpg|jpeg|gif|svg|webp|ico|css|js|woff|woff2|ttf|eot|pdf|mp4|mp3|zip)$/i;

function extractLocs(xml: string): string[] {
  const locs: string[] = [];
  const regex = /<loc>([^<]+)<\/loc>/g;
  let match: RegExpExecArray | null;
  while ((match = regex.exec(xml)) !== null) {
    locs.push(match[1]!.trim());
  }
  return locs;
}

function isSitemapIndex(xml: string): boolean {
  return xml.includes('<sitemapindex');
}

function isContentUrl(url: string): boolean {
  return !ASSET_EXTENSIONS.test(url);
}

async function fetchSitemap(url: string, fetcher: HttpFetcher): Promise<string | null> {
  try {
    const resp = await fetcher.get(url);
    if (resp.status === 200 && resp.body.includes('<')) {
      return resp.body;
    }
  } catch {
    // Network error
  }
  return null;
}

export async function parseSitemap(siteUrl: string, fetcher: HttpFetcher): Promise<SitemapResult> {
  // Try sitemap.xml first, then sitemap_index.xml fallback
  let xml = await fetchSitemap(`${siteUrl}/sitemap.xml`, fetcher);
  if (!xml) {
    xml = await fetchSitemap(`${siteUrl}/sitemap_index.xml`, fetcher);
  }

  if (!xml) {
    return { contentCount: 0, sitemapFound: false };
  }

  let contentCount = 0;

  if (isSitemapIndex(xml)) {
    // Parse child sitemap URLs and fetch each
    const childUrls = extractLocs(xml);
    const childResults = await Promise.all(
      childUrls.map(async (childUrl) => {
        const childXml = await fetchSitemap(childUrl, fetcher);
        if (!childXml) return 0;
        return extractLocs(childXml).filter(isContentUrl).length;
      }),
    );
    contentCount = childResults.reduce((sum, c) => sum + c, 0);
  } else {
    contentCount = extractLocs(xml).filter(isContentUrl).length;
  }

  return { contentCount, sitemapFound: true };
}
