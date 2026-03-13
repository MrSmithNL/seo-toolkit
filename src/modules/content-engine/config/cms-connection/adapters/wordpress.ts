// WordPress CMS adapter (TASK-009)
// F-002 US-001: WordPress connection via REST API + Application Passwords

import { type Result, ok, err, operationError, type OperationError } from '../../../../../lib/result.js';
import type { CmsAdapter, CmsCredentials, CmsHttpClient, VerifyResult, PublishResult, ContentPayload } from './types.js';

function wpHeaders(creds: CmsCredentials): Record<string, string> {
  const username = creds['username'] as string;
  const password = creds['applicationPassword'] as string;
  const encoded = Buffer.from(`${username}:${password}`).toString('base64');
  return {
    Authorization: `Basic ${encoded}`,
    'Content-Type': 'application/json',
  };
}

function apiBase(creds: CmsCredentials): string {
  return `${creds['siteUrl'] as string}/wp-json/wp/v2`;
}

export class WordPressAdapter implements CmsAdapter {
  readonly cmsType = 'wordpress';

  constructor(private readonly http: CmsHttpClient) {}

  async verify(credentials: CmsCredentials): Promise<Result<VerifyResult, OperationError>> {
    try {
      const resp = await this.http.get(
        `${apiBase(credentials)}/users/me`,
        wpHeaders(credentials),
      );

      if (resp.status === 200) {
        const data = JSON.parse(resp.body) as { name?: string };
        return ok({ valid: true, username: data.name });
      }

      return err(operationError({
        type: 'https://api.smithai.com/errors/auth',
        title: 'WordPress Authentication Failed',
        status: resp.status,
        detail: 'Could not authenticate with the provided credentials',
        suggestedAction: 'Check the username and application password are correct',
      }));
    } catch (e) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/connection',
        title: 'WordPress Connection Failed',
        status: 502,
        detail: `Could not connect to WordPress: ${(e as Error).message}`,
        suggestedAction: 'Check the site URL is correct and the site is reachable',
      }));
    }
  }

  async testPublish(credentials: CmsCredentials): Promise<Result<boolean, OperationError>> {
    try {
      const createResp = await this.http.post(
        `${apiBase(credentials)}/posts`,
        { title: 'SEO Toolkit Connection Test', status: 'draft', content: 'This is a test post.' },
        wpHeaders(credentials),
      );

      if (createResp.status !== 201) {
        return err(operationError({
          type: 'https://api.smithai.com/errors/cms',
          title: 'Test Publish Failed',
          status: createResp.status,
          detail: 'Could not create a test draft post',
          suggestedAction: 'Check the user has publish_posts capability',
        }));
      }

      const created = JSON.parse(createResp.body) as { id: number };

      // Clean up test post
      await this.http.delete(
        `${apiBase(credentials)}/posts/${created.id}?force=true`,
        wpHeaders(credentials),
      );

      return ok(true);
    } catch (e) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/connection',
        title: 'Test Publish Connection Failed',
        status: 502,
        detail: (e as Error).message,
      }));
    }
  }

  async publish(credentials: CmsCredentials, content: ContentPayload): Promise<Result<PublishResult, OperationError>> {
    try {
      const resp = await this.http.post(
        `${apiBase(credentials)}/posts`,
        { title: content.title, content: content.body, status: content.status ?? 'draft' },
        wpHeaders(credentials),
      );

      if (resp.status === 201) {
        const data = JSON.parse(resp.body) as { id: number; link: string };
        return ok({ id: String(data.id), url: data.link });
      }

      return err(operationError({
        type: 'https://api.smithai.com/errors/cms',
        title: 'Publish Failed',
        status: resp.status,
        detail: 'Could not create the post',
      }));
    } catch (e) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/connection',
        title: 'Publish Connection Failed',
        status: 502,
        detail: (e as Error).message,
      }));
    }
  }

  async unpublish(credentials: CmsCredentials, contentId: string): Promise<Result<boolean, OperationError>> {
    try {
      const resp = await this.http.delete(
        `${apiBase(credentials)}/posts/${contentId}?force=true`,
        wpHeaders(credentials),
      );

      if (resp.status === 200) {
        return ok(true);
      }

      return err(operationError({
        type: 'https://api.smithai.com/errors/cms',
        title: 'Unpublish Failed',
        status: resp.status,
        detail: `Could not delete post ${contentId}`,
      }));
    } catch (e) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/connection',
        title: 'Unpublish Connection Failed',
        status: 502,
        detail: (e as Error).message,
      }));
    }
  }
}
