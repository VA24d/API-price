from __future__ import annotations

from decimal import Decimal

from llm_price import cost_from_tokens


def main() -> None:
    breakdown = cost_from_tokens(
        "google",
        "gemini-1.5-flash",
        prompt_tokens=1200,
        completion_tokens=400,
        currency="INR",
        fx_usd_to_inr=Decimal("83.12"),
    )
    print("Total cost (INR):", breakdown.total_cost)


if __name__ == "__main__":
    main()