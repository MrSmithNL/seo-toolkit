// TASK-F05: Conformance suite runner
// Validates YAML test case structure and completeness

import { describe, it, expect } from 'vitest';
import { readFileSync, readdirSync } from 'fs';
import { join } from 'path';
import { parse } from 'yaml';

interface ConformanceCase {
  name: string;
  method: string;
  input: Record<string, unknown>;
  expect: {
    success: boolean;
    data?: Record<string, unknown>;
    error?: { status: number };
  };
  setup?: string;
  context?: string;
}

interface ConformanceSuite {
  feature: string;
  service: string;
  safety_checks: string[];
  cases: ConformanceCase[];
}

const CONFORMANCE_DIR = join(__dirname);

function loadSuites(): ConformanceSuite[] {
  const files = readdirSync(CONFORMANCE_DIR)
    .filter(f => f.endsWith('.yaml'));

  return files.map(f => {
    const content = readFileSync(join(CONFORMANCE_DIR, f), 'utf-8');
    return parse(content) as ConformanceSuite;
  });
}

describe('Conformance Suite — Structure Validation (TASK-F05)', () => {
  const suites = loadSuites();

  it('has 6 conformance suites (one per feature)', () => {
    expect(suites).toHaveLength(6);
  });

  it('every suite has feature, service, safety_checks, and cases', () => {
    for (const suite of suites) {
      expect(suite.feature).toBeTruthy();
      expect(suite.service).toBeTruthy();
      expect(suite.safety_checks).toBeDefined();
      expect(suite.safety_checks.length).toBeGreaterThan(0);
      expect(suite.cases).toBeDefined();
      expect(suite.cases.length).toBeGreaterThan(0);
    }
  });

  it('every suite has ≥5 test cases', () => {
    for (const suite of suites) {
      expect(suite.cases.length).toBeGreaterThanOrEqual(5);
    }
  });

  it('every case has name, method, input, and expect', () => {
    for (const suite of suites) {
      for (const c of suite.cases) {
        expect(c.name).toBeTruthy();
        expect(c.method).toBeTruthy();
        expect(c.input).toBeDefined();
        expect(c.expect).toBeDefined();
        expect(typeof c.expect.success).toBe('boolean');
      }
    }
  });

  it('error cases have status codes', () => {
    for (const suite of suites) {
      for (const c of suite.cases) {
        if (!c.expect.success) {
          expect(c.expect.error).toBeDefined();
          expect(c.expect.error!.status).toBeGreaterThanOrEqual(400);
        }
      }
    }
  });

  it('covers all 6 features', () => {
    const features = suites.map(s => s.feature);
    expect(features.some(f => f.includes('Site Registration'))).toBe(true);
    expect(features.some(f => f.includes('CMS Connection'))).toBe(true);
    expect(features.some(f => f.includes('Brand Voice'))).toBe(true);
    expect(features.some(f => f.includes('Topic Configuration'))).toBe(true);
    expect(features.some(f => f.includes('Quality Thresholds'))).toBe(true);
    expect(features.some(f => f.includes('AISO Preferences'))).toBe(true);
  });

  it('each suite documents safety checks', () => {
    for (const suite of suites) {
      expect(suite.safety_checks.length).toBeGreaterThanOrEqual(2);
      for (const check of suite.safety_checks) {
        expect(typeof check).toBe('string');
        expect(check.length).toBeGreaterThan(10);
      }
    }
  });

  it('includes both happy path and error cases per suite', () => {
    for (const suite of suites) {
      const happy = suite.cases.filter(c => c.expect.success);
      const errors = suite.cases.filter(c => !c.expect.success);
      expect(happy.length).toBeGreaterThan(0);
      expect(errors.length).toBeGreaterThan(0);
    }
  });

  it('total case count across all suites', () => {
    const total = suites.reduce((sum, s) => sum + s.cases.length, 0);
    expect(total).toBeGreaterThanOrEqual(30); // ≥5 per feature × 6 features
  });
});
