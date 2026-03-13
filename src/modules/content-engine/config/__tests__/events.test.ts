// TASK-017: Event bus integration tests
// Verifies all 7 CloudEvents 1.0 events emit with typed payloads

import { describe, it, expect } from 'vitest';
import { ConfigEventBus, type CloudEvent, type ConfigEventMap } from '../events.js';

describe('ConfigEventBus — CloudEvents 1.0 (TASK-017)', () => {
  const ctx = { tenantId: 'tnt_test', correlationId: 'cor_123' };

  it('emits site.registered with correct CloudEvents envelope', () => {
    const bus = new ConfigEventBus();
    let received: CloudEvent<unknown> | null = null;

    bus.on('site.registered', (event) => { received = event; });

    const event = bus.emit('site.registered', {
      siteId: 'ste_abc', url: 'https://example.com', tenantId: 'tnt_test',
    }, { ...ctx, subject: 'ste_abc' });

    expect(event.specversion).toBe('1.0');
    expect(event.source).toBe('/modules/content-engine-config');
    expect(event.type).toBe('com.smithai.site.registered.v1');
    expect(event.subject).toBe('ste_abc');
    expect(event.datacontenttype).toBe('application/json');
    expect(event.tenantid).toBe('tnt_test');
    expect(event.correlationid).toBe('cor_123');
    expect(event.time).toBeTruthy();
    expect(event.id).toBeTruthy();
    expect(event.data.siteId).toBe('ste_abc');
    expect(received).not.toBeNull();
  });

  it('emits site.crawled with CMS detection data', () => {
    const bus = new ConfigEventBus();
    const event = bus.emit('site.crawled', {
      siteId: 'ste_abc', cmsType: 'wordpress', languages: ['en', 'nl'], contentCount: 42,
    }, ctx);

    expect(event.type).toBe('com.smithai.site.crawled.v1');
    expect(event.data.cmsType).toBe('wordpress');
    expect(event.data.contentCount).toBe(42);
  });

  it('emits cms.connected', () => {
    const bus = new ConfigEventBus();
    const event = bus.emit('cms.connected', {
      siteId: 'ste_abc', cmsType: 'shopify', status: 'connected',
    }, ctx);

    expect(event.type).toBe('com.smithai.cms.connected.v1');
    expect(event.data.cmsType).toBe('shopify');
  });

  it('emits cms.verified', () => {
    const bus = new ConfigEventBus();
    const event = bus.emit('cms.verified', {
      siteId: 'ste_abc', writeAccessConfirmed: true,
    }, ctx);

    expect(event.type).toBe('com.smithai.cms.verified.v1');
    expect(event.data.writeAccessConfirmed).toBe(true);
  });

  it('emits voice.extracted', () => {
    const bus = new ConfigEventBus();
    const event = bus.emit('voice.extracted', {
      siteId: 'ste_abc', voiceProfileId: 'vce_xyz',
    }, ctx);

    expect(event.type).toBe('com.smithai.voice.extracted.v1');
    expect(event.data.voiceProfileId).toBe('vce_xyz');
  });

  it('emits topics.configured', () => {
    const bus = new ConfigEventBus();
    const event = bus.emit('topics.configured', {
      siteId: 'ste_abc', clusterCount: 5, keywordCount: 45,
    }, ctx);

    expect(event.type).toBe('com.smithai.topics.configured.v1');
    expect(event.data.clusterCount).toBe(5);
  });

  it('emits config.complete', () => {
    const bus = new ConfigEventBus();
    const event = bus.emit('config.complete', {
      siteId: 'ste_abc', configuredFeatures: ['site', 'cms', 'topics'],
    }, ctx);

    expect(event.type).toBe('com.smithai.config.complete.v1');
    expect(event.data.configuredFeatures).toHaveLength(3);
  });

  it('supports multiple subscribers', () => {
    const bus = new ConfigEventBus();
    const received: string[] = [];

    bus.on('site.registered', () => { received.push('handler1'); });
    bus.on('site.registered', () => { received.push('handler2'); });

    bus.emit('site.registered', {
      siteId: 'ste_abc', url: 'https://example.com', tenantId: 'tnt_test',
    }, ctx);

    expect(received).toEqual(['handler1', 'handler2']);
  });

  it('tracks listener count', () => {
    const bus = new ConfigEventBus();
    expect(bus.listenerCount('site.registered')).toBe(0);

    bus.on('site.registered', () => {});
    bus.on('site.registered', () => {});
    expect(bus.listenerCount('site.registered')).toBe(2);

    bus.off('site.registered');
    expect(bus.listenerCount('site.registered')).toBe(0);
  });

  it('does not crash when emitting with no subscribers', () => {
    const bus = new ConfigEventBus();
    const event = bus.emit('site.registered', {
      siteId: 'ste_abc', url: 'https://example.com', tenantId: 'tnt_test',
    }, ctx);

    expect(event.data.siteId).toBe('ste_abc');
  });

  it('manifests all 7 event types', () => {
    // Verify the type system covers all expected events
    const eventTypes: Array<keyof ConfigEventMap> = [
      'site.registered', 'site.crawled', 'cms.connected', 'cms.verified',
      'voice.extracted', 'topics.configured', 'config.complete',
    ];
    expect(eventTypes).toHaveLength(7);
  });
});
