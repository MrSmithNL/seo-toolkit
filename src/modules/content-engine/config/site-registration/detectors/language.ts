// Language detection — hreflang, html lang, fallback (TASK-007)
// F-001 US-003: Detect site languages for multi-language content support.

import type { HttpFetcher } from './types.js';

export interface DetectedLanguage {
  readonly code: string;
  readonly name: string;
  readonly urlPattern?: string;
}

// Common language code → name mapping
const LANGUAGE_NAMES: Record<string, string> = {
  en: 'English', nl: 'Dutch', de: 'German', fr: 'French',
  es: 'Spanish', it: 'Italian', pt: 'Portuguese', ja: 'Japanese',
  zh: 'Chinese', ko: 'Korean', ar: 'Arabic', ru: 'Russian',
  sv: 'Swedish', da: 'Danish', no: 'Norwegian', fi: 'Finnish',
  pl: 'Polish', cs: 'Czech', tr: 'Turkish', th: 'Thai',
};

function languageName(code: string): string {
  return LANGUAGE_NAMES[code] ?? code.toUpperCase();
}

export async function detectLanguages(url: string, fetcher: HttpFetcher): Promise<DetectedLanguage[]> {
  let body: string;
  try {
    const resp = await fetcher.get(url);
    if (resp.status !== 200) {
      return [{ code: 'en', name: 'English' }];
    }
    body = resp.body;
  } catch {
    return [{ code: 'en', name: 'English' }];
  }

  const found = new Map<string, DetectedLanguage>();

  // 1. Parse hreflang link tags
  const hreflangRegex = /hreflang="([^"]+)"\s+href="([^"]+)"/g;
  let match: RegExpExecArray | null;
  while ((match = hreflangRegex.exec(body)) !== null) {
    const rawCode = match[1]!;
    const href = match[2]!;
    const code = rawCode.split('-')[0]!.toLowerCase();
    if (code === 'x') continue; // skip x-default
    if (!found.has(code)) {
      found.set(code, { code, name: languageName(code), urlPattern: href });
    }
  }

  // 2. Parse html lang attribute
  const htmlLangMatch = /\blang="([^"]+)"/.exec(body);
  if (htmlLangMatch) {
    const code = htmlLangMatch[1]!.split('-')[0]!.toLowerCase();
    if (!found.has(code)) {
      found.set(code, { code, name: languageName(code) });
    }
  }

  // 3. Fallback to English
  if (found.size === 0) {
    return [{ code: 'en', name: 'English' }];
  }

  return Array.from(found.values());
}
