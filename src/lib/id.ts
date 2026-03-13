// Prefixed ID generation — API standards §4.3

import { nanoid } from 'nanoid';

const ID_PREFIXES = {
  site: 'ste',
  cmsConnection: 'cms',
  voiceProfile: 'vce',
  topicConfig: 'tpc',
  topicCluster: 'tcl',
  qualityThresholds: 'qty',
  aisoPreferences: 'asp',
  tenant: 'tnt',
} as const;

type EntityType = keyof typeof ID_PREFIXES;

export function generateId(entity: EntityType): string {
  return `${ID_PREFIXES[entity]}_${nanoid(16)}`;
}
