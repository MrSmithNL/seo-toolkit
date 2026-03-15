"""Generic Result type for business error handling.

Uses Ok/Err pattern instead of exceptions for expected business errors.
Mirrors the TypeScript Result<T, E> pattern for migration compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True)
class Ok(Generic[T]):  # noqa: UP046
    """Successful result containing a value."""

    value: T

    def is_ok(self) -> bool:
        """Return True if this is an Ok result."""
        return True

    def is_err(self) -> bool:
        """Return False if this is an Ok result."""
        return False


@dataclass(frozen=True)
class Err(Generic[E]):  # noqa: UP046
    """Error result containing an error value."""

    error: E

    def is_ok(self) -> bool:
        """Return False if this is an Err result."""
        return False

    def is_err(self) -> bool:
        """Return True if this is an Err result."""
        return True


Result = Ok[T] | Err[E]
