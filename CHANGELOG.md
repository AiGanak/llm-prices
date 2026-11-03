# Changelog

Data releases are tagged `vYYYY.MM.DD` (the date prices were checked). The Python package uses the same date as its version.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2026.11.02] - 2026-11-02

First public release.

### Added
- 14 models: OpenAI (GPT-6 Astra, GPT-6.1 Sol, GPT-6.1 Terra, GPT-6 Luna), Anthropic (Claude Fable 5.1, Claude Opus 5.5, Claude Sonnet 5.5, Claude Haiku 5.5, Claude Haiku 4.5) and Google (Gemini 4 Argon, Gemini 3.1 Pro preview, Gemini 3.8 Flash, Gemini 3.5 Flash-Lite, Gemini 3.1 Flash-Lite).
- Standard, cached-input, batch, cache-write and long-context rates, with announced price changes for Gemini 4 Argon (1 December 2026) and Gemini 3.8 Flash (1 January 2027).
- `data/prices.json`, `data/prices.csv`, `data/changes.json`, JSON Schemas and the first snapshot.
- Python package `llm_prices` with `cost()`, `compare()`, `models()` and the `llm-prices` command line tool.

[2026.11.02]: https://github.com/AiGanak/llm-prices/releases/tag/v2026.11.02
