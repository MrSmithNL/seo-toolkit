// Configuration completeness orchestrator (TASK-018)
// Tracks which config features are complete per site.
// Emits config.complete when Must-have features (F-001, F-002, F-004) are done.

import { type Result, ok, type OperationError } from '../../../lib/result.js';
import type { OperationContext } from '../../../lib/context.js';

export interface FeatureStatus {
  readonly feature: string;
  readonly label: string;
  readonly required: boolean;
  readonly configured: boolean;
}

export interface ConfigStatus {
  readonly siteId: string;
  readonly features: FeatureStatus[];
  readonly requiredComplete: boolean;
  readonly allComplete: boolean;
  readonly pipelineReady: boolean;
}

export interface ConfigCheckers {
  hasSiteRegistration(siteId: string): Promise<boolean>;
  hasCmsConnection(siteId: string): Promise<boolean>;
  hasVoiceProfile(siteId: string): Promise<boolean>;
  hasTopicConfig(siteId: string): Promise<boolean>;
  hasQualityThresholds(siteId: string): Promise<boolean>;
  hasAisoPreferences(siteId: string): Promise<boolean>;
}

const FEATURES = [
  { feature: 'F-001', label: 'Site Registration', required: true },
  { feature: 'F-002', label: 'CMS Connection', required: true },
  { feature: 'F-003', label: 'Brand Voice', required: false },
  { feature: 'F-004', label: 'Topic Configuration', required: true },
  { feature: 'F-005', label: 'Quality Thresholds', required: false },
  { feature: 'F-006', label: 'AISO Preferences', required: false },
] as const;

export class ConfigOrchestrator {
  constructor(private readonly checkers: ConfigCheckers) {}

  async getStatus(
    siteId: string,
    _ctx: OperationContext,
  ): Promise<Result<ConfigStatus, OperationError>> {
    const checks = await Promise.all([
      this.checkers.hasSiteRegistration(siteId),
      this.checkers.hasCmsConnection(siteId),
      this.checkers.hasVoiceProfile(siteId),
      this.checkers.hasTopicConfig(siteId),
      this.checkers.hasQualityThresholds(siteId),
      this.checkers.hasAisoPreferences(siteId),
    ]);

    const features: FeatureStatus[] = FEATURES.map((f, i) => ({
      feature: f.feature,
      label: f.label,
      required: f.required,
      configured: checks[i]!,
    }));

    const requiredComplete = features
      .filter(f => f.required)
      .every(f => f.configured);

    const allComplete = features.every(f => f.configured);

    return ok({
      siteId,
      features,
      requiredComplete,
      allComplete,
      pipelineReady: requiredComplete,
    });
  }
}
