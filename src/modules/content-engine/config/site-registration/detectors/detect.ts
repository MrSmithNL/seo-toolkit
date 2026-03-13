// CMS detection orchestrator (TASK-006)
// Runs all detectors, returns highest-confidence match or 'unknown'.

import type { DetectionResult, HttpFetcher } from './types.js';
import { WordPressDetector } from './wordpress.js';
import { ShopifyDetector } from './shopify.js';

const detectors = [new WordPressDetector(), new ShopifyDetector()];

export async function detectCms(url: string, fetcher: HttpFetcher): Promise<DetectionResult> {
  const results = await Promise.all(
    detectors.map((d) => d.detect(url, fetcher)),
  );

  const valid = results.filter((r): r is DetectionResult => r !== null);

  if (valid.length === 0) {
    return { cmsType: 'unknown', confidence: 0, evidence: 'No CMS detected' };
  }

  // Sort by confidence descending, return highest
  valid.sort((a, b) => b.confidence - a.confidence);
  return valid[0]!;
}
