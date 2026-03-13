// Brand voice extraction service (TASK-013)
// F-003: Extract brand voice from site content via LLM, or use defaults.

import { generateId } from '../../../../lib/id.js';
import { type Result, type OperationError, ok, err, operationError } from '../../../../lib/result.js';
import type { OperationContext } from '../../../../lib/context.js';
import type { VoiceRepository, VoiceProfileRecord } from './voice.repository.js';

export interface ExtractedVoice {
  brandName?: string;
  industry?: string;
  targetAudience?: string;
  brandValues?: string;
  keyTopics?: string;
  tone?: string;
  sentenceStructure?: string;
  vocabularyLevel?: string;
  person?: string;
}

export interface LlmClient {
  extractVoice(content: string): Promise<ExtractedVoice>;
}

export class VoiceService {
  constructor(
    private readonly repository: VoiceRepository,
    private readonly llm: LlmClient,
  ) {}

  async extractVoice(
    siteId: string, sourceUrl: string, _ctx: OperationContext,
  ): Promise<Result<VoiceProfileRecord, OperationError>> {
    const extracted = await this.llm.extractVoice(sourceUrl);

    const profile = await this.repository.create({
      id: generateId('voiceProfile'),
      siteId,
      brandName: extracted.brandName,
      industry: extracted.industry,
      targetAudience: extracted.targetAudience,
      brandValues: extracted.brandValues,
      keyTopics: extracted.keyTopics,
      tone: extracted.tone ?? 'conversational',
      sentenceStructure: extracted.sentenceStructure ?? 'mixed',
      vocabularyLevel: extracted.vocabularyLevel ?? 'intermediate',
      person: extracted.person ?? 'second',
      extractedFromUrl: sourceUrl,
      extractedAt: new Date().toISOString(),
    });

    return ok(profile);
  }

  async createDefaults(
    siteId: string, _ctx: OperationContext,
  ): Promise<Result<VoiceProfileRecord, OperationError>> {
    const profile = await this.repository.create({
      id: generateId('voiceProfile'),
      siteId,
    });
    return ok(profile);
  }

  async getProfile(
    siteId: string, _ctx: OperationContext,
  ): Promise<Result<VoiceProfileRecord, OperationError>> {
    const profile = await this.repository.findBySiteId(siteId);
    if (!profile) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/not-found',
        title: 'Voice Profile Not Found',
        status: 404,
        detail: `No voice profile for site ${siteId}`,
      }));
    }
    return ok(profile);
  }

  async updateProfile(
    siteId: string, fields: Partial<ExtractedVoice>, _ctx: OperationContext,
  ): Promise<Result<VoiceProfileRecord, OperationError>> {
    const updated = await this.repository.update(siteId, fields);
    return ok(updated);
  }
}
