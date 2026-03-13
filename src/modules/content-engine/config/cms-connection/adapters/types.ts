// CMS adapter interface — pluggable content management adapters (TASK-009)
// F-002: CMS Connection Management

import type { Result, OperationError } from '../../../../../lib/result.js';

export interface CmsCredentials {
  readonly cmsType: string;
  readonly [key: string]: unknown;
}

export interface VerifyResult {
  readonly valid: boolean;
  readonly username?: string;
  readonly permissions?: string[];
}

export interface PublishResult {
  readonly id: string;
  readonly url: string;
}

export interface ContentPayload {
  readonly title: string;
  readonly body: string;
  readonly status?: 'draft' | 'publish';
}

export interface CmsAdapter {
  readonly cmsType: string;

  /** Verify credentials are valid and have required permissions */
  verify(credentials: CmsCredentials): Promise<Result<VerifyResult, OperationError>>;

  /** Create a test post (draft), verify it works, then delete it */
  testPublish(credentials: CmsCredentials): Promise<Result<boolean, OperationError>>;

  /** Publish content to the CMS */
  publish(credentials: CmsCredentials, content: ContentPayload): Promise<Result<PublishResult, OperationError>>;

  /** Unpublish (delete/draft) content by ID */
  unpublish(credentials: CmsCredentials, contentId: string): Promise<Result<boolean, OperationError>>;
}

/** HTTP client abstraction for testability */
export interface CmsHttpClient {
  get(url: string, headers?: Record<string, string>): Promise<CmsHttpResponse>;
  post(url: string, body: unknown, headers?: Record<string, string>): Promise<CmsHttpResponse>;
  delete(url: string, headers?: Record<string, string>): Promise<CmsHttpResponse>;
}

export interface CmsHttpResponse {
  readonly status: number;
  readonly body: string;
}
