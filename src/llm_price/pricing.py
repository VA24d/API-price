from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Literal

from llm_price.currency import convert_money
from llm_price.data import get_model_info
from llm_price.tokens import estimate_tokens
from llm_price.types import Money, TokenPrice, TokenUsage


@dataclass(frozen=True)
class CostBreakdown:
    prompt_cost: Money
    completion_cost: Money
    total_cost: Money
    usage: TokenUsage
    notes: str | None = None


def _calc_cost(amount: Decimal, currency: Literal["USD", "INR"]) -> Money:
    return Money(currency=currency, amount=amount)


def _ensure_positive_tokens(prompt_tokens: int, completion_tokens: int) -> None:
    if prompt_tokens < 0 or completion_tokens < 0:
        raise ValueError("Token counts must be non-negative")


def cost_from_tokens(
    provider: str,
    model: str,
    *,
    prompt_tokens: int,
    completion_tokens: int,
    currency: Literal["USD", "INR"] = "USD",
    fx_usd_to_inr: Decimal | None = None,
) -> CostBreakdown:
    """Compute cost from explicit token counts."""
    _ensure_positive_tokens(prompt_tokens, completion_tokens)
    info = get_model_info(provider, model)
    token_price = info.pricing
    prompt_cost = (Decimal(prompt_tokens) / Decimal(1_000_000)) * token_price.input_per_1m
    completion_cost = (
        Decimal(completion_tokens) / Decimal(1_000_000)
    ) * token_price.output_per_1m
    total_cost = prompt_cost + completion_cost

    money_prompt = _calc_cost(prompt_cost, "USD")
    money_completion = _calc_cost(completion_cost, "USD")
    money_total = _calc_cost(total_cost, "USD")
    if currency == "INR":
        money_prompt = convert_money(money_prompt, "INR", fx_usd_to_inr)
        money_completion = convert_money(money_completion, "INR", fx_usd_to_inr)
        money_total = convert_money(money_total, "INR", fx_usd_to_inr)

    usage = TokenUsage(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)
    return CostBreakdown(
        prompt_cost=money_prompt,
        completion_cost=money_completion,
        total_cost=money_total,
        usage=usage,
    )


def cost_from_text(
    provider: str,
    model: str,
    *,
    prompt: str,
    completion: str | None = None,
    currency: Literal["USD", "INR"] = "USD",
    fx_usd_to_inr: Decimal | None = None,
) -> CostBreakdown:
    """Compute cost from prompt/completion text by estimating tokens."""
    usage, note = estimate_tokens(provider, model, prompt=prompt, completion=completion)
    breakdown = cost_from_tokens(
        provider,
        model,
        prompt_tokens=usage.prompt_tokens,
        completion_tokens=usage.completion_tokens,
        currency=currency,
        fx_usd_to_inr=fx_usd_to_inr,
    )
    if note:
        return CostBreakdown(
            prompt_cost=breakdown.prompt_cost,
            completion_cost=breakdown.completion_cost,
            total_cost=breakdown.total_cost,
            usage=breakdown.usage,
            notes=note,
        )
    return breakdown


def sum_cost(records: Iterable[CostBreakdown | dict]) -> Money:
    """Sum total costs from CostBreakdown objects or dicts with 'total_cost'."""
    total = Decimal("0")
    currency: Literal["USD", "INR"] | None = None
    for record in records:
        if isinstance(record, CostBreakdown):
            amount = record.total_cost.amount
            record_currency = record.total_cost.currency
        else:
            total_cost = record.get("total_cost")
            if not isinstance(total_cost, Money):
                raise ValueError("Record must contain total_cost Money")
            amount = total_cost.amount
            record_currency = total_cost.currency

        if currency is None:
            currency = record_currency
        if record_currency != currency:
            raise ValueError("All records must use the same currency")
        total += amount

    if currency is None:
        raise ValueError("No records provided")
    return Money(currency=currency, amount=total)