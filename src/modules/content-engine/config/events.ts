// Configuration event bus (TASK-017)
// CloudEvents 1.0 compliant typed event system for E-001

import { nanoid } from 'nanoid';

// === CloudEvents 1.0 Envelope ===

export interface CloudEvent<T> {
  readonly specversion: '1.0';
  readonly id: string;
  readonly source: string;
  readonly type: string;
  readonly subject?: string;
  readonly time: string;
  readonly datacontenttype: 'application/json';
  readonly tenantid: string;
  readonly correlationid: string;
  readonly data: T;
}

// === Event Payloads ===

export interface SiteRegisteredPayload {
  readonly siteId: string;
  readonly url: string;
  readonly tenantId: string;
}

export interface SiteCrawledPayload {
  readonly siteId: string;
  readonly cmsType: string;
  readonly languages: string[];
  readonly contentCount: number;
}

export interface CmsConnectedPayload {
  readonly siteId: string;
  readonly cmsType: string;
  readonly status: string;
}

export interface CmsVerifiedPayload {
  readonly siteId: string;
  readonly writeAccessConfirmed: boolean;
}

export interface VoiceExtractedPayload {
  readonly siteId: string;
  readonly voiceProfileId: string;
}

export interface TopicsConfiguredPayload {
  readonly siteId: string;
  readonly clusterCount: number;
  readonly keywordCount: number;
}

export interface ConfigCompletePayload {
  readonly siteId: string;
  readonly configuredFeatures: string[];
}

// === Event Type Map ===

export interface ConfigEventMap {
  'site.registered': SiteRegisteredPayload;
  'site.crawled': SiteCrawledPayload;
  'cms.connected': CmsConnectedPayload;
  'cms.verified': CmsVerifiedPayload;
  'voice.extracted': VoiceExtractedPayload;
  'topics.configured': TopicsConfiguredPayload;
  'config.complete': ConfigCompletePayload;
}

export type ConfigEventType = keyof ConfigEventMap;

const EVENT_SOURCE = '/modules/content-engine-config';
const CE_TYPE_PREFIX = 'com.smithai';

// === Typed Event Bus (in-process for R1, swap to Trigger.dev for R2) ===

type EventHandler<T> = (event: CloudEvent<T>) => void | Promise<void>;

export class ConfigEventBus {
  private readonly handlers = new Map<string, EventHandler<unknown>[]>();

  emit<K extends ConfigEventType>(
    eventType: K,
    payload: ConfigEventMap[K],
    context: { tenantId: string; correlationId: string; subject?: string },
  ): CloudEvent<ConfigEventMap[K]> {
    const event: CloudEvent<ConfigEventMap[K]> = {
      specversion: '1.0',
      id: nanoid(),
      source: EVENT_SOURCE,
      type: `${CE_TYPE_PREFIX}.${eventType}.v1`,
      subject: context.subject,
      time: new Date().toISOString(),
      datacontenttype: 'application/json',
      tenantid: context.tenantId,
      correlationid: context.correlationId,
      data: payload,
    };

    const handlers = this.handlers.get(eventType) ?? [];
    for (const handler of handlers) {
      handler(event as CloudEvent<unknown>);
    }

    return event;
  }

  on<K extends ConfigEventType>(
    eventType: K,
    handler: EventHandler<ConfigEventMap[K]>,
  ): void {
    const existing = this.handlers.get(eventType) ?? [];
    existing.push(handler as EventHandler<unknown>);
    this.handlers.set(eventType, existing);
  }

  off<K extends ConfigEventType>(eventType: K): void {
    this.handlers.delete(eventType);
  }

  listenerCount(eventType: ConfigEventType): number {
    return (this.handlers.get(eventType) ?? []).length;
  }
}
