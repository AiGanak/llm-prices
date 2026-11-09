# @aiganak/llm-prices

LLM API list prices for OpenAI, Anthropic and Google models (USD per million tokens) with a token cost calculator. No dependencies, Node 18+.

```js
import { cost, compare, get } from "@aiganak/llm-prices";

cost("gpt-6.1-terra", 2000, 300);              // 0.0035
cost("claude-sonnet-5-5", 50_000, 1_000, 40_000); // 40,000 of the 50,000 input tokens read from cache
compare(3000, 400)[0].model.name;               // cheapest model for this request
get("gemini-4-argon").rates({ on: "2026-12-01" }); // announced price changes apply on their date
```

`inputTokens` is the whole prompt, including cached tokens. Long-prompt rates apply to the whole request above a model's threshold. Every figure is copied from the provider's own pricing page; the date it was checked is `CHECKED`.

Data: [github.com/AiGanak/llm-prices](https://github.com/AiGanak/llm-prices) (CC-BY-4.0). Python: `pip install aiganak-llm-prices`. Live prices page: https://aiganak.com/llm-api-pricing/
