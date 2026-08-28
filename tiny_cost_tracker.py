import time
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any

@dataclass
class ModelPricing:
    input_1k: float
    output_1k: float

DEFAULT_PRICING = {
    "gpt-4o": ModelPricing(0.005, 0.015),
    "gpt-4o-mini": ModelPricing(0.00015, 0.0006),
    "claude-3-5-sonnet": ModelPricing(0.003, 0.015),
    "claude-3-haiku": ModelPricing(0.00025, 0.00125),
    "gemini-1.5-pro": ModelPricing(0.0035, 0.0105),
    "gemini-1.5-flash": ModelPricing(0.000075, 0.0003),
}

@dataclass
class CostEntry:
    timestamp: float
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class CostTracker:
    """
    Zero-dependency cost tracker for AI agents.
    Track tokens and spend across models with budgeting and persistence.
    """
    def __init__(self, budget: float = 1.0, pricing: Optional[Dict[str, ModelPricing]] = None, storage_path: Optional[str] = None):
        self.budget = budget
        self.pricing = pricing or DEFAULT_PRICING
        self.storage_path = storage_path
        self.entries: List[CostEntry] = []
        self.total_cost = 0.0
        
        if storage_path:
            self.load()

    def add(self, model: str, input_tokens: int, output_tokens: int, metadata: Optional[Dict[str, Any]] = None):
        price = self.pricing.get(model, ModelPricing(0.0, 0.0))
        cost = (input_tokens / 1000 * price.input_1k) + (output_tokens / 1000 * price.output_1k)
        
        entry = CostEntry(
            timestamp=time.time(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            metadata=metadata or {}
        )
        
        self.entries.append(entry)
        self.total_cost += cost
        
        if self.storage_path:
            self.save()
            
        if self.total_cost > self.budget:
            return {"allowed": False, "cost": cost, "total": self.total_cost, "over_budget": True}
        
        return {"allowed": True, "cost": cost, "total": self.total_cost, "over_budget": False}

    def get_stats(self):
        models = {}
        for e in self.entries:
            m = models.setdefault(e.model, {"cost": 0.0, "input": 0, "output": 0})
            m["cost"] += e.cost
            m["input"] += e.input_tokens
            m["output"] += e.output_tokens
            
        return {
            "total_cost": self.total_cost,
            "budget": self.budget,
            "remaining": max(0, self.budget - self.total_cost),
            "usage_percent": (self.total_cost / self.budget * 100) if self.budget > 0 else 0,
            "models": models,
            "entry_count": len(self.entries)
        }

    def save(self):
        if not self.storage_path: return
        with open(self.storage_path, 'w') as f:
            json.dump({
                "budget": self.budget,
                "total_cost": self.total_cost,
                "entries": [asdict(e) for e in self.entries]
            }, f, indent=2)

    def load(self):
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.budget = data.get("budget", self.budget)
                self.total_cost = data.get("total_cost", 0.0)
                self.entries = [CostEntry(**e) for e in data.get("entries", [])]
        except (FileNotFoundError, json.JSONDecodeError):
            pass

if __name__ == "__main__":
    tracker = CostTracker(budget=0.10)
    res = tracker.add("gpt-4o", 1000, 500)
    print(f"Added 1500 tokens: {res}")
    print(json.dumps(tracker.get_stats(), indent=2))
