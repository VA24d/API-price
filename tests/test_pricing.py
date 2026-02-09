from decimal import Decimal

from llm_price.pricing import cost_from_tokens, sum_cost


def test_cost_from_tokens_usd() -> None:
    breakdown = cost_from_tokens(
        "openai",
        "gpt-4o-mini",
        prompt_tokens=1_000_000,
        completion_tokens=1_000_000,
    )
    assert breakdown.total_cost.currency == "USD"
    assert breakdown.total_cost.amount == Decimal("0.75")


def test_cost_from_tokens_inr() -> None:
    breakdown = cost_from_tokens(
        "openai",
        "gpt-4o-mini",
        prompt_tokens=1_000_000,
        completion_tokens=0,
        currency="INR",
        fx_rate=Decimal("80"),
    )
    assert breakdown.total_cost.currency == "INR"
    assert breakdown.total_cost.amount == Decimal("12")


def test_sum_cost() -> None:
    first = cost_from_tokens(
        "openai",
        "gpt-4o-mini",
        prompt_tokens=1_000_000,
        completion_tokens=0,
    )
    second = cost_from_tokens(
        "openai",
        "gpt-4o-mini",
        prompt_tokens=0,
        completion_tokens=1_000_000,
    )
    total = sum_cost([first, second])
    assert total.amount == Decimal("0.75")