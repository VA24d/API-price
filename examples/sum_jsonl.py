from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from llm_price import cost_from_text, cost_from_tokens, sum_cost
from llm_price.types import Money


def main() -> None:
    records = []
    for line in Path("examples/usage.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        if "total_cost" in data:
            total = data["total_cost"]
            records.append(
                {
                    "total_cost": Money(
                        currency=total["currency"],
                        amount=Decimal(total["amount"]),
                    )
                }
            )
            continue
        if "prompt" in data or "completion" in data:
            records.append(
                cost_from_text(
                    data["provider"],
                    data["model"],
                    prompt=data.get("prompt", ""),
                    completion=data.get("completion"),
                    currency=data.get("currency", "USD"),
                    fx_usd_to_inr=(
                        Decimal(data["fx_usd_to_inr"]) if "fx_usd_to_inr" in data else None
                    ),
                )
            )
            continue
        records.append(
            cost_from_tokens(
                data["provider"],
                data["model"],
                prompt_tokens=data.get("prompt_tokens", 0),
                completion_tokens=data.get("completion_tokens", 0),
                currency=data.get("currency", "USD"),
                fx_usd_to_inr=Decimal(data["fx_usd_to_inr"]) if "fx_usd_to_inr" in data else None,
            )
        )
    total = sum_cost(records)
    print("Total:", total)


if __name__ == "__main__":
    main()