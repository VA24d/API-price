from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal


@dataclass(frozen=True)
class Money:
    currency: Literal["USD", "INR"]
    amount: Decimal


@dataclass(frozen=True)
class TokenPrice:
    input_per_1m: Decimal
    output_per_1m: Decimal


@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int