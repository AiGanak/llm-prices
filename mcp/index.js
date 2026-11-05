#!/usr/bin/env node
// AiGanak LLM cost MCP server: current LLM API prices, cost estimates, model comparisons and the
// language token tax for OpenAI, Anthropic and Google models, from AiGanak's open data (CC BY 4.0).
// Data is fetched from GitHub (jsDelivr) at start-up and falls back to the copy bundled with this package.
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const CDN = "https://cdn.jsdelivr.net/gh/AiGanak/llm-prices@main/";
const FILES = { prices: "data/prices.json", changes: "data/changes.json", tax: "data/token-tax/index.json" };
const LOCAL = { prices: "data/prices.json", changes: "data/changes.json", tax: "data/token-tax.json" };
const OFFLINE = process.env.LLM_PRICES_OFFLINE === "1";

async function load(key) {
  if (!OFFLINE) {
    try {
      const r = await fetch(CDN + FILES[key], { signal: AbortSignal.timeout(4000) });
      if (r.ok) return { data: await r.json(), from: "live" };
    } catch { /* fall back to the bundled copy */ }
  }
  return { data: JSON.parse(readFileSync(join(HERE, LOCAL[key]), "utf8")), from: "bundled" };
}

const [P, C, T] = await Promise.all([load("prices"), load("changes"), load("tax")]);
const PRICES = P.data, CHANGES = C.data.changes, TAX = T.data;
const MODELS = Object.fromEntries(PRICES.models.map((m) => [m.id, m]));
const FOOTER = `\n\nSource: AiGanak open LLM price data (prices checked ${PRICES.checked}; token tax measured ${TAX.measured}), https://aiganak.com/llm-api-pricing/ · CC BY 4.0. Confirm on the provider's page before committing to a budget.`;

const LANGS = {
  en: "English", hi: "Hindi", "hi-Latn": "Hinglish (Latin script)", bn: "Bengali", mr: "Marathi", te: "Telugu", ta: "Tamil",
  gu: "Gujarati", kn: "Kannada", ml: "Malayalam", or: "Odia", pa: "Punjabi", ur: "Urdu", de: "German", fr: "French", es: "Spanish",
  pt: "Portuguese", ru: "Russian", ja: "Japanese", zh: "Chinese (Simplified)", ko: "Korean", ar: "Arabic", id: "Indonesian",
};
const ALIASES = Object.fromEntries(Object.entries(LANGS).flatMap(([c, n]) => [[c.toLowerCase(), c], [n.toLowerCase(), c], [n.toLowerCase().split(" ")[0], c]]));
ALIASES.hinglish = "hi-Latn"; ALIASES.chinese = "zh"; ALIASES.mandarin = "zh"; ALIASES.portuguese = "pt"; ALIASES.oriya = "or";
const lang = (s) => ALIASES[String(s || "").trim().toLowerCase()];

// Money: whole cents from $1 up; below $1 keep up to 6 decimals (exact list prices such as $0.075, small per-request costs).
const usd = (x) => {
  if (x >= 1) return "$" + x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const v = Math.round(x * 1e6) / 1e6, t = v.toFixed(6).replace(/0+$/, "");
  return "$" + (t.split(".")[1].length < 2 ? v.toFixed(2) : t);
};
const day = (s) => (s ? new Date(s + "T00:00:00Z") : new Date());

function findModel(id) {
  const k = String(id || "").trim().toLowerCase();
  if (MODELS[k]) return MODELS[k];
  const hit = PRICES.models.find((m) => m.name.toLowerCase() === k) || PRICES.models.find((m) => m.id.includes(k) || m.name.toLowerCase().includes(k));
  if (!hit) throw new Error(`Unknown model "${id}". Known: ${Object.keys(MODELS).join(", ")}`);
  return hit;
}

function rates(m, batch, on) {
  let r = batch ? m.pricing.batch : m.pricing.standard;
  for (const c of [...m.scheduled_changes].sort((a, b) => a.effective.localeCompare(b.effective))) {
    if (day(on) >= day(c.effective)) { const n = batch ? c.batch : c.standard; if (n) r = n; }
  }
  return r;
}

