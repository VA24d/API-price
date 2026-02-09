from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import requests


PRICING_URL = "https://bes-dev.github.io/openai-pricing-api/pricing.json"
MODELS_PATH = Path(__file__).resolve().parents[1] / "src" / "llm_price" / "data" / "models.json"
NOTES_TEXT = "OpenAI pricing from openai-pricing-api"


def _load_pricing() -> dict[str, Any]:
    response = requests.get(PRICING_URL, timeout=30)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("OpenAI pricing API response must be a JSON object")
    return data


def _load_models() -> list[dict[str, Any]]:
    return json.loads(MODELS_PATH.read_text(encoding="utf-8"))


def _write_models(models: list[dict[str, Any]]) -> None:
    MODELS_PATH.write_text(json.dumps(models, indent=2) + "\n", encoding="utf-8")


def _normalize_pricing(value: Any, field: str, model: str) -> str:
    if value is None:
        raise ValueError(f"Missing {field} pricing for {model}")
    try:
        normalized = Decimal(str(value)).normalize()
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field} pricing for {model}") from exc
    return format(normalized, "f")


def _normalize_pricing_optional(value: Any, field: str, model: str) -> str | None:
    if value is None:
        return None
    return _normalize_pricing(value, field, model)


def _merge_openai_models(
    models: list[dict[str, Any]], pricing: dict[str, Any]
) -> list[dict[str, Any]]:
    existing_release_dates = {
        item["model"].lower(): item.get("release_date")
        for item in models
        if item.get("provider") == "openai"
    }
    existing_notes = {
        item["model"].lower(): item.get("notes")
        for item in models
        if item.get("provider") == "openai"
    }

    openai_models: list[dict[str, Any]] = []
    for _, entry in pricing.items():
        if not isinstance(entry, dict):
            continue
        if entry.get("pricing_type") != "per_1m_tokens":
            continue
        model = entry.get("model")
        if not isinstance(model, str):
            continue
        lower_model = model.lower()
        openai_models.append(
            {
                "provider": "openai",
                "model": model,
                "release_date": existing_release_dates.get(lower_model),
                "pricing": {
                    "input_per_1m": _normalize_pricing(entry.get("input"), "input", model),
                    "cached_input_per_1m": _normalize_pricing_optional(
                        entry.get("cached_input"), "cached_input", model
                    ),
                    "output_per_1m": _normalize_pricing(entry.get("output"), "output", model),
                },
                "notes": existing_notes.get(lower_model) or NOTES_TEXT,
            }
        )

    non_openai = [item for item in models if item.get("provider") != "openai"]
    openai_models.sort(key=lambda item: item["model"].lower())
    return openai_models + non_openai


def main() -> None:
    pricing = _load_pricing()
    models = _load_models()
    updated = _merge_openai_models(models, pricing)
    _write_models(updated)


if __name__ == "__main__":
    main()