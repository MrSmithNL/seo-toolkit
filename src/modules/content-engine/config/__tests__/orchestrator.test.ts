// TASK-018: Configuration completeness orchestrator tests
// Tracks feature completion, pipeline readiness

import { describe, it, expect } from 'vitest';
import { createOperationContext } from '../../../../lib/context.js';
import { ConfigOrchestrator, type ConfigCheckers } from '../orchestrator.js';

function mockCheckers(overrides: Partial<Record<keyof ConfigCheckers, boolean>> = {}): ConfigCheckers {
  return {
    hasSiteRegistration: async () => overrides.hasSiteRegistration ?? false,
    hasCmsConnection: async () => overrides.hasCmsConnection ?? false,
    hasVoiceProfile: async () => overrides.hasVoiceProfile ?? false,
    hasTopicConfig: async () => overrides.hasTopicConfig ?? false,
    hasQualityThresholds: async () => overrides.hasQualityThresholds ?? false,
    hasAisoPreferences: async () => overrides.hasAisoPreferences ?? false,
  };
}

const ctx = createOperationContext('tnt_test');
const siteId = 'ste_test1';

describe('ConfigOrchestrator — Completeness Tracking (TASK-018)', () => {
  it('reports all unconfigured when nothing is set up', async () => {
    const orchestrator = new ConfigOrchestrator(mockCheckers());
    const result = await orchestrator.getStatus(siteId, ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;

    expect(result.data.features).toHaveLength(6);
    expect(result.data.requiredComplete).toBe(false);
    expect(result.data.allComplete).toBe(false);
    expect(result.data.pipelineReady).toBe(false);
  });

  it('reports pipeline ready when all Must-haves are configured', async () => {
    const orchestrator = new ConfigOrchestrator(mockCheckers({
      hasSiteRegistration: true,
      hasCmsConnection: true,
      hasTopicConfig: true,
    }));
    const result = await orchestrator.getStatus(siteId, ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;

    expect(result.data.requiredComplete).toBe(true);
    expect(result.data.pipelineReady).toBe(true);
    expect(result.data.allComplete).toBe(false); // optional features still missing
  });

  it('reports not ready when one Must-have is missing', async () => {
    const orchestrator = new ConfigOrchestrator(mockCheckers({
      hasSiteRegistration: true,
      hasCmsConnection: true,
      // hasTopicConfig missing — required!
    }));
    const result = await orchestrator.getStatus(siteId, ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;

    expect(result.data.requiredComplete).toBe(false);
    expect(result.data.pipelineReady).toBe(false);
  });

  it('reports all complete when everything is configured', async () => {
    const orchestrator = new ConfigOrchestrator(mockCheckers({
      hasSiteRegistration: true,
      hasCmsConnection: true,
      hasVoiceProfile: true,
      hasTopicConfig: true,
      hasQualityThresholds: true,
      hasAisoPreferences: true,
    }));
    const result = await orchestrator.getStatus(siteId, ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;

    expect(result.data.allComplete).toBe(true);
    expect(result.data.pipelineReady).toBe(true);
  });

  it('correctly identifies required vs optional features', async () => {
    const orchestrator = new ConfigOrchestrator(mockCheckers());
    const result = await orchestrator.getStatus(siteId, ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;

    const required = result.data.features.filter(f => f.required);
    const optional = result.data.features.filter(f => !f.required);

    expect(required).toHaveLength(3); // F-001, F-002, F-004
    expect(optional).toHaveLength(3); // F-003, F-005, F-006
    expect(required.map(f => f.feature).sort()).toEqual(['F-001', 'F-002', 'F-004']);
  });

  it('includes feature labels for display', async () => {
    const orchestrator = new ConfigOrchestrator(mockCheckers());
    const result = await orchestrator.getStatus(siteId, ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;

    const labels = result.data.features.map(f => f.label);
    expect(labels).toContain('Site Registration');
    expect(labels).toContain('CMS Connection');
    expect(labels).toContain('Topic Configuration');
  });

  it('optional features alone do not make pipeline ready', async () => {
    const orchestrator = new ConfigOrchestrator(mockCheckers({
      hasVoiceProfile: true,
      hasQualityThresholds: true,
      hasAisoPreferences: true,
    }));
    const result = await orchestrator.getStatus(siteId, ctx);

    expect(result.success).toBe(true);
    if (!result.success) return;

    expect(result.data.requiredComplete).toBe(false);
    expect(result.data.pipelineReady).toBe(false);
  });
});
