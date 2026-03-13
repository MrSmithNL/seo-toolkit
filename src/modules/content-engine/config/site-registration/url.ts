// URL normalisation — TASK-005
// F-001 US-001: Canonicalise user-entered URLs for storage.
// Algorithm from design spec §URL Normalisation.

import { type Result, ok, err, type OperationError, operationError } from '../../../../lib/result.js';

export function normaliseUrl(raw: string): Result<string, OperationError> {
  const trimmed = raw.trim();
  if (!trimmed) {
    return err(operationError({
      type: 'https://api.smithai.com/errors/validation',
      title: 'Invalid URL',
      status: 400,
      detail: 'URL cannot be empty',
      suggestedAction: 'Enter a domain like example.com',
    }));
  }

  // Step 1: Add https:// if no protocol
  let urlString = trimmed;
  if (!/^https?:\/\//i.test(urlString)) {
    urlString = `https://${urlString}`;
  }

  // Step 2: Parse with URL constructor
  let parsed: URL;
  try {
    parsed = new URL(urlString);
  } catch {
    return err(operationError({
      type: 'https://api.smithai.com/errors/validation',
      title: 'Invalid URL',
      status: 400,
      detail: 'Invalid URL format. Enter a domain like example.com',
      suggestedAction: 'Check the URL format',
    }));
  }

  // Reject empty hostname
  if (!parsed.hostname || parsed.hostname === '') {
    return err(operationError({
      type: 'https://api.smithai.com/errors/validation',
      title: 'Invalid URL',
      status: 400,
      detail: 'URL must contain a valid hostname',
      suggestedAction: 'Enter a domain like example.com',
    }));
  }

  // Step 3: Force https
  parsed.protocol = 'https:';

  // Step 4: Lowercase hostname (URL constructor already does this)
  // Step 5: Strip default ports
  if (parsed.port === '443' || parsed.port === '80') {
    parsed.port = '';
  }

  // Step 6: Strip fragment
  parsed.hash = '';

  // Step 7: Build normalised string
  let result = parsed.toString();

  // Strip trailing slash (only if it's the path-only slash)
  if (result.endsWith('/')) {
    result = result.slice(0, -1);
  }

  return ok(result);
}
