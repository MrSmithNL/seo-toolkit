// AISO Factor Registry (TASK-016)
// 36-factor model grouped into 6 categories

export type AISOCategory =
  | 'structured_data'
  | 'content_structure'
  | 'authority_signals'
  | 'technical_seo'
  | 'ai_discoverability'
  | 'user_experience';

export interface AISOFactor {
  readonly id: string;
  readonly name: string;
  readonly category: AISOCategory;
  readonly description: string;
}

const FACTORS: readonly AISOFactor[] = [
  // structured_data (8)
  { id: 'schema_faq', name: 'FAQ Schema', category: 'structured_data', description: 'FAQPage schema markup for question-answer content' },
  { id: 'schema_howto', name: 'HowTo Schema', category: 'structured_data', description: 'HowTo schema for step-by-step instructions' },
  { id: 'schema_product', name: 'Product Schema', category: 'structured_data', description: 'Product schema for e-commerce content' },
  { id: 'schema_review', name: 'Review Schema', category: 'structured_data', description: 'Review schema for product/service reviews' },
  { id: 'schema_breadcrumb', name: 'Breadcrumb Schema', category: 'structured_data', description: 'BreadcrumbList schema for navigation hierarchy' },
  { id: 'schema_article', name: 'Article Schema', category: 'structured_data', description: 'Article schema for blog posts and news' },
  { id: 'schema_organization', name: 'Organization Schema', category: 'structured_data', description: 'Organization schema for publisher identity' },
  { id: 'schema_video', name: 'Video Schema', category: 'structured_data', description: 'VideoObject schema for embedded videos' },

  // content_structure (7)
  { id: 'heading_hierarchy', name: 'Heading Hierarchy', category: 'content_structure', description: 'Proper H1-H6 heading nesting' },
  { id: 'definition_paragraphs', name: 'Definition Paragraphs', category: 'content_structure', description: 'Clear concise definitions that AI can extract' },
  { id: 'numbered_lists', name: 'Numbered Lists', category: 'content_structure', description: 'Ordered lists for step-by-step and ranking content' },
  { id: 'comparison_tables', name: 'Comparison Tables', category: 'content_structure', description: 'Structured data tables for comparisons' },
  { id: 'summary_boxes', name: 'Summary Boxes', category: 'content_structure', description: 'TL;DR and key points summaries' },
  { id: 'key_takeaways', name: 'Key Takeaway Sections', category: 'content_structure', description: 'Highlighted takeaway blocks' },
  { id: 'topic_clustering', name: 'Topic Clustering', category: 'content_structure', description: 'Related subtopics grouped logically' },

  // authority_signals (6)
  { id: 'citation_authority', name: 'Citation Authority', category: 'authority_signals', description: 'Links to authoritative sources' },
  { id: 'expert_attribution', name: 'Expert Attribution', category: 'authority_signals', description: 'Named expert quotes and credentials' },
  { id: 'statistical_evidence', name: 'Statistical Evidence', category: 'authority_signals', description: 'Data points and statistics with sources' },
  { id: 'source_diversity', name: 'Source Diversity', category: 'authority_signals', description: 'Multiple independent sources cited' },
  { id: 'recency_signals', name: 'Recency Signals', category: 'authority_signals', description: 'Recent dates, updated timestamps' },
  { id: 'eeat_markers', name: 'E-E-A-T Markers', category: 'authority_signals', description: 'Experience, Expertise, Authoritativeness, Trustworthiness signals' },

  // technical_seo (5)
  { id: 'page_speed', name: 'Page Speed', category: 'technical_seo', description: 'Fast loading optimised content' },
  { id: 'mobile_responsive', name: 'Mobile Responsiveness', category: 'technical_seo', description: 'Mobile-first content layout' },
  { id: 'canonical_urls', name: 'Canonical URLs', category: 'technical_seo', description: 'Proper canonical tag implementation' },
  { id: 'sitemap_inclusion', name: 'XML Sitemap Inclusion', category: 'technical_seo', description: 'Pages included in sitemap' },
  { id: 'internal_linking', name: 'Internal Linking Depth', category: 'technical_seo', description: 'Strategic internal link structure' },

  // ai_discoverability (6)
  { id: 'concise_answers', name: 'Concise Answer Paragraphs', category: 'ai_discoverability', description: 'Direct answers in 2-3 sentences for AI extraction' },
  { id: 'qa_format', name: 'Question-Answer Format', category: 'ai_discoverability', description: 'Explicit Q&A patterns AI can parse' },
  { id: 'definitive_statements', name: 'Definitive Statements', category: 'ai_discoverability', description: 'Clear declarative sentences for AI citations' },
  { id: 'entity_mentions', name: 'Entity Mentions', category: 'ai_discoverability', description: 'Named entities and proper nouns for knowledge graph' },
  { id: 'topic_completeness', name: 'Topic Completeness', category: 'ai_discoverability', description: 'Comprehensive coverage of the topic' },
  { id: 'natural_language', name: 'Natural Language Phrasing', category: 'ai_discoverability', description: 'Conversational phrasing matching AI search queries' },

  // user_experience (4)
  { id: 'readability_score', name: 'Readability Score', category: 'user_experience', description: 'Flesch-Kincaid readability optimisation' },
  { id: 'content_freshness', name: 'Content Freshness', category: 'user_experience', description: 'Regular content updates and date signals' },
  { id: 'visual_content', name: 'Visual Content Ratio', category: 'user_experience', description: 'Images, diagrams, and media balance' },
  { id: 'engagement_structure', name: 'Engagement Structure', category: 'user_experience', description: 'Scannable layout with clear visual hierarchy' },
] as const;

export class FactorRegistry {
  private readonly factors: ReadonlyMap<string, AISOFactor>;

  constructor() {
    this.factors = new Map(FACTORS.map(f => [f.id, f]));
  }

  getAll(): AISOFactor[] {
    return [...this.factors.values()];
  }

  getByCategory(category: AISOCategory): AISOFactor[] {
    return [...this.factors.values()].filter(f => f.category === category);
  }

  getCategories(): AISOCategory[] {
    return ['structured_data', 'content_structure', 'authority_signals', 'technical_seo', 'ai_discoverability', 'user_experience'];
  }

  validate(factorIds: string[]): { valid: boolean; unknown: string[] } {
    const unknown = factorIds.filter(id => !this.factors.has(id));
    return { valid: unknown.length === 0, unknown };
  }

  get count(): number {
    return this.factors.size;
  }
}
