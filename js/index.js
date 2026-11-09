// LLM API list prices (USD per million tokens) and a token cost calculator.
// Prices are copied from each provider's pricing page; the date checked is exported as CHECKED.
import { readFileSync } from "node:fs";

const read = (name) => JSON.parse(readFileSync(new URL(`./data/${name}`, import.meta.url), "utf8"));
const DATA = read("prices.json");

export const CHECKED = DATA.checked;

const rates = (d) => ({ input: d.input, cachedInput: d.cached_input, output: d.output });

const toDay = (on) => {
  if (on === undefined || on === null) return new Date().toISOString().slice(0, 10);
  return on instanceof Date ? on.toISOString().slice(0, 10) : String(on).slice(0, 10);
};

function makeModel(d) {
  const p = d.pricing;
  const lc = p.long_context;
  const model = {
    id: d.id, provider: d.provider, name: d.name, tier: d.tier, status: d.status,
    standard: rates(p.standard), batch: rates(p.batch),
    cacheWrite: p.cache_write ?? null,
    longContextThreshold: lc ? lc.threshold_tokens : null,
    longContext: lc ? rates(lc.standard) : null,
    scheduledChanges: d.scheduled_changes ?? [],
    sourceUrl: d.source_url, checked: d.checked,
    // Rates in force on a date (default today), including announced price changes.
    rates({ batch = false, on } = {}) {
      const day = toDay(on);
      let current = batch ? model.batch : model.standard;
      const key = batch ? "batch" : "standard";
      for (const c of [...model.scheduledChanges].sort((a, b) => a.effective.localeCompare(b.effective))) {
        if (day >= c.effective && c[key]) current = rates(c[key]);
      }
      return current;
    },
    // USD cost of one request. inputTokens is the whole prompt, including cachedTokens.
    cost(inputTokens, outputTokens, cachedTokens = 0, { batch = false, on } = {}) {
      if (Math.min(inputTokens, outputTokens, cachedTokens) < 0) throw new RangeError("token counts cannot be negative");
      if (cachedTokens > inputTokens) throw new RangeError("cachedTokens is part of inputTokens and cannot exceed it");
      let r = model.rates({ batch, on });
      if (model.longContext && model.longContextThreshold && inputTokens > model.longContextThreshold) {
        if (batch) throw new RangeError(`${model.id}: batch pricing for prompts over ${model.longContextThreshold} tokens is not listed in this dataset`);
        if (model.scheduledChanges.length && r !== model.standard) throw new RangeError(`${model.id}: long-context rates after an announced price change are not published`);
        r = model.longContext;
      }
      const usd = ((inputTokens - cachedTokens) * r.input + cachedTokens * r.cachedInput + outputTokens * r.output) / 1e6;
      return Math.round(usd * 1e10) / 1e10;
    },
  };
  return model;
}

const MODELS = new Map(DATA.models.map((m) => [m.id, makeModel(m)]));

export function models({ provider, tier, includeLegacy = true } = {}) {
  let out = [...MODELS.values()];
  if (provider) out = out.filter((m) => m.provider.toLowerCase() === provider.toLowerCase());
  if (tier) out = out.filter((m) => m.tier === tier.toLowerCase());
  if (!includeLegacy) out = out.filter((m) => m.status !== "legacy");
  return out;
}

export function get(id) {
  const m = MODELS.get(id);
  if (!m) throw new RangeError(`unknown model "${id}"; known: ${[...MODELS.keys()].sort().join(", ")}`);
  return m;
}

export const cost = (id, inputTokens, outputTokens, cachedTokens = 0, opts) => get(id).cost(inputTokens, outputTokens, cachedTokens, opts);

// The same request on every model, cheapest first. Models that cannot price it are skipped.
export function compare(inputTokens, outputTokens, cachedTokens = 0, { batch = false, on, ids } = {}) {
  const list = ids ? ids.map(get) : models();
  const out = [];
  for (const m of list) {
    try { out.push({ model: m, cost: m.cost(inputTokens, outputTokens, cachedTokens, { batch, on }) }); } catch (e) { if (!(e instanceof RangeError)) throw e; }
  }
  return out.sort((a, b) => a.cost - b.cost);
}

export const changes = () => read("changes.json").changes;
