// SiteService — site registration + crawl pipeline (TASK-001 + TASK-011)
// P-008: Zod input → OperationContext → business logic → persist → return Result

import { z } from 'zod';
import { generateId } from '../../../../lib/id.js';
import { type Result, type OperationError, ok, err, operationError } from '../../../../lib/result.js';
import type { OperationContext } from '../../../../lib/context.js';
import type { SiteRecord, SiteRepository } from './site.repository.js';
import { normaliseUrl } from './url.js';
import { detectCms } from './detectors/detect.js';
import { detectLanguages, type DetectedLanguage } from './detectors/language.js';
import { parseSitemap } from './sitemap.js';
import type { HttpFetcher } from './detectors/types.js';

const RegisterSiteInput = z.object({
  url: z.string().url(),
  name: z.string().min(1),
});

const RegisterAndCrawlInput = z.object({
  url: z.string().min(1),
  name: z.string().min(1),
});

export interface CrawlResult {
  readonly site: SiteRecord;
  readonly languages: DetectedLanguage[];
}

export class SiteService {
  constructor(
    private readonly repository: SiteRepository,
    private readonly fetcher?: HttpFetcher,
  ) {}

  /** Walking skeleton — register with pre-validated URL */
  async registerSite(
    input: { url: string; name: string },
    ctx: OperationContext,
  ): Promise<Result<SiteRecord, OperationError>> {
    const parsed = RegisterSiteInput.safeParse(input);
    if (!parsed.success) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/validation',
        title: 'Validation Error',
        status: 400,
        detail: parsed.error.issues.map(i => `${String(i.path[0])}: ${i.message}`).join('; '),
        suggestedAction: 'Check URL format and name',
      }));
    }

    const existing = await this.repository.findByUrl(parsed.data.url, ctx.tenantId);
    if (existing) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/conflict',
        title: 'Duplicate Site',
        status: 409,
        detail: `Site with URL ${parsed.data.url} already exists for this tenant`,
        suggestedAction: 'Use the existing site or choose a different URL',
      }));
    }

    const site = await this.repository.create({
      id: generateId('site'),
      tenantId: ctx.tenantId,
      url: parsed.data.url,
      name: parsed.data.name,
    });

    return ok(site);
  }

  /** Full pipeline — normalise URL → store → detect CMS → detect languages → count content */
  async registerAndCrawl(
    input: { url: string; name: string },
    ctx: OperationContext,
  ): Promise<Result<CrawlResult, OperationError>> {
    const parsed = RegisterAndCrawlInput.safeParse(input);
    if (!parsed.success) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/validation',
        title: 'Validation Error',
        status: 400,
        detail: parsed.error.issues.map(i => `${String(i.path[0])}: ${i.message}`).join('; '),
        suggestedAction: 'Check URL format and name',
      }));
    }

    // Normalise URL
    const normalised = normaliseUrl(parsed.data.url);
    if (!normalised.success) {
      return err(normalised.error);
    }
    const url = normalised.data;

    // Check duplicate
    const existing = await this.repository.findByUrl(url, ctx.tenantId);
    if (existing) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/conflict',
        title: 'Duplicate Site',
        status: 409,
        detail: `Site with URL ${url} already exists for this tenant`,
        suggestedAction: 'Use the existing site or choose a different URL',
      }));
    }

    // Create initial record
    const site = await this.repository.create({
      id: generateId('site'),
      tenantId: ctx.tenantId,
      url,
      name: parsed.data.name,
    });

    if (!this.fetcher) {
      return ok({ site, languages: [] });
    }

    // Crawl pipeline (parallel)
    const [cmsResult, languages, sitemapResult] = await Promise.all([
      detectCms(url, this.fetcher),
      detectLanguages(url, this.fetcher),
      parseSitemap(url, this.fetcher),
    ]);

    // Update site with crawl results
    const updatedSite = await this.repository.update(site.id, ctx.tenantId, {
      cmsType: cmsResult.cmsType,
      cmsDetectedAt: new Date().toISOString(),
      primaryLanguage: languages[0]?.code ?? 'en',
      contentCount: sitemapResult.contentCount,
      lastCrawled: new Date().toISOString(),
    });

    // Persist detected languages
    for (const lang of languages) {
      await this.repository.addLanguage({
        id: generateId('siteLanguage'),
        siteId: site.id,
        code: lang.code,
        name: lang.name,
        urlPattern: lang.urlPattern,
      });
    }

    // Event emission deferred to TASK-017
    return ok({ site: updatedSite, languages });
  }

  async getSite(
    id: string,
    ctx: OperationContext,
  ): Promise<Result<SiteRecord, OperationError>> {
    const site = await this.repository.findById(id, ctx.tenantId);

    if (!site) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/not-found',
        title: 'Site Not Found',
        status: 404,
        detail: `Site ${id} not found`,
        suggestedAction: 'Check the site ID is correct',
      }));
    }

    return ok(site);
  }
}
