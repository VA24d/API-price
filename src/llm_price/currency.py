from __future__ import annotations

import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Final

import requests

from llm_price.types import CurrencyCode, Money


_EXCHANGE_RATE_HOST_URL: Final[str] = "https://api.exchangerate.host/latest"
_DEFAULT_CACHE_TTL_SECONDS: Final[int] = 60 * 60
_DEFAULT_TIMEOUT_SECONDS: Final[float] = 5.0


@dataclass(frozen=True)
class FxRateCache:
    base_currency: CurrencyCode
    target_currency: CurrencyCode
    rate: Decimal
    fetched_at: float


_FX_CACHE: FxRateCache | None = None


def _fetch_fx_rate(
    base_currency: CurrencyCode,
    target_currency: CurrencyCode,
    *,
    timeout_seconds: float,
) -> Decimal:
    response = requests.get(
        _EXCHANGE_RATE_HOST_URL,
        params={"base": base_currency, "symbols": target_currency},
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    payload = response.json()
    try:
        rate_value = payload["rates"][target_currency]
    except (KeyError, TypeError) as exc:
        raise ValueError("Unexpected FX response from exchangerate.host") from exc
    return Decimal(str(rate_value))


def get_fx_rate(
    base_currency: CurrencyCode,
    target_currency: CurrencyCode,
    *,
    cache_ttl_seconds: int = _DEFAULT_CACHE_TTL_SECONDS,
    timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
    use_cache: bool = True,
) -> Decimal:
    global _FX_CACHE
    now = time.time()
    if use_cache and _FX_CACHE is not None:
        if (
            _FX_CACHE.base_currency == base_currency
            and _FX_CACHE.target_currency == target_currency
            and now - _FX_CACHE.fetched_at < cache_ttl_seconds
        ):
            return _FX_CACHE.rate

    rate = _fetch_fx_rate(base_currency, target_currency, timeout_seconds=timeout_seconds)
    _FX_CACHE = FxRateCache(
        base_currency=base_currency,
        target_currency=target_currency,
        rate=rate,
        fetched_at=now,
    )
    return rate


def get_fx_usd_to_inr(
    *,
    cache_ttl_seconds: int = _DEFAULT_CACHE_TTL_SECONDS,
    timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
    use_cache: bool = True,
) -> Decimal:
    return get_fx_rate(
        "USD",
        "INR",
        cache_ttl_seconds=cache_ttl_seconds,
        timeout_seconds=timeout_seconds,
        use_cache=use_cache,
    )


def convert_money(
    money: Money,
    target_currency: CurrencyCode,
    fx_rate: Decimal | None,
) -> Money:
    if money.currency == target_currency:
        return money
    if fx_rate is None:
        raise ValueError("fx_rate is required for currency conversions")
    return Money(currency=target_currency, amount=money.amount * fx_rate)