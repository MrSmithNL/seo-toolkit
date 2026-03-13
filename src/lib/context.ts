// OperationContext — tenant-scoped request context

export interface OperationContext {
  readonly tenantId: string;
  readonly correlationId: string;
  readonly idempotencyKey?: string;
  readonly requestId?: string;
}

export function createOperationContext(
  tenantId: string,
  overrides: Partial<Omit<OperationContext, 'tenantId'>> = {},
): OperationContext {
  return {
    tenantId,
    correlationId: overrides.correlationId ?? crypto.randomUUID(),
    idempotencyKey: overrides.idempotencyKey,
    requestId: overrides.requestId,
  };
}
