// Smoke test: real site CMS detection
// Runs against live sites — skip in CI (set SKIP_SMOKE=1)

import { describe, it, expect } from 'vitest';
import { detectCms } from '../../src/modules/content-engine/config/site-registration/detectors/detect.js';
import type { HttpFetcher } from '../../src/modules/content-engine/config/site-registration/detectors/types.js';

const SKIP = process.env.SKIP_SMOKE === '1' || process.env.CI === 'true';

// Real HTTP fetcher using Node.js fetch
const realFetcher: HttpFetcher = {
  async get(url: string) {
    try {
      const resp = await fetch(url, {
        headers: { 'User-Agent': 'SmithAI-SEOToolkit/0.2.0' },
        signal: AbortSignal.timeout(10_000),
      });
      const body = await resp.text();
      return { status: resp.status, body: body.substring(0, 50_000) };
    } catch {
      return { status: 0, body: '' };
    }
  },
};

describe.skipIf(SKIP)('Real Site CMS Detection (smoke)', () => {
  it('detects hairgenetix.com as Shopify', async () => {
    const result = await detectCms('https://hairgenetix.com', realFetcher);
    expect(result.cmsType).toBe('shopify');
    expect(result.confidence).toBeGreaterThan(0.5);
  }, 15_000);

  it('detects skingenetix.com as Shopify', async () => {
    const result = await detectCms('https://skingenetix.com', realFetcher);
    expect(result.cmsType).toBe('shopify');
    expect(result.confidence).toBeGreaterThan(0.5);
  }, 15_000);
});
