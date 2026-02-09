# ADR 0002: Daily OpenAI pricing sync

## Status
Accepted

## Context
OpenAI pricing changes frequently, and the library currently ships static
metadata in `src/llm_price/data/models.json`. Keeping these prices accurate
manually is error-prone. A public JSON feed is available at
https://bes-dev.github.io/openai-pricing-api/pricing.json and includes cached
input pricing for prompt caching.

## Decision
Add a lightweight sync script that fetches the OpenAI pricing feed daily via
GitHub Actions. The script updates only OpenAI entries while preserving existing
release dates and notes, and stores `cached_input_per_1m` alongside standard
input/output prices. The action auto-commits updated metadata to `main` when
changes occur.

## Consequences
- OpenAI pricing data stays current without manual edits.
- Cached input pricing is captured for prompt caching cost estimates.
- Non-OpenAI metadata remains unchanged.
- The repository will receive automated commits when prices change.