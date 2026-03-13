// TASK-009: WordPress CMS adapter
// TDD: Tests first with mocked HTTP.

import { describe, it, expect } from 'vitest';
import { WordPressAdapter } from '../adapters/wordpress.js';
import type { CmsHttpClient, CmsHttpResponse, CmsCredentials } from '../adapters/types.js';

function mockHttpClient(responses: Record<string, { method?: string; response: CmsHttpResponse }>): CmsHttpClient {
  function find(url: string, method: string): CmsHttpResponse {
    // Try method-specific key first, then URL-only
    const key = `${method}:${url}`;
    if (responses[key]) return responses[key]!.response;
    if (responses[url]) return responses[url]!.response;
    return { status: 404, body: '' };
  }

  return {
    async get(url: string): Promise<CmsHttpResponse> { return find(url, 'GET'); },
    async post(url: string): Promise<CmsHttpResponse> { return find(url, 'POST'); },
    async delete(url: string): Promise<CmsHttpResponse> { return find(url, 'DELETE'); },
  };
}

const validCreds: CmsCredentials = {
  cmsType: 'wordpress',
  siteUrl: 'https://example.com',
  username: 'admin',
  applicationPassword: 'xxxx xxxx xxxx xxxx',
};

describe('WordPressAdapter', () => {
  describe('verify', () => {
    it('returns valid when /wp-json/wp/v2/users/me succeeds', async () => {
      const client = mockHttpClient({
        'https://example.com/wp-json/wp/v2/users/me': {
          response: {
            status: 200,
            body: JSON.stringify({ id: 1, name: 'admin', slug: 'admin' }),
          },
        },
      });

      const adapter = new WordPressAdapter(client);
      const result = await adapter.verify(validCreds);

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.valid).toBe(true);
        expect(result.data.username).toBe('admin');
      }
    });

    it('returns invalid when auth fails (401)', async () => {
      const client = mockHttpClient({
        'https://example.com/wp-json/wp/v2/users/me': {
          response: { status: 401, body: '{"code":"rest_not_logged_in"}' },
        },
      });

      const adapter = new WordPressAdapter(client);
      const result = await adapter.verify(validCreds);

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.status).toBe(401);
      }
    });

    it('returns error on network failure', async () => {
      const client: CmsHttpClient = {
        async get(): Promise<CmsHttpResponse> { throw new Error('Connection refused'); },
        async post(): Promise<CmsHttpResponse> { throw new Error('Connection refused'); },
        async delete(): Promise<CmsHttpResponse> { throw new Error('Connection refused'); },
      };

      const adapter = new WordPressAdapter(client);
      const result = await adapter.verify(validCreds);

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.status).toBe(502);
      }
    });
  });

  describe('testPublish', () => {
    it('creates a draft post then deletes it', async () => {
      const client = mockHttpClient({
        'POST:https://example.com/wp-json/wp/v2/posts': {
          response: {
            status: 201,
            body: JSON.stringify({ id: 999, title: { rendered: 'Test' }, status: 'draft' }),
          },
        },
        'DELETE:https://example.com/wp-json/wp/v2/posts/999?force=true': {
          response: { status: 200, body: '{"deleted":true}' },
        },
      });

      const adapter = new WordPressAdapter(client);
      const result = await adapter.testPublish(validCreds);

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe(true);
      }
    });

    it('returns error when post creation fails', async () => {
      const client = mockHttpClient({
        'POST:https://example.com/wp-json/wp/v2/posts': {
          response: { status: 403, body: '{"code":"rest_cannot_create"}' },
        },
      });

      const adapter = new WordPressAdapter(client);
      const result = await adapter.testPublish(validCreds);

      expect(result.success).toBe(false);
    });
  });

  describe('publish', () => {
    it('creates a post with given content', async () => {
      const client = mockHttpClient({
        'POST:https://example.com/wp-json/wp/v2/posts': {
          response: {
            status: 201,
            body: JSON.stringify({
              id: 42,
              link: 'https://example.com/hello-world',
              title: { rendered: 'Hello World' },
            }),
          },
        },
      });

      const adapter = new WordPressAdapter(client);
      const result = await adapter.publish(validCreds, {
        title: 'Hello World',
        body: '<p>Content here</p>',
        status: 'draft',
      });

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.id).toBe('42');
        expect(result.data.url).toBe('https://example.com/hello-world');
      }
    });
  });

  describe('unpublish', () => {
    it('deletes a post by ID', async () => {
      const client = mockHttpClient({
        'DELETE:https://example.com/wp-json/wp/v2/posts/42?force=true': {
          response: { status: 200, body: '{"deleted":true}' },
        },
      });

      const adapter = new WordPressAdapter(client);
      const result = await adapter.unpublish(validCreds, '42');

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toBe(true);
      }
    });

    it('returns error when delete fails', async () => {
      const client = mockHttpClient({
        'DELETE:https://example.com/wp-json/wp/v2/posts/42?force=true': {
          response: { status: 404, body: '{"code":"rest_post_invalid_id"}' },
        },
      });

      const adapter = new WordPressAdapter(client);
      const result = await adapter.unpublish(validCreds, '42');

      expect(result.success).toBe(false);
    });
  });
});
