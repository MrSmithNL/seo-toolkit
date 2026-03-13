// Shopify CMS detector (TASK-006)
// Checks page HTML for cdn.shopify.com references or Shopify.theme JS object

import type { CmsDetector, DetectionResult, HttpFetcher } from './types.js';

export class ShopifyDetector implements CmsDetector {
  readonly name = 'shopify' as const;

  async detect(url: string, fetcher: HttpFetcher): Promise<DetectionResult | null> {
    try {
      const resp = await fetcher.get(url);
      if (resp.status !== 200) return null;

      const body = resp.body;

      if (body.includes('cdn.shopify.com')) {
        return {
          cmsType: 'shopify',
          confidence: 0.9,
          evidence: 'Found cdn.shopify.com reference in page HTML',
        };
      }

      if (body.includes('Shopify.theme')) {
        return {
          cmsType: 'shopify',
          confidence: 0.85,
          evidence: 'Found Shopify.theme JavaScript object in page',
        };
      }
    } catch {
      // Network error
    }

    return null;
  }
}
