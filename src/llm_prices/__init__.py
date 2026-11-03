"""LLM API list prices for OpenAI, Anthropic and Google models, with a token-cost calculator.

    >>> import llm_prices
    >>> llm_prices.cost("gpt-6.1-terra", input_tokens=2_000, output_tokens=300)
    0.0035

All prices are USD per million tokens, copied from each provider's pricing page.
The date they were checked is in ``llm_prices.CHECKED``.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from importlib import resources
from typing import Iterable, Optional, Union

__all__ = ["Rates", "Model", "CHECKED", "models", "get", "cost", "compare", "changes"]
__version__ = "2026.11.2"

DateLike = Union[date, str, None]


@dataclass(frozen=True)
class Rates:
    """USD per million tokens."""

    input: float
    cached_input: float
    output: float

    @classmethod
    def _from(cls, d: dict) -> "Rates":
        return cls(d["input"], d["cached_input"], d["output"])


@dataclass(frozen=True)
class Model:
    id: str
    provider: str
    name: str
    tier: str
    status: str
    standard: Rates
    batch: Rates
    cache_write: Optional[float]
    long_context_threshold: Optional[int]
    long_context: Optional[Rates]
    scheduled: tuple
    source_url: str
    checked: str

    def rates(self, *, batch: bool = False, on: DateLike = None) -> Rates:
        """Rates in force on a date (default: today), including announced price changes."""
        day = _day(on)
        current = self.batch if batch else self.standard
        for change in sorted(self.scheduled, key=lambda c: c["effective"]):
            if day >= date.fromisoformat(change["effective"]):
                key = "batch" if batch else "standard"
                if key in change:
                    current = Rates._from(change[key])
        return current

    def cost(self, input_tokens: int, output_tokens: int, cached_tokens: int = 0, *,
             batch: bool = False, on: DateLike = None) -> float:
        """USD cost of one request.

        ``input_tokens`` is the whole prompt, including ``cached_tokens`` (the part read from cache).
        Long-context rates apply to the whole request when the prompt exceeds the model's threshold.
        """
        if min(input_tokens, output_tokens, cached_tokens) < 0:
            raise ValueError("token counts cannot be negative")
        if cached_tokens > input_tokens:
            raise ValueError("cached_tokens is part of input_tokens and cannot exceed it")
        r = self.rates(batch=batch, on=on)
        if self.long_context and self.long_context_threshold and input_tokens > self.long_context_threshold:
            if batch:
                raise ValueError(f"{self.id}: batch pricing for prompts over {self.long_context_threshold:,} tokens "
                                 "is not listed in this dataset; check the provider's pricing page")
            if self.scheduled and r != self.standard:
                raise ValueError(f"{self.id}: long-context rates after an announced price change are not published")
            r = self.long_context
        usd = ((input_tokens - cached_tokens) * r.input + cached_tokens * r.cached_input + output_tokens * r.output) / 1e6
        return round(usd, 10)


def _day(on: DateLike) -> date:
    if on is None:
        return date.today()
    return date.fromisoformat(on) if isinstance(on, str) else on


def _load(name: str) -> dict:
    return json.loads(resources.files("llm_prices").joinpath("data", name).read_text(encoding="utf-8"))


_DATA = _load("prices.json")
CHECKED: str = _DATA["checked"]


def _model(d: dict) -> Model:
    p = d["pricing"]
    lc = p.get("long_context")
    return Model(
        id=d["id"], provider=d["provider"], name=d["name"], tier=d["tier"], status=d["status"],
        standard=Rates._from(p["standard"]), batch=Rates._from(p["batch"]), cache_write=p.get("cache_write"),
        long_context_threshold=lc["threshold_tokens"] if lc else None, long_context=Rates._from(lc["standard"]) if lc else None,
        scheduled=tuple(d.get("scheduled_changes", [])), source_url=d["source_url"], checked=d["checked"],
    )


_MODELS = {m["id"]: _model(m) for m in _DATA["models"]}


def models(provider: Optional[str] = None, tier: Optional[str] = None, include_legacy: bool = True) -> list:
    """All models, optionally filtered by provider ("OpenAI", "Anthropic", "Google") and tier ("flagship", "mid", "small")."""
    out = list(_MODELS.values())
    if provider:
        out = [m for m in out if m.provider.lower() == provider.lower()]
    if tier:
        out = [m for m in out if m.tier == tier.lower()]
    if not include_legacy:
        out = [m for m in out if m.status != "legacy"]
    return out


def get(model_id: str) -> Model:
    """A model by its API ID, e.g. ``"claude-sonnet-5-5"``."""
    try:
        return _MODELS[model_id]
    except KeyError:
        raise KeyError(f"unknown model {model_id!r}; known: {', '.join(sorted(_MODELS))}") from None


def cost(model_id: str, input_tokens: int, output_tokens: int, cached_tokens: int = 0, *,
         batch: bool = False, on: DateLike = None) -> float:
    """USD cost of one request on a model. See :meth:`Model.cost`."""
    return get(model_id).cost(input_tokens, output_tokens, cached_tokens, batch=batch, on=on)


def compare(input_tokens: int, output_tokens: int, cached_tokens: int = 0, *, batch: bool = False,
            on: DateLike = None, ids: Optional[Iterable[str]] = None) -> list:
    """(model, cost) pairs for the same request on every model, cheapest first. Models that cannot price it are skipped."""
    out = []
    for m in (get(i) for i in ids) if ids else models():
        try:
            out.append((m, m.cost(input_tokens, output_tokens, cached_tokens, batch=batch, on=on)))
        except ValueError:
            continue
    return sorted(out, key=lambda x: x[1])


def changes() -> list:
    """The price change log, newest first."""
    return _load("changes.json")["changes"]
