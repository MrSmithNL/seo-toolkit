// Result type — no naked `throw` (FF-032)

export interface Ok<T> {
  readonly success: true;
  readonly data: T;
}

export interface Err<E> {
  readonly success: false;
  readonly error: E;
}

export type Result<T, E = OperationError> = Ok<T> | Err<E>;

export function ok<T>(data: T): Ok<T> {
  return { success: true, data };
}

export function err<E>(error: E): Err<E> {
  return { success: false, error };
}

export interface OperationError {
  readonly type: string;
  readonly title: string;
  readonly status: number;
  readonly detail: string;
  readonly suggestedAction?: string;
}

export function operationError(fields: OperationError): OperationError {
  return Object.freeze(fields);
}
