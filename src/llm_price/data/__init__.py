"""Bundled model metadata for llm-price."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from importlib import resources
from typing import Literal

from llm_price.types import TokenPrice


@dataclass(frozen=True)
class ModelInfo:
    provider: Literal["openai", "google"]
    model: str
    release_date: date | None
    pricing: TokenPrice
    notes: str | None


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def _load_models() -> list[ModelInfo]:
    raw = json.loads(resources.files("llm_price.data").joinpath("models.json").read_text())
    models: list[ModelInfo] = []
    for item in raw:
        pricing = TokenPrice(
            input_per_1m=Decimal(item["pricing"]["input_per_1m"]),
            output_per_1m=Decimal(item["pricing"]["output_per_1m"]),
        )
        models.append(
            ModelInfo(
                provider=item["provider"],
                model=item["model"],
                release_date=_parse_date(item.get("release_date")),
                pricing=pricing,
                notes=item.get("notes"),
            )
        )
    return models


_MODELS = _load_models()


def list_models(provider: str | None = None) -> list[ModelInfo]:
    if provider is None:
        return list(_MODELS)
    normalized = provider.lower()
    return [model for model in _MODELS if model.provider == normalized]


def get_model_info(provider: str, model: str) -> ModelInfo:
    normalized_provider = provider.lower()
    normalized_model = model.lower()
    for info in _MODELS:
        if info.provider == normalized_provider and info.model.lower() == normalized_model:
            return info
    raise ValueError(f"Unknown model '{model}' for provider '{provider}'")


__all__ = ["ModelInfo", "get_model_info", "list_models"]