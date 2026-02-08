from __future__ import annotations

from decimal import Decimal
from typing import Literal

from llm_price.types import Money


def convert_money(
    money: Money,
    target_currency: Literal["USD", "INR"],
    fx_usd_to_inr: Decimal | None,
) -> Money:
    if money.currency == target_currency:
        return money
    if target_currency == "INR":
        if fx_usd_to_inr is None:
            raise ValueError("fx_usd_to_inr is required for INR conversions")
        return Money(currency="INR", amount=money.amount * fx_usd_to_inr)
    raise ValueError(f"Unsupported conversion to {target_currency}")