from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

CurrencyCode = str


@dataclass(frozen=True)
class Money:
    currency: CurrencyCode
    amount: Decimal


@dataclass(frozen=True)
class TokenPrice:
    input_per_1m: Decimal
    cached_input_per_1m: Decimal | None
    output_per_1m: Decimal


@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int