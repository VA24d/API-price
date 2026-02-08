from __future__ import annotations

from llm_price import cost_from_text


def main() -> None:
    breakdown = cost_from_text(
        "openai",
        "gpt-4o-mini",
        prompt="Summarize this text.",
        completion="Here is a summary...",
    )
    print("Prompt tokens:", breakdown.usage.prompt_tokens)
    print("Completion tokens:", breakdown.usage.completion_tokens)
    print("Total cost:", breakdown.total_cost)


if __name__ == "__main__":
    main()