// Cost of one request in USD. inputTokens is the whole prompt, including cachedTokens.
function cost(m, inputTokens, outputTokens, cachedTokens = 0, batch = false, on) {
  if ([inputTokens, outputTokens, cachedTokens].some((x) => x < 0)) throw new Error("Token counts cannot be negative.");
  if (cachedTokens > inputTokens) throw new Error("cached_input_tokens is part of input_tokens and cannot exceed it.");
  let r = rates(m, batch, on), note = "";
  const lc = m.pricing.long_context;
  if (lc && inputTokens > lc.threshold_tokens) {
    if (batch) throw new Error(`${m.id}: batch pricing for prompts over ${lc.threshold_tokens.toLocaleString()} tokens is not listed in this dataset; check the provider's page.`);
    r = lc.standard; note = `Long-context rates apply (prompt over ${lc.threshold_tokens.toLocaleString()} tokens): ${lc.note || ""}`;
  }
  const usdIn = ((inputTokens - cachedTokens) * r.input + cachedTokens * r.cached_input) / 1e6, usdOut = (outputTokens * r.output) / 1e6;
  return { total: usdIn + usdOut, input: usdIn, output: usdOut, rates: r, note };
}

// Token tax: tokens of the same text in a language, as a multiple of English, on the same model.
function taxRow(modelId, code) {
  const t = TAX.models[modelId]?.tokens;
  return t ? t[code] / t.en : null;
}
function tokensPerChar(modelId, code) {
  const t = TAX.models[modelId]?.tokens;
  return t ? t[code] / TAX.chars[code] : null;
}
const SCRIPTS = [[/[଀-୿]/, "or"], [/[਀-੿]/, "pa"], [/[઀-૿]/, "gu"], [/[஀-௿]/, "ta"], [/[ఀ-౿]/, "te"],
  [/[ಀ-೿]/, "kn"], [/[ഀ-ൿ]/, "ml"], [/[ঀ-৿]/, "bn"], [/[ऀ-ॿ]/, "hi"], [/[぀-ヿ]/, "ja"],
  [/[가-힯]/, "ko"], [/[一-鿿]/, "zh"], [/[؀-ۿ]/, "ar"], [/[Ѐ-ӿ]/, "ru"]];
function detect(text) {
  for (const [re, c] of SCRIPTS) if (re.test(text)) return c === "hi" && /(आहे|आणि|तुम्ही|करा)/.test(text) ? "mr" : c === "ar" && /[ٹڈڑںے]/.test(text) ? "ur" : c;
  return "en";
}

const text = (s) => ({ content: [{ type: "text", text: s + FOOTER }] });
const fail = (e) => ({ isError: true, content: [{ type: "text", text: String(e.message || e) }] });
const row = (m) => { const s = m.pricing.standard, b = m.pricing.batch; return `${m.id.padEnd(24)} ${m.provider.padEnd(10)} ${m.tier.padEnd(9)} in ${usd(s.input)} · cached ${usd(s.cached_input)} · out ${usd(s.output)} · batch ${usd(b.input)}/${usd(b.output)}${m.scheduled_changes.length ? " · price change announced" : ""}${m.status !== "active" ? ` · ${m.status}` : ""}`; };

const server = new McpServer({ name: "aiganak-llm-cost", version: "2026.11.5" }, {
  instructions: "Current LLM API list prices (USD per million tokens) for OpenAI, Anthropic and Google models, request cost estimates and comparisons, and the language token tax (how many more tokens the same text takes in 22 languages vs English on each model). Data by AiGanak (aiganak.com), CC BY 4.0. Cite AiGanak and the check date when you quote figures.",
});

server.registerTool("list_models", {
  title: "List LLM models and prices",
  description: "List current OpenAI, Anthropic and Google API models with standard, cached-input and batch prices in USD per million tokens.",
  inputSchema: { provider: z.enum(["OpenAI", "Anthropic", "Google"]).optional(), tier: z.enum(["flagship", "mid", "small"]).optional() },
}, async ({ provider, tier }) => {
  const ms = PRICES.models.filter((m) => (!provider || m.provider === provider) && (!tier || m.tier === tier));
  return text(`USD per 1M tokens, standard tier, text. Checked ${PRICES.checked}.\n` + ms.map(row).join("\n"));
});

