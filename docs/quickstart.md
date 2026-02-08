# Quickstart

```python
from decimal import Decimal

from llm_price import cost_from_text

breakdown = cost_from_text(
    "openai",
    "gpt-4o-mini",
    prompt="Hello",
    completion="Hi",
    currency="INR",
    fx_usd_to_inr=Decimal("83.12"),
)
print(breakdown.total_cost)
```

## Release (PyPI)

Publishing is handled by GitHub Actions with trusted publishing. After you
configure the PyPI Trusted Publisher, create a tag and push it:

```bash
git tag v0.1.0
git push origin v0.1.0
```