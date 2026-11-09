import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import * as p from "./index.js";

test("data matches the canonical dataset", () => {
  const canon = JSON.parse(readFileSync(new URL("../data/prices.json", import.meta.url), "utf8"));
  const bundled = JSON.parse(readFileSync(new URL("./data/prices.json", import.meta.url), "utf8"));
  assert.deepEqual(bundled, canon);
  assert.equal(p.models().length, canon.models.length);
  assert.equal(p.CHECKED, canon.checked);
});

test("cost matches the Python package example", () => {
  assert.equal(p.cost("gpt-6.1-terra", 2000, 300), 0.0035);
});

test("cached tokens are part of input", () => {
  assert.equal(p.cost("claude-sonnet-5-5", 1_000_000, 0, 1_000_000), 0.1);
  assert.throws(() => p.cost("claude-sonnet-5-5", 10, 0, 11), RangeError);
});

test("batch is half of standard where listed", () => {
  assert.equal(p.cost("claude-sonnet-5-5", 1_000_000, 1_000_000, 0, { batch: true }), 6);
});

test("announced price change applies on its date", () => {
  const m = p.get("gemini-4-argon");
  assert.equal(m.rates({ on: "2026-11-30" }).input, 2);
  assert.equal(m.rates({ on: "2026-12-01" }).input, 4);
});

test("compare is sorted cheapest first; unknown model throws", () => {
  const r = p.compare(1000, 200);
  for (let i = 1; i < r.length; i++) assert.ok(r[i - 1].cost <= r[i].cost);
  assert.throws(() => p.get("nope"), RangeError);
  assert.ok(Array.isArray(p.changes()));
});
