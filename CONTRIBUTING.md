# Contributing

Thank you for helping keep these prices accurate.

## Reporting a price change

[Open an issue](https://github.com/AiGanak/llm-prices/issues/new?template=price-change.yml) with:

- the model ID,
- the new price, and
- a link to the provider's **own** pricing or model page (we do not accept third-party sources).

We confirm every report against the provider's page before it is merged, usually within one working day.

## Pull requests

1. Edit `data/prices.json`. Update the model's `checked` date and the top-level `checked` date.
2. If a price changed or a model was added, add an entry at the top of `data/changes.json`.
3. Regenerate derived files and run the tests:

   ```bash
   pip install -e ".[dev]"
   python scripts/build.py
   python -m pytest
   ```

4. Commit `data/`, `src/llm_prices/data/` and `README.md` together.

Never edit `data/prices.csv`, `src/llm_prices/data/` or the README price table by hand: they are generated, and CI rejects files that do not match `data/prices.json`.

## Scope

In scope: text-token list prices on the standard tier for OpenAI, Anthropic and Google, including batch, caching and long-context rates. Out of scope for now: priority or regional tiers, negotiated discounts, image/audio/video pricing and tool fees. Suggestions for new providers are welcome as issues.
