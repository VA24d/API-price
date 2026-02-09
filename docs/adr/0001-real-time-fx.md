# ADR 0001: Real-time FX via exchangerate.host

## Status
Accepted

## Context
The library previously required callers to supply a fixed FX rate whenever non-USD
output was requested. Users asked for a free and stable real-time option, with
minimal dependencies and operational overhead. The project already depends on
`requests` and favors simple, explicit data flows.

## Decision
Add a `get_fx_rate` helper that fetches the latest rate for any currency pair
from `https://api.exchangerate.host/latest` and caches it in-process for one
hour by default. When `currency != "USD"` and no `fx_rate` is supplied, pricing
functions now fetch and use the live rate. Callers can still pass a fixed rate
to override the live lookup.

## Consequences
- Conversions now work out-of-the-box with a live rate for any currency.
- Network access is required when non-USD output is requested without an override.
- Rates are cached to avoid repeated HTTP calls.
- Callers can disable caching or specify a custom TTL via `get_fx_rate`.