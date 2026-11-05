# AiGanak LLM Cost MCP server

Ask your AI assistant what an LLM workload will cost, which model is cheapest for it, and how much more the same text costs in Hindi, German or Japanese, using current, sourced prices for OpenAI, Anthropic and Google models.

Works with any MCP client: Claude Desktop, Claude Code, Cursor, VS Code, Windsurf and others. No API key, no account.

## Tools

| Tool | What it answers |
|---|---|
| `list_models` | Current models with standard, cached-input and batch prices per million tokens |
| `get_model_price` | Full pricing for one model: cache writes, long-context surcharges, announced price changes, source page |
| `estimate_cost` | Cost of N requests on one model, with caching, batch and future-dated prices |
| `compare_models` | The same workload priced on every model, cheapest first |
| `token_tax` | How many more tokens a language takes than English, per model family (22 languages) |
| `estimate_text_cost` | Tokens and cost for a piece of text in any measured language, script detected automatically |
| `price_changes` | Dated, sourced log of LLM API price changes |

Example questions:

- *"What will 50,000 requests of 6,000 input tokens (4,000 cached) and 500 output cost on Claude Sonnet 5.5 vs GPT-6.1 Sol?"*
- *"Which model is cheapest for a Tamil support bot?"*
- *"What does Gemini 4 Argon cost per request after its December price change?"*

## Install

Requires Node.js 18 or later.

**Claude Desktop**: add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aiganak-llm-cost": { "command": "npx", "args": ["-y", "@aiganak/llm-cost-mcp"] }
  }
}
```

**Claude Code**:

```bash
claude mcp add aiganak-llm-cost -- npx -y @aiganak/llm-cost-mcp
```

**Cursor**: add the same `mcpServers` entry to `~/.cursor/mcp.json`.

**From source** (no npm needed):

```bash
git clone https://github.com/AiGanak/llm-prices && cd llm-prices/mcp && npm install
# then use: "command": "node", "args": ["/path/to/llm-prices/mcp/index.js"]
```

## Data

Prices, the price change log and the token tax index come from [AiGanak/llm-prices](https://github.com/AiGanak/llm-prices) (CC BY 4.0). The server fetches the latest data at start-up and falls back to the copy bundled with the package if it is offline (set `LLM_PRICES_OFFLINE=1` to always use the bundled copy). Prices are checked weekly against each provider's own pricing page; the token tax is re-measured monthly with each provider's official token counter.

Prices change. Confirm on the provider's page before committing to a budget.

## About

Built by [AiGanak](https://aiganak.com). We help teams cut LLM spend without losing quality: free tools at [aiganak.com/tools](https://aiganak.com/tools/), the [LLM Cost Report](https://aiganak.com/llm-cost-report/) and [cost audits](https://aiganak.com/llm-cost-audit/).
