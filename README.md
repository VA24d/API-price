# llm-price

Pricing + release metadata and cost estimation for LLMs (OpenAI + Google Gemini).

## Features

- Model metadata with release dates
- Static pricing in **USD per 1M tokens**
- Cost estimation from **token counts or raw text**
- Any currency output (real-time FX from exchangerate.host, cached)
- CLI for listing models and summing JSONL usage

## Install

```bash
pip install llm-price
```

## Quickstart (Python)

```python
from decimal import Decimal

from llm_price import cost_from_text, cost_from_tokens, get_fx_rate, list_models

models = list_models("openai")
print(models[0])

cost = cost_from_text(
    "openai",
    "gpt-4o-mini",
    prompt="Summarize this text.",
    completion="Here is a summary...",
)
print(cost.total_cost)

cost_in_inr = cost_from_tokens(
    "google",
    "gemini-1.5-flash",
    prompt_tokens=120,
    completion_tokens=40,
    currency="INR",
    fx_rate=Decimal("83.12"),
)
print(cost_in_inr.total_cost)

live_fx = get_fx_rate("USD", "INR")
print("Live USD→INR:", live_fx)
```

## CLI

```bash
llm-price models --provider openai

llm-price cost \
  --provider openai \
  --model gpt-4o-mini \
  --prompt "Hello" \
  --completion "Hi" \
  --currency USD

llm-price cost \
  --provider google \
  --model gemini-1.5-flash \
  --prompt-tokens 100 \
  --completion-tokens 20 \
  --currency INR \
  --fx-rate "83.12"
```

## JSONL Summation

`llm-price sum usage.jsonl` supports lines with:

### Token counts

```json
{"provider":"openai","model":"gpt-4o-mini","prompt_tokens":1200,"completion_tokens":400}
```

### Raw text (tokenized internally)

```json
{"provider":"openai","model":"gpt-4o-mini","prompt":"Hello","completion":"Hi"}
```

### Pre-computed totals

```json
{"total_cost":{"amount":"0.0123","currency":"USD"}}
```

## Example Scripts

Run these from the repo root after installing dependencies:

```bash
python examples/basic_cost.py
python examples/inr_conversion.py
python examples/sum_jsonl.py
```

## Notes

- Pricing data is stored in `src/llm_price/data/models.json` in **USD per 1M tokens**.
- For non-USD output, FX defaults to a real-time rate from exchangerate.host.
- You can override it with `fx_rate` to use a fixed rate.
- Rates are cached in-process for 1 hour by default.
- Gemini token counting uses the official CountTokens API when `GOOGLE_API_KEY` is set; otherwise it falls back to an approximation.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Release (PyPI)

This project uses GitHub Actions trusted publishing. Create a tag like `v0.1.0`
and push it to GitHub to trigger the publish workflow:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Configure the PyPI Trusted Publisher with:

- **PyPI Project Name**: `llm-price`
- **Owner**: `VA24d`
- **Repository name**: `API-price`
- **Workflow name**: `publish.yml`
- **Environment name**: `pypi`