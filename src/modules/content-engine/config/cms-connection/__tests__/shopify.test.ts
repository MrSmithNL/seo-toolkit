// TASK-010: Shopify CMS adapter
// TDD: Tests first with mocked HTTP (GraphQL Admin API).

import { describe, it, expect } from 'vitest';
import { ShopifyAdapter } from '../adapters/shopify.js';
import type { CmsHttpClient, CmsHttpResponse, CmsCredentials } from '../adapters/types.js';

function mockHttpClient(handler: (url: string, method: string, body?: unknown) => CmsHttpResponse): CmsHttpClient {
  return {
    async get(url: string): Promise<CmsHttpResponse> { return handler(url, 'GET'); },
    async post(url: string, body: unknown): Promise<CmsHttpResponse> { return handler(url, 'POST', body); },
    async delete(url: string): Promise<CmsHttpResponse> { return handler(url, 'DELETE'); },
  };
}

const validCreds: CmsCredentials = {
  cmsType: 'shopify',
  storeDomain: 'test-store.myshopify.com',
  accessToken: 'shpat_test_token_123',
};

const shopUrl = 'https://test-store.myshopify.com/admin/api/2024-01/graphql.json';

describe('ShopifyAdapter', () => {
  describe('verify', () => {
    it('returns valid when shop query succeeds with required scopes', () => {
      const client = mockHttpClient((url, method, body) => {
        if (url === shopUrl && method === 'POST') {
          const query = JSON.stringify(body);
          if (query.includes('shop')) {
            return {
              status: 200,
              body: JSON.stringify({
                data: {
                  shop: { name: 'Test Store' },
                  app: { installation: { accessScopes: [
                    { handle: 'read_content' },
                    { handle: 'write_content' },
                  ] } },
                },
              }),
            };
          }
        }
        return { status: 404, body: '' };
      });

      const adapter = new ShopifyAdapter(client);
      return adapter.verify(validCreds).then(result => {
        expect(result.success).toBe(true);
        if (result.success) {
          expect(result.data.valid).toBe(true);
          expect(result.data.permissions).toContain('read_content');
          expect(result.data.permissions).toContain('write_content');
        }
      });
    });

    it('returns error when access token is invalid (401)', () => {
      const client = mockHttpClient(() => ({
        status: 401,
        body: '{"errors":"[API] Invalid API key or access token"}',
      }));

      const adapter = new ShopifyAdapter(client);
      return adapter.verify(validCreds).then(result => {
        expect(result.success).toBe(false);
        if (!result.success) {
          expect(result.error.status).toBe(401);
        }
      });
    });

    it('returns error when missing required scopes', () => {
      const client = mockHttpClient((url, method) => {
        if (method === 'POST') {
          return {
            status: 200,
            body: JSON.stringify({
              data: {
                shop: { name: 'Test Store' },
                app: { installation: { accessScopes: [
                  { handle: 'read_products' },
                ] } },
              },
            }),
          };
        }
        return { status: 404, body: '' };
      });

      const adapter = new ShopifyAdapter(client);
      return adapter.verify(validCreds).then(result => {
        expect(result.success).toBe(false);
        if (!result.success) {
          expect(result.error.detail).toContain('read_content');
        }
      });
    });
  });

  describe('testPublish', () => {
    it('creates a test article then deletes it', () => {
      let createdId: string | null = null;
      const client = mockHttpClient((_url, method, body) => {
        if (method === 'POST') {
          const query = JSON.stringify(body);
          if (query.includes('articleCreate')) {
            createdId = 'gid://shopify/Article/123';
            return {
              status: 200,
              body: JSON.stringify({
                data: { articleCreate: { article: { id: createdId }, userErrors: [] } },
              }),
            };
          }
          if (query.includes('articleDelete') && createdId) {
            return {
              status: 200,
              body: JSON.stringify({
                data: { articleDelete: { deletedArticleId: createdId, userErrors: [] } },
              }),
            };
          }
        }
        return { status: 404, body: '' };
      });

      const adapter = new ShopifyAdapter(client);
      return adapter.testPublish(validCreds).then(result => {
        expect(result.success).toBe(true);
        if (result.success) {
          expect(result.data).toBe(true);
        }
      });
    });
  });

  describe('publish', () => {
    it('creates an article with given content', () => {
      const client = mockHttpClient((_url, method, body) => {
        if (method === 'POST') {
          const query = JSON.stringify(body);
          if (query.includes('articleCreate')) {
            return {
              status: 200,
              body: JSON.stringify({
                data: {
                  articleCreate: {
                    article: {
                      id: 'gid://shopify/Article/42',
                      handle: 'hello-world',
                    },
                    userErrors: [],
                  },
                },
              }),
            };
          }
        }
        return { status: 404, body: '' };
      });

      const adapter = new ShopifyAdapter(client);
      return adapter.publish(validCreds, {
        title: 'Hello World',
        body: '<p>Content</p>',
        status: 'draft',
      }).then(result => {
        expect(result.success).toBe(true);
        if (result.success) {
          expect(result.data.id).toBe('gid://shopify/Article/42');
        }
      });
    });
  });

  describe('unpublish', () => {
    it('deletes an article by ID', () => {
      const client = mockHttpClient((_url, method, body) => {
        if (method === 'POST') {
          const query = JSON.stringify(body);
          if (query.includes('articleDelete')) {
            return {
              status: 200,
              body: JSON.stringify({
                data: { articleDelete: { deletedArticleId: 'gid://shopify/Article/42', userErrors: [] } },
              }),
            };
          }
        }
        return { status: 404, body: '' };
      });

      const adapter = new ShopifyAdapter(client);
      return adapter.unpublish(validCreds, 'gid://shopify/Article/42').then(result => {
        expect(result.success).toBe(true);
      });
    });
  });
});
