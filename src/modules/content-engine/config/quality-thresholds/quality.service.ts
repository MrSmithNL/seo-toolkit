// Quality thresholds service (TASK-015)
// F-005: Configurable quality gates with sensible defaults

import { generateId } from '../../../../lib/id.js';
import { type Result, ok, err, operationError, type OperationError } from '../../../../lib/result.js';
import type { OperationContext } from '../../../../lib/context.js';
import type { QualityRepository, QualityThresholdsRecord } from './quality.repository.js';

type ReadabilityGrade = 'grade_6' | 'grade_8' | 'grade_10' | 'grade_12' | 'college';
type PublishMode = 'draft_review' | 'auto_publish' | 'manual_only';

const VALID_GRADES: ReadabilityGrade[] = ['grade_6', 'grade_8', 'grade_10', 'grade_12', 'college'];
const VALID_MODES: PublishMode[] = ['draft_review', 'auto_publish', 'manual_only'];

export interface ThresholdDefaults {
  readonly seoScoreMin: number;
  readonly aisoScoreMin: number;
  readonly readabilityTarget: ReadabilityGrade;
  readonly wordCountMin: number;
  readonly wordCountMax: number;
  readonly publishMode: PublishMode;
}

export interface UpdateThresholdsInput {
  seoScoreMin?: number;
  aisoScoreMin?: number;
  readabilityTarget?: string;
  wordCountMin?: number;
  wordCountMax?: number;
  publishMode?: string;
}

export function getDefaults(cmsType?: string): ThresholdDefaults {
  const base: ThresholdDefaults = {
    seoScoreMin: 65,
    aisoScoreMin: 7.0,
    readabilityTarget: 'grade_8',
    wordCountMin: 1500,
    wordCountMax: 3000,
    publishMode: 'draft_review',
  };

  if (cmsType === 'shopify') {
    return { ...base, wordCountMin: 800, wordCountMax: 2000, readabilityTarget: 'grade_6' };
  }

  return base;
}

export class QualityService {
  constructor(private readonly repository: QualityRepository) {}

  async createDefaults(
    siteId: string,
    cmsType: string | undefined,
    _ctx: OperationContext,
  ): Promise<Result<QualityThresholdsRecord, OperationError>> {
    const existing = await this.repository.findBySiteId(siteId);
    if (existing) {
      return ok(existing);
    }

    const defaults = getDefaults(cmsType);
    const record = await this.repository.create({
      id: generateId('qualityThresholds'),
      siteId,
      ...defaults,
    });
    return ok(record);
  }

  async getThresholds(
    siteId: string,
    _ctx: OperationContext,
  ): Promise<Result<QualityThresholdsRecord, OperationError>> {
    const record = await this.repository.findBySiteId(siteId);
    if (!record) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/not-found',
        title: 'Quality Thresholds Not Found',
        status: 404,
        detail: `No quality thresholds found for site ${siteId}`,
      }));
    }
    return ok(record);
  }

  async updateThresholds(
    siteId: string,
    input: UpdateThresholdsInput,
    _ctx: OperationContext,
  ): Promise<Result<QualityThresholdsRecord, OperationError>> {
    const validation = this.validate(input);
    if (!validation.success) return validation;

    const existing = await this.repository.findBySiteId(siteId);
    if (!existing) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/not-found',
        title: 'Quality Thresholds Not Found',
        status: 404,
        detail: `No quality thresholds found for site ${siteId}`,
      }));
    }

    const record = await this.repository.update(siteId, input);
    return ok(record);
  }

  async resetToDefaults(
    siteId: string,
    cmsType: string | undefined,
    _ctx: OperationContext,
  ): Promise<Result<QualityThresholdsRecord, OperationError>> {
    const existing = await this.repository.findBySiteId(siteId);
    if (!existing) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/not-found',
        title: 'Quality Thresholds Not Found',
        status: 404,
        detail: `No quality thresholds found for site ${siteId}`,
      }));
    }

    const defaults = getDefaults(cmsType);
    const record = await this.repository.update(siteId, defaults);
    return ok(record);
  }

  private validate(input: UpdateThresholdsInput): Result<void, OperationError> {
    const errors: string[] = [];

    if (input.seoScoreMin !== undefined && (input.seoScoreMin < 0 || input.seoScoreMin > 100)) {
      errors.push('seoScoreMin must be 0-100');
    }
    if (input.aisoScoreMin !== undefined && (input.aisoScoreMin < 0 || input.aisoScoreMin > 10)) {
      errors.push('aisoScoreMin must be 0.0-10.0');
    }
    if (input.readabilityTarget !== undefined && !VALID_GRADES.includes(input.readabilityTarget as ReadabilityGrade)) {
      errors.push(`readabilityTarget must be one of: ${VALID_GRADES.join(', ')}`);
    }
    if (input.wordCountMin !== undefined && input.wordCountMin < 300) {
      errors.push('wordCountMin must be >= 300');
    }
    if (input.wordCountMax !== undefined && input.wordCountMax > 10000) {
      errors.push('wordCountMax must be <= 10000');
    }
    if (input.wordCountMin !== undefined && input.wordCountMax !== undefined && input.wordCountMin > input.wordCountMax) {
      errors.push('wordCountMin must be <= wordCountMax');
    }
    if (input.publishMode !== undefined && !VALID_MODES.includes(input.publishMode as PublishMode)) {
      errors.push(`publishMode must be one of: ${VALID_MODES.join(', ')}`);
    }

    if (errors.length > 0) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/validation',
        title: 'Invalid Thresholds',
        status: 400,
        detail: errors.join('; '),
      }));
    }

    return ok(undefined);
  }
}
