// WordPress CMS detector (TASK-006)
// Checks: 1) /wp-json/wp/v2/ endpoint (validates JSON body), 2) /wp-login.php fallback (validates form)

import type { CmsDetector, DetectionResult, HttpFetcher } from './types.js';

export class WordPressDetector implements CmsDetector {
  readonly name = 'wordpress' as const;

  async detect(url: string, fetcher: HttpFetcher): Promise<DetectionResult | null> {
    try {
      // Primary signal: WP REST API — must return JSON containing WP-specific markers
      const apiResp = await fetcher.get(`${url}/wp-json/wp/v2/`);
      if (apiResp.status === 200 && this.isWordPressApiResponse(apiResp.body)) {
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
      // Fallback signal: wp-login page — must contain WordPress login form markers
      const loginResp = await fetcher.get(`${url}/wp-login.php`);
      if (loginResp.status === 200 && this.isWordPressLoginPage(loginResp.body)) {
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

  private isWordPressApiResponse(body: string): boolean {
    // WP REST API returns JSON with namespace markers — not just any 200 response
    return body.includes('wp/v2') || body.includes('"namespaces"') || body.includes('wp-json');
  }

  private isWordPressLoginPage(body: string): boolean {
    // WordPress login page has specific form IDs/classes
    return body.includes('wp-login') || body.includes('wp-submit');
  }
}
