// Topic configuration service (TASK-014)
// F-004: Three input modes — auto-infer, manual keywords, GSC import
// All paths cluster into TopicCluster entities with priorities.

import { generateId } from '../../../../lib/id.js';
import { type Result, ok, err, operationError, type OperationError } from '../../../../lib/result.js';
import type { OperationContext } from '../../../../lib/context.js';
import type { TopicRepository, TopicConfigRecord, TopicClusterRecord } from './topic.repository.js';

export interface ClusterResult {
  readonly name: string;
  readonly keywords: string[];
}

export interface LlmClusterer {
  clusterKeywords(keywords: string[]): Promise<ClusterResult[]>;
  inferTopics(pageData: string[]): Promise<string[]>;
}

export interface TopicConfigResult {
  readonly config: TopicConfigRecord;
  readonly clusters: TopicClusterRecord[];
}

type ClusterPriority = 'high' | 'medium' | 'low';

export class TopicService {
  constructor(
    private readonly repository: TopicRepository,
    private readonly llm: LlmClusterer,
  ) {}

  async setTopics(
    siteId: string,
    keywords: string[],
    _ctx: OperationContext,
  ): Promise<Result<TopicConfigResult, OperationError>> {
    const cleaned = this.parseKeywords(keywords);
    if (cleaned.length === 0) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/validation',
        title: 'No Valid Keywords',
        status: 400,
        detail: 'At least one keyword is required',
      }));
    }

    // Remove existing config for this site (re-entrant)
    await this.repository.deleteConfigBySiteId(siteId);

    const config = await this.repository.createConfig({
      id: generateId('topicConfig'),
      siteId,
      source: 'manual',
      seedKeywords: JSON.stringify(cleaned),
    });

    const clusters = await this.buildClusters(config.id, cleaned);
    return ok({ config, clusters });
  }

  async inferTopics(
    siteId: string,
    pageData: string[],
    _ctx: OperationContext,
  ): Promise<Result<TopicConfigResult, OperationError>> {
    if (pageData.length === 0) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/validation',
        title: 'No Page Data',
        status: 400,
        detail: 'At least one page is required for topic inference',
      }));
    }

    const inferred = await this.llm.inferTopics(pageData);
    if (inferred.length === 0) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/inference',
        title: 'Topic Inference Failed',
        status: 422,
        detail: 'Could not infer topics from the provided content',
      }));
    }

    await this.repository.deleteConfigBySiteId(siteId);

    const config = await this.repository.createConfig({
      id: generateId('topicConfig'),
      siteId,
      source: 'auto_inferred',
      seedKeywords: JSON.stringify(inferred),
    });

    const clusters = await this.buildClusters(config.id, inferred);
    return ok({ config, clusters });
  }

  async getTopics(
    siteId: string,
    _ctx: OperationContext,
  ): Promise<Result<TopicConfigResult, OperationError>> {
    const config = await this.repository.findConfigBySiteId(siteId);
    if (!config) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/not-found',
        title: 'Topic Config Not Found',
        status: 404,
        detail: `No topic configuration found for site ${siteId}`,
      }));
    }

    const clusters = await this.repository.findClustersByConfigId(config.id);
    return ok({ config, clusters });
  }

  async updateClusterPriority(
    clusterId: string,
    priority: ClusterPriority,
    _ctx: OperationContext,
  ): Promise<Result<TopicClusterRecord, OperationError>> {
    const valid: ClusterPriority[] = ['high', 'medium', 'low'];
    if (!valid.includes(priority)) {
      return err(operationError({
        type: 'https://api.smithai.com/errors/validation',
        title: 'Invalid Priority',
        status: 400,
        detail: `Priority must be one of: ${valid.join(', ')}`,
      }));
    }

    const cluster = await this.repository.updateClusterPriority(clusterId, priority);
    return ok(cluster);
  }

  private parseKeywords(input: string[]): string[] {
    // Accept array of strings, split by comma/newline, deduplicate
    const all = input
      .flatMap(s => s.split(/[,\n]/))
      .map(k => k.trim().toLowerCase())
      .filter(k => k.length > 0);

    return [...new Set(all)];
  }

  private async buildClusters(
    configId: string,
    keywords: string[],
  ): Promise<TopicClusterRecord[]> {
    let clusterData: ClusterResult[];

    if (keywords.length <= 5) {
      // Small set → single cluster
      clusterData = [{ name: 'Primary Topics', keywords }];
    } else {
      clusterData = await this.llm.clusterKeywords(keywords);
    }

    const records: TopicClusterRecord[] = [];
    for (let i = 0; i < clusterData.length; i++) {
      const c = clusterData[i]!;
      const record = await this.repository.addCluster({
        id: generateId('topicCluster'),
        topicConfigId: configId,
        name: c.name,
        keywords: JSON.stringify(c.keywords),
        priority: i === 0 ? 'high' : 'medium',
        contentCount: 0,
      });
      records.push(record);
    }

    return records;
  }
}
