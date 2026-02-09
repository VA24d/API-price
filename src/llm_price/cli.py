from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
import typer

from llm_price.data import list_models
from llm_price.pricing import Money, cost_from_text, cost_from_tokens, sum_cost
from llm_price.types import CurrencyCode


app = typer.Typer(no_args_is_help=True)


def _parse_currency(value: str) -> CurrencyCode:
    normalized = value.upper()
    if not normalized.isalpha() or len(normalized) != 3:
        raise typer.BadParameter("currency must be a 3-letter ISO code")
    return normalized


def _parse_decimal(value: str | None, option_name: str) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise typer.BadParameter(f"{option_name} must be a valid decimal") from exc


@app.command()
def models(provider: str | None = typer.Option(None, "--provider")) -> None:
    items = list_models(provider)
    for info in items:
        release = info.release_date.isoformat() if info.release_date else "unknown"
        typer.echo(
            f"{info.provider}:{info.model} release={release} "
            f"input_per_1m={info.pricing.input_per_1m} "
            f"output_per_1m={info.pricing.output_per_1m}"
        )


@app.command()
def cost(
    provider: str = typer.Option(..., "--provider"),
    model: str = typer.Option(..., "--model"),
    prompt: str | None = typer.Option(None, "--prompt"),
    completion: str | None = typer.Option(None, "--completion"),
    prompt_tokens: int | None = typer.Option(None, "--prompt-tokens"),
    completion_tokens: int | None = typer.Option(None, "--completion-tokens"),
    currency: str = typer.Option("USD", "--currency"),
    fx_rate: str | None = typer.Option(None, "--fx-rate"),
) -> None:
    parsed_currency = _parse_currency(currency)
    parsed_fx = _parse_decimal(fx_rate, "--fx-rate")
    if prompt is None and prompt_tokens is None:
        raise typer.BadParameter("Provide --prompt or --prompt-tokens")
    if prompt_tokens is not None:
        breakdown = cost_from_tokens(
            provider,
            model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens or 0,
            currency=parsed_currency,
            fx_rate=parsed_fx,
        )
    else:
        breakdown = cost_from_text(
            provider,
            model,
            prompt=prompt or "",
            completion=completion,
            currency=parsed_currency,
            fx_rate=parsed_fx,
        )
    typer.echo(
        json.dumps(
            {
                "prompt_cost": str(breakdown.prompt_cost.amount),
                "completion_cost": str(breakdown.completion_cost.amount),
                "total_cost": str(breakdown.total_cost.amount),
                "currency": breakdown.total_cost.currency,
                "prompt_tokens": breakdown.usage.prompt_tokens,
                "completion_tokens": breakdown.usage.completion_tokens,
                "notes": breakdown.notes,
            },
            indent=2,
        )
    )


@app.command()
def sum(
    file: Path = typer.Argument(..., exists=True),
) -> None:
    records = []
    with file.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            data = json.loads(line)
            if "total_cost" in data:
                total_cost = data.get("total_cost")
                if not isinstance(total_cost, dict):
                    raise typer.BadParameter("total_cost must be a dict with amount/currency")
                money = Money(
                    currency=_parse_currency(total_cost["currency"]),
                    amount=_parse_decimal(str(total_cost["amount"]), "total_cost.amount")
                    or Decimal("0"),
                )
                records.append({"total_cost": money})
                continue
            if "prompt" in data or "completion" in data:
                parsed_currency = _parse_currency(data.get("currency", "USD"))
                breakdown = cost_from_text(
                    data["provider"],
                    data["model"],
                    prompt=data.get("prompt", ""),
                    completion=data.get("completion"),
                    currency=parsed_currency,
                    fx_rate=(
                        _parse_decimal(str(data["fx_rate"]), "fx_rate")
                        if "fx_rate" in data
                        else None
                    ),
                )
                records.append(breakdown)
                continue
            parsed_currency = _parse_currency(data.get("currency", "USD"))
            breakdown = cost_from_tokens(
                data["provider"],
                data["model"],
                prompt_tokens=data.get("prompt_tokens", 0),
                completion_tokens=data.get("completion_tokens", 0),
                currency=parsed_currency,
                fx_rate=(
                    _parse_decimal(str(data["fx_rate"]), "fx_rate")
                    if "fx_rate" in data
                    else None
                ),
            )
            records.append(breakdown)
    total = sum_cost(records)
    typer.echo(json.dumps({"total": str(total.amount), "currency": total.currency}, indent=2))