server.registerTool("get_model_price", {
  title: "Get one model's full pricing",
  description: "Full pricing for one model: standard, cached input, cache write, batch, long-context surcharge, announced future price changes and the provider's source page.",
  inputSchema: { model: z.string().describe("API model ID or name, e.g. gpt-6.1-terra or Claude Sonnet 5.5") },
}, async ({ model }) => {
  try {
    const m = findModel(model), p = m.pricing;
    const lines = [`${m.name} (${m.provider}, model ID ${m.id}, ${m.tier}${m.status !== "active" ? ", " + m.status : ""})`,
      `Standard: input ${usd(p.standard.input)}, cached input ${usd(p.standard.cached_input)}, output ${usd(p.standard.output)} per 1M tokens`,
      `Batch: input ${usd(p.batch.input)}, cached input ${usd(p.batch.cached_input)}, output ${usd(p.batch.output)}`];
    if (p.cache_write != null) lines.push(`Cache write (shortest lifetime): ${usd(p.cache_write)} per 1M tokens`);
    if (p.long_context) lines.push(`Over ${p.long_context.threshold_tokens.toLocaleString()} prompt tokens: input ${usd(p.long_context.standard.input)}, output ${usd(p.long_context.standard.output)} for the whole request. ${p.long_context.note || ""}`);
    for (const c of m.scheduled_changes) lines.push(`Announced: from ${c.effective}, input ${usd(c.standard.input)}, cached ${usd(c.standard.cached_input)}, output ${usd(c.standard.output)}`);
    lines.push(`Provider page: ${m.source_url} (checked ${m.checked})`, `Details: https://aiganak.com/llm-api-pricing/${m.id}/`);
    return text(lines.join("\n"));
  } catch (e) { return fail(e); }
});

const usage = {
  input_tokens: z.number().int().nonnegative().describe("Prompt tokens per request, including cached tokens"),
  output_tokens: z.number().int().nonnegative().describe("Output tokens per request, including any reasoning/thinking tokens"),
  cached_input_tokens: z.number().int().nonnegative().default(0).describe("Part of input_tokens read from the prompt cache"),
  requests: z.number().int().positive().default(1).describe("Number of requests to price"),
  batch: z.boolean().default(false).describe("Use asynchronous batch prices (results within 24 hours)"),
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional().describe("Price on this date (YYYY-MM-DD), including announced changes; default today"),
};

server.registerTool("estimate_cost", {
  title: "Estimate the cost of LLM requests",
  description: "Cost in USD of N requests on one model, with input/output breakdown, caching, batch, long-context surcharges and announced price changes.",
  inputSchema: { model: z.string(), ...usage },
}, async ({ model, input_tokens, output_tokens, cached_input_tokens, requests, batch, date }) => {
  try {
    const m = findModel(model), c = cost(m, input_tokens, output_tokens, cached_input_tokens, batch, date);
    return text([`${m.name}: ${usd(c.total * requests)} for ${requests.toLocaleString()} request${requests > 1 ? "s" : ""} (${usd(c.total)} each)`,
      `Input ${usd(c.input * requests)} · output ${usd(c.output * requests)} · rates used: input ${usd(c.rates.input)}, cached ${usd(c.rates.cached_input)}, output ${usd(c.rates.output)} per 1M${batch ? " (batch)" : ""}${date ? ` on ${date}` : ""}`,
      c.note].filter(Boolean).join("\n"));
  } catch (e) { return fail(e); }
});

server.registerTool("compare_models", {
  title: "Compare the same workload across models",
  description: "Price the same request on every model (optionally one provider or tier), cheapest first. Use to choose a model on cost before testing quality.",
  inputSchema: { ...usage, provider: z.enum(["OpenAI", "Anthropic", "Google"]).optional(), tier: z.enum(["flagship", "mid", "small"]).optional() },
}, async ({ input_tokens, output_tokens, cached_input_tokens, requests, batch, date, provider, tier }) => {
  const out = [], skipped = [];
  for (const m of PRICES.models.filter((m) => (!provider || m.provider === provider) && (!tier || m.tier === tier))) {
    try { out.push([m, cost(m, input_tokens, output_tokens, cached_input_tokens, batch, date).total * requests]); } catch { skipped.push(m.id); }
  }
  out.sort((a, b) => a[1] - b[1]);
  return text(`${requests.toLocaleString()} request(s) of ${input_tokens.toLocaleString()} input (${cached_input_tokens.toLocaleString()} cached) and ${output_tokens.toLocaleString()} output tokens${batch ? ", batch" : ""}:\n` +
    out.map(([m, v], i) => `${String(i + 1).padStart(2)}. ${m.name.padEnd(26)} ${usd(v)}`).join("\n") + (skipped.length ? `\nNot priced (no listed rate for this case): ${skipped.join(", ")}` : "") +
    "\nCheaper is only better if quality holds on your own examples.");
});

