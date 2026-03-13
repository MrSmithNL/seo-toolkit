// CMS detector interface — pluggable detector pattern (TASK-006)

export type CmsType = 'wordpress' | 'shopify' | 'unknown';

export interface DetectionResult {
  readonly cmsType: CmsType;
  readonly confidence: number; // 0-1
  readonly evidence: string;
}

export interface CmsDetector {
  readonly name: CmsType;
  detect(url: string, fetcher: HttpFetcher): Promise<DetectionResult | null>;
}

/** Abstraction over fetch for testability */
export interface HttpFetcher {
  get(url: string): Promise<HttpResponse>;
}

export interface HttpResponse {
  readonly status: number;
  readonly body: string;
}
