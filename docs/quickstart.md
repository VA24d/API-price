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