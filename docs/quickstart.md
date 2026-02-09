# Quickstart

```python
from llm_price import cost_from_text, get_fx_rate

breakdown = cost_from_text(
    "openai",
    "gpt-4o-mini",
    prompt="Hello",
    completion="Hi",
    currency="EUR",
)
print(breakdown.total_cost)

live_fx = get_fx_rate("USD", "EUR")
print(live_fx)
```

## Release (PyPI)

Publishing is handled by GitHub Actions with trusted publishing. After you
configure the PyPI Trusted Publisher, create a tag and push it:

```bash
git tag v0.1.0
git push origin v0.1.0
```