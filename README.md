# LLM API Prices

[![CI](https://github.com/AiGanak/llm-prices/actions/workflows/ci.yml/badge.svg)](https://github.com/AiGanak/llm-prices/actions/workflows/ci.yml)
[![Data: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-1f6feb)](LICENSE-DATA)
[![Code: MIT](https://img.shields.io/badge/code-MIT-1f6feb)](LICENSE)
[![Prices checked](https://img.shields.io/badge/prices%20checked-weekly-2ea44f)](CHANGELOG.md)

Up-to-date list prices for the OpenAI, Anthropic and Google Gemini APIs. Every price is a machine-readable record copied from the provider's own pricing page, with its source and the date it was checked.

- **One dataset, four ways to use it:** an MCP server for AI assistants ([`mcp/`](mcp/)), plus [`data/prices.json`](data/prices.json) (with a [JSON Schema](schema/prices.schema.json)), [`data/prices.csv`](data/prices.csv), and a dependency-free Python package.
- **Everything that changes the bill:** standard, cached-input and batch rates, cache-write prices, long-context surcharges and announced future price changes.
- **History:** a dated snapshot for every check in [`data/snapshots/`](data/snapshots/), and a sourced [price change log](data/changes.json).

Maintained by [AiGanak](https://aiganak.com). The same data powers the free [LLM API pricing calculator](https://aiganak.com/llm-api-pricing/) and the [LLM price change log](https://aiganak.com/llm-price-changes/).

## Current prices

<!-- prices:start -->
| Model | Provider | Tier | Input | Cached input | Output | Batch input | Batch output |
|---|---|---|--:|--:|--:|--:|--:|
| [Claude Fable 5.1](https://platform.claude.com/docs/en/about-claude/pricing)<br>`claude-fable-5-1` | Anthropic | Flagship | $10 | $0.25 | $50 | $5 | $25 |
| [Claude Opus 5.5](https://platform.claude.com/docs/en/about-claude/pricing)<br>`claude-opus-5-5` | Anthropic | Flagship | $4 | $0.20 | $20 | $2 | $10 |
| [Gemini 3.1 Pro (preview)](https://ai.google.dev/gemini-api/docs/pricing)<br>`gemini-3.1-pro-preview` | Google | Flagship | $2 | $0.20 | $12 | $1 | $6 |
| [Gemini 4 Argon](https://ai.google.dev/gemini-api/docs/pricing)<br>`gemini-4-argon` | Google | Flagship | $2 | $0.10 | $10 ¹ | $1 | $5 |
| [GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)<br>`gpt-6-astra` | OpenAI | Flagship | $10 | $1 | $50 | $5 | $25 |
| [Claude Sonnet 5.5](https://platform.claude.com/docs/en/about-claude/pricing)<br>`claude-sonnet-5-5` | Anthropic | Mid | $2 | $0.10 | $10 | $1 | $5 |
| [Gemini 3.8 Flash](https://ai.google.dev/gemini-api/docs/pricing)<br>`gemini-3.8-flash` | Google | Mid | $0.75 | $0.075 | $3.75 ¹ | $0.375 | $1.875 |
| [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol)<br>`gpt-6.1-sol` | OpenAI | Mid | $2 | $0.10 | $10 | $1 | $5 |
| [GPT-6.1 Terra](https://developers.openai.com/api/docs/models/gpt-6.1-terra)<br>`gpt-6.1-terra` | OpenAI | Mid | $1 | $0.05 | $5 | $0.50 | $2.50 |
| [Claude Haiku 4.5](https://platform.claude.com/docs/en/about-claude/pricing) *(legacy)*<br>`claude-haiku-4-5` | Anthropic | Small | $1 | $0.10 | $5 | $0.50 | $2.50 |
| [Claude Haiku 5.5](https://platform.claude.com/docs/en/about-claude/pricing)<br>`claude-haiku-5-5` | Anthropic | Small | $0.10 | $0.01 | $0.50 | $0.05 | $0.25 |
| [Gemini 3.5 Flash-Lite](https://ai.google.dev/gemini-api/docs/pricing)<br>`gemini-3.5-flash-lite` | Google | Small | $0.30 | $0.03 | $2.50 | $0.15 | $1.25 |
| [Gemini 3.1 Flash-Lite](https://ai.google.dev/gemini-api/docs/pricing)<br>`gemini-3.1-flash-lite` | Google | Small | $0.25 | $0.025 | $1.50 | $0.125 | $0.75 |
| [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna)<br>`gpt-6-luna` | OpenAI | Small | $0.10 | $0.01 | $0.50 | $0.05 | $0.25 |

USD per million tokens, standard tier, text. Checked 2026-11-02.

¹ Announced price change: Gemini 4 Argon: $4 input / $20 output from 2026-12-01; Gemini 3.8 Flash: $1.50 input / $7.50 output from 2027-01-01.
<!-- prices:end -->

Per-model detail, worked examples and head-to-head comparisons: [aiganak.com/llm-api-pricing](https://aiganak.com/llm-api-pricing/).

## Language token tax

The same text costs a different number of tokens in each language, and every model family tokenizes differently. [`data/token-tax/`](data/token-tax/) holds a 12-message business corpus in English and 22 other languages, the official token counts per model, and the [counting script](scripts/count_tokens.py). Selected results (tokens as a multiple of English on the same model, measured 4 November 2026):

| Language | OpenAI GPT-6 | Claude 5.x | Gemini 3.x | Gemini 4 Argon |
|---|--:|--:|--:|--:|
| Hindi | 1.43× | 2.28× | 1.18× | 1.28× |
| Tamil | 1.91× | 3.21× | 1.36× | 1.65× |
| Kannada | 1.89× | 6.38× | 1.82× | 2.05× |
| Odia | 4.85× | 5.33× | 3.37× | 2.29× |
| German | 1.25× | 1.99× | 1.29× | 1.27× |
| Chinese | 1.03× | 1.01× | 0.96× | 0.90× |

Full index for 23 languages, with a free checker for your own text: [aiganak.com/language-token-tax](https://aiganak.com/language-token-tax/).

## Quick start

### Use the JSON directly

No install needed. Fetch the latest file from GitHub or the jsDelivr CDN:

```bash
curl -s https://raw.githubusercontent.com/AiGanak/llm-prices/main/data/prices.json
curl -s https://cdn.jsdelivr.net/gh/AiGanak/llm-prices@main/data/prices.json
```

```js
const res = await fetch("https://cdn.jsdelivr.net/gh/AiGanak/llm-prices@main/data/prices.json");
const { models } = await res.json();
const terra = models.find((m) => m.id === "gpt-6.1-terra");
console.log(terra.pricing.standard); // { input: 1, cached_input: 0.05, output: 5 }
```

Pin a dated version for reproducible results: `.../llm-prices@v2026.11.02/data/prices.json`.

### Python

[![PyPI](https://img.shields.io/pypi/v/aiganak-llm-prices)](https://pypi.org/project/aiganak-llm-prices/)

```bash
pip install aiganak-llm-prices
```

```python
import llm_prices

# Cost of one request: 6,000 prompt tokens (4,000 read from cache) and a 500-token answer
llm_prices.cost("claude-sonnet-5-5", input_tokens=6_000, output_tokens=500, cached_tokens=4_000)
# 0.0094

# Half price for work that can wait
llm_prices.cost("gpt-6.1-sol", 20_000, 800, batch=True)

# Prices on a future date, including announced changes
llm_prices.cost("gemini-4-argon", 2_000, 300, on="2026-12-01")

# The same request on every model, cheapest first
for model, usd in llm_prices.compare(input_tokens=2_000, output_tokens=300)[:5]:
    print(f"{model.name:28} ${usd:.5f}")
```

The package has no dependencies and works offline: the data ships inside it. `llm_prices.CHECKED` tells you when the prices were last checked.

### Command line

```console
$ llm-prices list --provider anthropic
$ llm-prices cost claude-opus-5-5 --input 20000 --output 800 --requests 100000
$ llm-prices compare --input 2000 --output 300 --cached 1500
```

### In your AI assistant (MCP server)

Ask Claude, Cursor or any MCP client what a workload costs, which model is cheapest, or what the token tax is for a language. See [`mcp/`](mcp/) for the server and setup:

```json
{ "mcpServers": { "aiganak-llm-cost": { "command": "npx", "args": ["-y", "@aiganak/llm-cost-mcp"] } } }
```

## Data format

Each model record in `data/prices.json`:

```json
{
  "id": "gpt-6-astra",
  "provider": "OpenAI",
  "name": "GPT-6 Astra",
  "tier": "flagship",
  "status": "active",
  "pricing": {
    "standard": { "input": 10, "cached_input": 1, "output": 50 },
    "batch": { "input": 5, "cached_input": 0.5, "output": 25 },
    "cache_write": 12.5,
    "long_context": {
      "threshold_tokens": 272000,
      "standard": { "input": 20, "cached_input": 2, "output": 75 },
      "note": "Prompts over 272K input tokens cost 2x input and cache rates and 1.5x output for the whole request."
    }
  },
  "scheduled_changes": [],
  "source_url": "https://developers.openai.com/api/docs/models/gpt-6-astra",
  "checked": "2026-11-02"
}
```

| Field | Meaning |
|---|---|
| `id` | The provider's API model ID, as used in requests. |
| `tier` | `flagship`, `mid` or `small`, for like-for-like comparison across providers. |
| `status` | `active`, `preview` or `legacy` (previous generation, still available). |
| `pricing.standard` | Pay-as-you-go list price in USD per million tokens. `cached_input` is the price of input tokens read from the prompt cache. |
| `pricing.batch` | Asynchronous batch price (results within 24 hours). |
| `pricing.cache_write` | Price to write tokens to the shortest-lived prompt cache, where the provider charges for it. |
| `pricing.long_context` | Rates that apply to the **whole request** when the prompt is longer than `threshold_tokens`. |
| `scheduled_changes` | Announced future prices and the date they take effect. |
| `source_url` | The provider page the prices were copied from. |

The full contract is [`schema/prices.schema.json`](schema/prices.schema.json) (JSON Schema 2020-12). Breaking changes to the format bump `schema_version` and are announced in the [changelog](CHANGELOG.md).

## Methodology

1. **Primary sources only.** Every price is copied by hand from the provider's own pricing or model page, never from third-party aggregators. Each record links to its source.
2. **Checked weekly**, and the same day a provider announces a change. Each check updates `checked`, adds a snapshot in `data/snapshots/`, and tags a release (`vYYYY.MM.DD`).
3. **Validated in CI.** Every change must pass the JSON Schema, unit tests for the cost calculator, and a check that the CSV, package data and this README were regenerated from the JSON.
4. **Scope.** Text tokens on the standard (pay-as-you-go) tier. Regional endpoints, priority tiers, enterprise discounts, image, audio and tool fees (such as web search) are not included. Cache storage fees (Gemini) are noted in the change log but not modelled.

Prices can change at any time. Always confirm on the provider's page before making a purchasing decision.

## Get notified when prices change

- **Watch** this repository (Custom → Releases) to get an email for every new dated release.
- Or sign up for [free LLM price change alerts](https://aiganak.com/llm-price-alerts/): one email when a provider changes a price, nothing else.

## Contributing

Spotted a price that has changed? [Open an issue](https://github.com/AiGanak/llm-prices/issues/new?template=price-change.yml) with a link to the provider's page. Pull requests should edit `data/prices.json` (and `data/changes.json`), then run:

```bash
python scripts/build.py
python -m pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Citation

If you use this dataset in research or a publication, please cite it (GitHub's **Cite this repository** button uses [CITATION.cff](CITATION.cff)):

```bibtex
@misc{aiganak_llm_prices,
  title  = {LLM API Prices: list prices for OpenAI, Anthropic and Google models},
  author = {{AiGanak}},
  year   = {2026},
  url    = {https://github.com/AiGanak/llm-prices}
}
```

## License

- **Data** (`data/`, `schema/`): [Creative Commons Attribution 4.0](LICENSE-DATA). Use it anywhere, including commercially, with a link back to this repository or [aiganak.com/llm-api-pricing](https://aiganak.com/llm-api-pricing/).
- **Code** (`src/`, `scripts/`, `tests/`): [MIT](LICENSE).

Model and company names are trademarks of their owners. This project is independent and not affiliated with OpenAI, Anthropic or Google.

## About AiGanak

[AiGanak](https://aiganak.com) is an AI systems studio. We help teams cut LLM spend without losing quality: free tools like the [LLM Bill Analyzer](https://aiganak.com/llm-bill-analyzer/) and [self-host vs API calculator](https://aiganak.com/self-host-vs-api-calculator/), a fixed-price [LLM Cost Report](https://aiganak.com/llm-cost-report/), and hands-on [cost audits](https://aiganak.com/llm-cost-audit/). We also build [custom small language models](https://aiganak.com/services/custom-slm-development/) for private deployment.