server.registerTool("token_tax", {
  title: "Language token tax",
  description: "How many more tokens the same text takes in a language than in English, on each measured model (OpenAI GPT-6, Claude 5.x, Gemini 3.x, Gemini 4 Argon). 22 languages incl. Hindi, Tamil, German, Japanese. Omit language to list all.",
  inputSchema: { language: z.string().optional().describe("Language name or code, e.g. Hindi, ta, German, Hinglish") },
}, async ({ language }) => {
  const ids = Object.keys(TAX.models);
  if (language) {
    const code = lang(language);
    if (!code || code === "en") return fail(new Error(`Unknown language "${language}". Measured: ${Object.values(LANGS).filter((n) => n !== "English").join(", ")}`));
    const lines = ids.map((id) => ({ id, r: taxRow(id, code), n: TAX.models[id].tokens[code] })).sort((a, b) => a.r - b.r)
      .map((x) => `${x.id.padEnd(24)} ${x.r.toFixed(2)}× English (${x.n} tokens vs ${TAX.models[x.id].tokens.en} for the same English text)`);
    return text(`${LANGS[code]}: tokens for the same 12 business messages, as a multiple of English on the same model (fewest first). You pay per token, so cost scales with this.\n` + lines.join("\n") +
      `\nIndex and checker: https://aiganak.com/language-token-tax/`);
  }
  const fam = [...new Map(ids.map((id) => [JSON.stringify(TAX.models[id].tokens), id])).values()];
  const head = "language".padEnd(26) + fam.map((id) => id.padStart(24)).join("");
  const rows = Object.keys(LANGS).filter((c) => c !== "en").map((c) => LANGS[c].slice(0, 25).padEnd(26) + fam.map((id) => (taxRow(id, c).toFixed(2) + "×").padStart(24)).join(""));
  return text(`Tokens as a multiple of English on the same model (one representative model per tokenizer family):\n${head}\n${rows.join("\n")}`);
});

server.registerTool("estimate_text_cost", {
  title: "Estimate tokens and cost for a text in any measured language",
  description: "Estimate how many tokens a text takes on a model and what N such messages cost as input or output, using measured tokens-per-character for its language. Detects the script if language is omitted.",
  inputSchema: {
    text: z.string().min(1), model: z.string(), language: z.string().optional(),
    messages: z.number().int().positive().default(1).describe("How many messages of this size"),
    as: z.enum(["input", "output"]).default("input"),
  },
}, async ({ text: t, model, language, messages, as }) => {
  try {
    const m = findModel(model);
    if (!TAX.models[m.id]) throw new Error(`No token measurements for ${m.id} yet. Measured: ${Object.keys(TAX.models).join(", ")}`);
    const code = language ? lang(language) : detect(t);
    if (!code) throw new Error(`Unknown language "${language}".`);
    const chars = [...t].length, tok = chars * tokensPerChar(m.id, code), r = rates(m, false);
    const price = as === "input" ? r.input : r.output, total = (tok * messages * price) / 1e6;
    return text(`${LANGS[code]}${language ? "" : " (detected)"} on ${m.name}: about ${Math.max(1, Math.round(tok)).toLocaleString()} tokens per message (${taxRow(m.id, code).toFixed(2)}× the same text in English).\n` +
      `${messages.toLocaleString()} message(s) as ${as}: about ${usd(total)} at ${usd(price)} per 1M ${as} tokens.\nEstimate from measured tokens per character; exact counts vary with wording.`);
  } catch (e) { return fail(e); }
});

server.registerTool("price_changes", {
  title: "Recent LLM API price changes",
  description: "Dated, sourced log of LLM API price changes and pricing announcements (newest first).",
  inputSchema: { limit: z.number().int().positive().max(50).default(10) },
}, async ({ limit }) => text(CHANGES.slice(0, limit).map((c) => `${c.date}${c.effective ? ` (effective ${c.effective})` : ""} · ${c.provider} · ${c.title}\n  ${c.detail}\n  ${c.source_url}`).join("\n") + "\nFull log: https://aiganak.com/llm-price-changes/"));

await server.connect(new StdioServerTransport());
