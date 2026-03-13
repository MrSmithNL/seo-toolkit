// WordPress CMS detector (TASK-006)
// Checks: 1) /wp-json/wp/v2/ endpoint, 2) /wp-login.php fallback

import type { CmsDetector, DetectionResult, HttpFetcher } from './types.js';

export class WordPressDetector implements CmsDetector {
  readonly name = 'wordpress' as const;

  async detect(url: string, fetcher: HttpFetcher): Promise<DetectionResult | null> {
    try {
      // Primary signal: WP REST API
      const apiResp = await fetcher.get(`${url}/wp-json/wp/v2/`);
      if (apiResp.status === 200) {
        return {
          cmsType: 'wordpress',
          confidence: 0.95,
          evidence: 'WP REST API endpoint responded at /wp-json/wp/v2/',
        };
      }
    } catch {
      // Network error — try fallback
    }

    try {
      // Fallback signal: wp-login page
      const loginResp = await fetcher.get(`${url}/wp-login.php`);
      if (loginResp.status === 200) {
        return {
          cmsType: 'wordpress',
          confidence: 0.7,
          evidence: 'WordPress login page found at /wp-login.php',
        };
      }
    } catch {
      // Network error
    }

    return null;
  }
}
