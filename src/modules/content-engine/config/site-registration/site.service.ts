// SiteService — walking skeleton business logic
// P-008: Zod input → OperationContext → business logic → persist → return Result

import { z } from 'zod';
import { generateId } from '../../../../lib/id.js';
import { type Result, type OperationError, ok, err, operationError } from '../../../../lib/result.js';
import type { OperationContext } from '../../../../lib/context.js';
import type { SiteRecord, SiteRepository } from './site.repository.js';

const RegisterSiteInput = z.object({
  url: z.string().url(),
  name: z.string().min(1),
});

type RegisterSiteInput = z.infer<typeof RegisterSiteInput>;

export class SiteService {
  constructor(private readonly repository: SiteRepository) {}

  async registerSite(
    input: { url: string; name: string },
    ctx: OperationContext,
  ): Promise<Result<SiteRecord, OperationError>> {
    // Step 1: Validate
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

    // Step 2: Check for duplicate (same URL + tenant)
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

    // Step 3: Persist
    const site = await this.repository.create({
      id: generateId('site'),
      tenantId: ctx.tenantId,
      url: parsed.data.url,
      name: parsed.data.name,
    });

    // Step 4: Return Result (event emission deferred to TASK-007)
    return ok(site);
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
