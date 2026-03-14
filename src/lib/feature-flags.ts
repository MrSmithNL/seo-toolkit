// Feature flags — simple file-based for R1 CLI
// Future: swap to PostHog or LaunchDarkly via interface

const FLAGS = {
  'content-engine-v1': true,
} as const;

type FlagName = keyof typeof FLAGS;

export function isEnabled(flag: FlagName): boolean {
  return FLAGS[flag] ?? false;
}

export function assertEnabled(flag: FlagName): void {
  if (!isEnabled(flag)) {
    throw new Error(`Feature "${flag}" is not enabled. Enable it in src/lib/feature-flags.ts`);
  }
}
