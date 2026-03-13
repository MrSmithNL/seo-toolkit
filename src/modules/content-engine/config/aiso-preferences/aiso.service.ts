// AISO preferences service (TASK-016)
// F-006: Configurable AISO scoring with 36-factor model

import { generateId } from '../../../../lib/id.js';
import { type Result, ok, err, operationError, type OperationError } from '../../../../lib/result.js';
import type { OperationContext } from '../../../../lib/context.js';
import type { AisoRepository, AisoPreferencesRecord } from './aiso.repository.js';
import { FactorRegistry } from './factor-registry.js';

const VALID_SCHEMA_TYPES = ['Article', 'FAQPage', 'HowTo', 'Product', 'Review', 'BreadcrumbList', 'Organization', 'WebPage', 'VideoObject'] as const;
const VALID_PLATFORMS = ['chatgpt', 'gemini', 'perplexity', 'claude', 'copilot'] as const;

const DEFAULT_SCHEMA_TYPES = ['Article', 'FAQPage', 'BreadcrumbList'];
const DEFAULT_PLATFORMS = ['chatgpt', 'perplexity', 'gemini'];

export interface UpdateAisoInput {
  useRecommended?: boolean;
  priorityFactors?: string[];
  schemaTypes?: string[];
  aiPlatformTargets?: string[];
}

export class AisoService {
  private readonly registry: FactorRegistry;

  constructor(
    private readonly repository: AisoRepository,
    registry?: FactorRegistry,
  ) {
    this.registry = registry ?? new FactorRegistry();
  }

  async createDefaults(
    siteId: string,
    _ctx: OperationContext,
  ): Promise<Result<AisoPreferencesRecord, OperationError>> {
    const existing = await this.repository.findBySiteId(siteId);
    if (existing) return ok(existing);

    const record = await this.repository.create({
      id: generateId('aisoPreferences'),
      siteId,
      useRecommended: true,
      schemaTypes: JSON.stringify(DEFAULT_SCHEMA_TYPES),
      aiPlatformTargets: JSON.stringify(DEFAULT_PLATFORMS),
    });
    return ok(record);
  }

  async getPreferences(
    siteId: string,
    _ctx: OperationContext,
  ): Promise<Result<AisoPreferencesRecord, OperationError>> {
    const record = await this.repository.findBySiteId(siteId);
    if (!record) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/not-found',
        title: 'AISO Preferences Not Found',
        status: 404,
        detail: `No AISO preferences found for site ${siteId}`,
      }));
    }
    return ok(record);
  }

  async updatePreferences(
    siteId: string,
    input: UpdateAisoInput,
    _ctx: OperationContext,
  ): Promise<Result<AisoPreferencesRecord, OperationError>> {
    const existing = await this.repository.findBySiteId(siteId);
    if (!existing) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/not-found',
        title: 'AISO Preferences Not Found',
        status: 404,
        detail: `No AISO preferences found for site ${siteId}`,
      }));
    }

    // Validate priority factors
    if (input.priorityFactors) {
      const validation = this.registry.validate(input.priorityFactors);
      if (!validation.valid) {
        return err(operationError({
          type: 'https://api.smithai.com/errors/validation',
          title: 'Invalid AISO Factors',
          status: 400,
          detail: `Unknown factors: ${validation.unknown.join(', ')}`,
        }));
      }
    }

    // Validate schema types
    if (input.schemaTypes) {
      const invalid = input.schemaTypes.filter(s => !(VALID_SCHEMA_TYPES as readonly string[]).includes(s));
      if (invalid.length > 0) {
        return err(operationError({
          type: 'https://api.smithai.com/errors/validation',
          title: 'Invalid Schema Types',
          status: 400,
          detail: `Unknown schema types: ${invalid.join(', ')}`,
        }));
      }
    }

    // Validate platforms
    if (input.aiPlatformTargets) {
      const invalid = input.aiPlatformTargets.filter(p => !(VALID_PLATFORMS as readonly string[]).includes(p));
      if (invalid.length > 0) {
        return err(operationError({
          type: 'https://api.smithai.com/errors/validation',
          title: 'Invalid AI Platforms',
          status: 400,
          detail: `Unknown platforms: ${invalid.join(', ')}`,
        }));
      }
    }

    const updateFields: Record<string, unknown> = {};
    if (input.useRecommended !== undefined) updateFields['useRecommended'] = input.useRecommended;
    if (input.priorityFactors) updateFields['priorityFactors'] = JSON.stringify(input.priorityFactors);
    if (input.schemaTypes) updateFields['schemaTypes'] = JSON.stringify(input.schemaTypes);
    if (input.aiPlatformTargets) updateFields['aiPlatformTargets'] = JSON.stringify(input.aiPlatformTargets);

    const record = await this.repository.update(siteId, updateFields);
    return ok(record);
  }

  async resetToRecommended(
    siteId: string,
    _ctx: OperationContext,
  ): Promise<Result<AisoPreferencesRecord, OperationError>> {
    const existing = await this.repository.findBySiteId(siteId);
    if (!existing) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/not-found',
        title: 'AISO Preferences Not Found',
        status: 404,
        detail: `No AISO preferences found for site ${siteId}`,
      }));
    }

    const record = await this.repository.update(siteId, {
      useRecommended: true,
      priorityFactors: null,
      schemaTypes: JSON.stringify(DEFAULT_SCHEMA_TYPES),
      aiPlatformTargets: JSON.stringify(DEFAULT_PLATFORMS),
    });
    return ok(record);
  }

  getFactorRegistry(): FactorRegistry {
    return this.registry;
  }
}
