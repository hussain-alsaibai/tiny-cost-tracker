# tiny-cost-tracker

> Zero-dependency per-agent cost tracking with token budgeting.

Track model spend across your AI agent fleet — LLM calls, embeddings, tool invocations — with a simple API, built-in pricing for major models, and optional JSON persistence.

```python
from tiny_cost_tracker import CostTracker

tracker = CostTracker(budget=10.00)  # $10 budget

# Record an LLM call
result = tracker.add("gpt-4o", input_tokens=1250, output_tokens=340)
# {"allowed": True, "cost": 0.01135, "total": 0.01135, "over_budget": False}

# Check budget status
stats = tracker.get_stats()
print(f"Spent ${stats['total_cost']:.2f} of ${stats['budget']} budget")
# → "Spent $0.01 of $10.00 budget"
```

## Features

- **Built-in pricing** for GPT-4o, GPT-4o-mini, Claude 3.5 Sonnet, Claude 3 Haiku, Gemini Pro/Flash
- **Custom pricing** — pass your own model → $/1K tokens map
- **Hard budget enforcement** — `add()` reports when you cross the line
- **Per-model breakdown** — see which models are burning your budget
- **JSON persistence** — survive process restarts with `storage_path`
- **Metadata** — attach session IDs, agent names, task types to every entry
- **Zero dependencies** — stdlib only (dataclasses, json, time)

## Why

AI agents burn tokens fast. When you run a fleet of autonomous workers (bounty bots, background agents, code reviewers), you need to know:
- Which model is eating your budget?
- When should a sub-agent be throttled?
- Can I afford this eval run?

`tiny-cost-tracker` answers those with ~100 lines of stdlib Python. No vendor lock-in, no cloud, no external DB.

## API

| Method | Description |
|--------|-------------|
| `add(model, input_tokens, output_tokens, metadata=None)` | Record a call, check budget. Returns dict with cost + over_budget flag |
| `get_stats()` | Aggregate: total spend, per-model, usage %, entry count |
| `save()` / `load()` | Persist to JSON (auto if `storage_path` given) |
| `budget` | Settable property — adjust mid-run |

## Cost Formula

`cost = (input_tokens/1000 × input_1k) + (output_tokens/1000 × output_1k)`

All prices are **per 1K tokens**, USD. Override via the `pricing` kwarg:

```python
from tiny_cost_tracker import CostTracker, ModelPricing

custom = CostTracker(
    budget=5.0,
    pricing={
        "my-local-model": ModelPricing(input_1k=0.001, output_1k=0.002),
    }
)
```

## CLI Usage

```bash
python tiny_cost_tracker.py
# Added 1500 tokens: {'allowed': True, 'cost': 0.011, ...}
# {
#   "total_cost": 0.011,
#   "budget": 0.1,
#   "remaining": 0.089,
#   "usage_percent": 11.0,
#   ...
# }
```

## License

MIT — use it, ship it, forget it.
