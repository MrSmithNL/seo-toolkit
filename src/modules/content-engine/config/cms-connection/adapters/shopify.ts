// Shopify CMS adapter (TASK-010)
// F-002 US-002: Shopify connection via GraphQL Admin API

import { type Result, ok, err, operationError, type OperationError } from '../../../../../lib/result.js';
import type { CmsAdapter, CmsCredentials, CmsHttpClient, VerifyResult, PublishResult, ContentPayload } from './types.js';

const REQUIRED_SCOPES = ['read_content', 'write_content'];

function graphqlUrl(creds: CmsCredentials): string {
  return `https://${creds['storeDomain'] as string}/admin/api/2024-01/graphql.json`;
}

function headers(creds: CmsCredentials): Record<string, string> {
  return {
    'X-Shopify-Access-Token': creds['accessToken'] as string,
    'Content-Type': 'application/json',
  };
}

export class ShopifyAdapter implements CmsAdapter {
  readonly cmsType = 'shopify';

  constructor(private readonly http: CmsHttpClient) {}

  async verify(credentials: CmsCredentials): Promise<Result<VerifyResult, OperationError>> {
    try {
      const resp = await this.http.post(
        graphqlUrl(credentials),
        {
          query: `{ shop { name } app { installation { accessScopes { handle } } } }`,
        },
        headers(credentials),
      );

      if (resp.status === 401) {
        return err(operationError({
          type: 'https://api.smithai.com/errors/auth',
          title: 'Shopify Authentication Failed',
          status: 401,
          detail: 'Invalid access token',
          suggestedAction: 'Check the Shopify access token is correct',
        }));
      }

      if (resp.status !== 200) {
        return err(operationError({
          type: 'https://api.smithai.com/errors/connection',
          title: 'Shopify API Error',
          status: resp.status,
          detail: 'Unexpected response from Shopify API',
        }));
      }

      const data = JSON.parse(resp.body) as {
        data: {
          shop: { name: string };
          app: { installation: { accessScopes: Array<{ handle: string }> } };
        };
      };

      const scopes = data.data.app.installation.accessScopes.map(s => s.handle);
      const missing = REQUIRED_SCOPES.filter(s => !scopes.includes(s));

      if (missing.length > 0) {
        return err(operationError({
          type: 'https://api.smithai.com/errors/permissions',
          title: 'Missing Shopify Scopes',
          status: 403,
          detail: `Missing required scopes: ${missing.join(', ')}`,
          suggestedAction: 'Update the Shopify app permissions to include read_content and write_content',
        }));
      }

      return ok({ valid: true, permissions: scopes });
    } catch (e) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/connection',
        title: 'Shopify Connection Failed',
        status: 502,
        detail: (e as Error).message,
      }));
    }
  }

  async testPublish(credentials: CmsCredentials): Promise<Result<boolean, OperationError>> {
    try {
      // Create test article
      const createResp = await this.http.post(
        graphqlUrl(credentials),
        {
          query: `mutation { articleCreate(article: { title: "SEO Toolkit Test", body: "Test", blogId: "gid://shopify/Blog/1" }) { article { id } userErrors { message } } }`,
        },
        headers(credentials),
      );

      if (createResp.status !== 200) {
        return err(operationError({
          type: 'https://api.smithai.com/errors/cms',
          title: 'Shopify Test Publish Failed',
          status: createResp.status,
          detail: 'Could not create test article',
        }));
      }

      const createData = JSON.parse(createResp.body) as {
        data: { articleCreate: { article: { id: string }; userErrors: Array<{ message: string }> } };
      };

      const articleId = createData.data.articleCreate.article.id;

      // Delete test article
      await this.http.post(
        graphqlUrl(credentials),
        {
          query: `mutation { articleDelete(id: "${articleId}") { deletedArticleId userErrors { message } } }`,
        },
        headers(credentials),
      );

      return ok(true);
    } catch (e) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/connection',
        title: 'Shopify Test Publish Failed',
        status: 502,
        detail: (e as Error).message,
      }));
    }
  }

  async publish(credentials: CmsCredentials, content: ContentPayload): Promise<Result<PublishResult, OperationError>> {
    try {
      const resp = await this.http.post(
        graphqlUrl(credentials),
        {
          query: `mutation { articleCreate(article: { title: "${content.title}", body: "${content.body}", blogId: "gid://shopify/Blog/1" }) { article { id handle } userErrors { message } } }`,
        },
        headers(credentials),
      );

      if (resp.status !== 200) {
        return err(operationError({
          type: 'https://api.smithai.com/errors/cms',
          title: 'Shopify Publish Failed',
          status: resp.status,
          detail: 'Could not create article',
        }));
      }

      const data = JSON.parse(resp.body) as {
        data: { articleCreate: { article: { id: string; handle: string }; userErrors: Array<{ message: string }> } };
      };

      const article = data.data.articleCreate.article;
      const storeDomain = credentials['storeDomain'] as string;
      return ok({
        id: article.id,
        url: `https://${storeDomain}/blogs/news/${article.handle}`,
      });
    } catch (e) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/connection',
        title: 'Shopify Publish Failed',
        status: 502,
        detail: (e as Error).message,
      }));
    }
  }

  async unpublish(credentials: CmsCredentials, contentId: string): Promise<Result<boolean, OperationError>> {
    try {
      const resp = await this.http.post(
        graphqlUrl(credentials),
        {
          query: `mutation { articleDelete(id: "${contentId}") { deletedArticleId userErrors { message } } }`,
        },
        headers(credentials),
      );

      if (resp.status === 200) {
        return ok(true);
      }

      return err(operationError({
        type: 'https://api.smithai.com/errors/cms',
        title: 'Shopify Unpublish Failed',
        status: resp.status,
        detail: `Could not delete article ${contentId}`,
      }));
    } catch (e) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/connection',
        title: 'Shopify Unpublish Failed',
        status: 502,
        detail: (e as Error).message,
      }));
    }
  }
}
