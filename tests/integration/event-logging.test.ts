// TASK-F08: CloudEvents event logging verification
// All 7 events must emit with CloudEvents 1.0 envelope

import { describe, it, expect } from 'vitest';
import {
  ConfigEventBus,
  type CloudEvent,
  type ConfigEventType,
  type ConfigEventMap,
} from '../../src/modules/content-engine/config/events.js';

const ALL_EVENTS: Array<{ type: ConfigEventType; payload: ConfigEventMap[ConfigEventType] }> = [
  {
    type: 'site.registered',
    payload: { siteId: 'ste_test', url: 'https://example.com', tenantId: 'tnt_t' },
  },
  {
    type: 'site.crawled',
    payload: { siteId: 'ste_test', cmsType: 'wordpress', languages: ['en'], contentCount: 10 },
  },
  {
    type: 'cms.connected',
    payload: { siteId: 'ste_test', cmsType: 'shopify', status: 'connected' },
  },
  {
    type: 'cms.verified',
    payload: { siteId: 'ste_test', writeAccessConfirmed: true },
  },
  {
    type: 'voice.extracted',
    payload: { siteId: 'ste_test', voiceProfileId: 'vce_test' },
  },
  {
    type: 'topics.configured',
    payload: { siteId: 'ste_test', clusterCount: 3, keywordCount: 25 },
  },
  {
    type: 'config.complete',
    payload: { siteId: 'ste_test', configuredFeatures: ['site', 'cms', 'topics'] },
  },
];

describe('CloudEvents 1.0 Envelope Verification (TASK-F08)', () => {
  const ctx = { tenantId: 'tnt_verification', correlationId: 'cor_verify_123', subject: 'ste_test' };

  for (const { type, payload } of ALL_EVENTS) {
    it(`${type} has valid CloudEvents 1.0 envelope`, () => {
      const bus = new ConfigEventBus();
      const event = bus.emit(type, payload as never, ctx);

      // CloudEvents 1.0 required attributes
      expect(event.specversion).toBe('1.0');
      expect(event.id).toBeTruthy();
      expect(typeof event.id).toBe('string');
      expect(event.source).toBe('/modules/content-engine-config');
      expect(event.type).toBe(`com.smithai.${type}.v1`);
      expect(event.time).toBeTruthy();
      expect(event.datacontenttype).toBe('application/json');

      // Custom extension attributes
      expect(event.tenantid).toBe('tnt_verification');
      expect(event.correlationid).toBe('cor_verify_123');

      // Subject (optional but expected)
      expect(event.subject).toBe('ste_test');

      // Data payload present
      expect(event.data).toBeDefined();
      expect(typeof event.data).toBe('object');
    });
  }

  it('all 7 events have unique IDs', () => {
    const bus = new ConfigEventBus();
    const ids = ALL_EVENTS.map(({ type, payload }) =>
      bus.emit(type, payload as never, ctx).id
    );

    const uniqueIds = new Set(ids);
    expect(uniqueIds.size).toBe(7);
  });

  it('event timestamps are valid ISO 8601', () => {
    const bus = new ConfigEventBus();
    for (const { type, payload } of ALL_EVENTS) {
      const event = bus.emit(type, payload as never, ctx);
      const parsed = new Date(event.time);
      expect(parsed.toISOString()).toBe(event.time);
    }
  });

  it('events are JSON-serialisable (no class instances or functions)', () => {
    const bus = new ConfigEventBus();
    for (const { type, payload } of ALL_EVENTS) {
      const event = bus.emit(type, payload as never, ctx);
      const serialised = JSON.parse(JSON.stringify(event));
      expect(serialised.specversion).toBe('1.0');
      expect(serialised.data).toEqual(event.data);
    }
  });

  it('subscriber receives complete CloudEvents envelope', () => {
    const bus = new ConfigEventBus();
    let received: CloudEvent<unknown> | null = null;

    bus.on('site.registered', (event) => { received = event; });

    bus.emit('site.registered', {
      siteId: 'ste_sub', url: 'https://sub.com', tenantId: 'tnt_sub',
    }, { tenantId: 'tnt_sub', correlationId: 'cor_sub', subject: 'ste_sub' });

    expect(received).not.toBeNull();
    expect(received!.specversion).toBe('1.0');
    expect(received!.tenantid).toBe('tnt_sub');
    expect(received!.correlationid).toBe('cor_sub');
  });
});
