"""Regenerate every derived file from data/prices.json and data/changes.json.

    python scripts/build.py          # write files
    python scripts/build.py --check  # fail if any derived file is out of date (used in CI)
"""
from __future__ import annotations

import csv
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CHECK = "--check" in sys.argv


def out(path: Path, text: str, stale: list) -> None:
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return
    if CHECK:
        stale.append(str(path.relative_to(ROOT)))
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def usd(x: float) -> str:
    """$10, $0.20, $2.50, $0.075: whole dollars bare, otherwise at least two decimals."""
    if x == int(x):
        return f"${int(x)}"
    t = f"{x:.4f}".rstrip("0")
    return "$" + (t if len(t.split(".")[1]) >= 2 else t + "0")


def fmt(x) -> str:
    return "" if x is None else f"{x:g}"


def main() -> int:
    prices_text = (DATA / "prices.json").read_text(encoding="utf-8")
    changes_text = (DATA / "changes.json").read_text(encoding="utf-8")
    d = json.loads(prices_text)
    stale: list = []

    # 1. CSV: one row per model, flat columns.
    cols = ["id", "provider", "name", "tier", "status", "input", "cached_input", "output", "batch_input", "batch_cached_input",
            "batch_output", "cache_write", "long_context_threshold_tokens", "long_context_input", "long_context_output",
            "next_change_effective", "next_input", "next_output", "source_url", "checked"]
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(cols)
    for m in d["models"]:
        p, s, b = m["pricing"], m["pricing"]["standard"], m["pricing"]["batch"]
        lc = p.get("long_context") or {}
        nx = (m["scheduled_changes"] or [{}])[0]
        w.writerow([m["id"], m["provider"], m["name"], m["tier"], m["status"], fmt(s["input"]), fmt(s["cached_input"]), fmt(s["output"]),
                    fmt(b["input"]), fmt(b["cached_input"]), fmt(b["output"]), fmt(p.get("cache_write")),
                    lc.get("threshold_tokens", ""), fmt(lc.get("standard", {}).get("input")), fmt(lc.get("standard", {}).get("output")),
                    nx.get("effective", ""), fmt(nx.get("standard", {}).get("input")), fmt(nx.get("standard", {}).get("output")),
                    m["source_url"], m["checked"]])
    out(DATA / "prices.csv", buf.getvalue(), stale)

    # 2. Dated snapshot (history is never rewritten).
    snap = DATA / "snapshots" / f"{d['checked']}.json"
    if not snap.exists():
        out(snap, prices_text, stale)

    # 3. Package data.
    out(ROOT / "src/llm_prices/data/prices.json", prices_text, stale)
    out(ROOT / "src/llm_prices/data/changes.json", changes_text, stale)

    # 3b. Compact token tax index (for the CDN, the MCP server and other clients).
    tt_dir = DATA / "token-tax"
    res = sorted(tt_dir.glob("results-*.json"))
    if res:
        models = {}
        for f in res:
            models.update(json.loads(f.read_text(encoding="utf-8"))["models"])
        date = max(json.loads(f.read_text(encoding="utf-8"))["date"] for f in res)
        chars = {p.stem: len(p.read_text(encoding="utf-8").strip()) for p in sorted(tt_dir.glob("*.txt"))}
        idx = {"dataset": "language-token-tax", "publisher": d["publisher"], "license": "CC-BY-4.0", "measured": date,
               "method": "Same 12 business messages per language, official token-count endpoint per model, message overhead removed.",
               "url": "https://aiganak.com/language-token-tax/", "chars": chars,
               "models": {m: {"provider": v["provider"], "tokens": v["tokens"]} for m, v in sorted(models.items())},
               }
        ow = sorted(tt_dir.glob("open-weights-*.json"))
        if ow:  # open-weight tokenizers, counted locally; kept separate from the API-measured models
            o = json.loads(ow[-1].read_text(encoding="utf-8"))
            idx["open_weights"] = {"measured": o["date"], "method": o["method"],
                                   "models": {m: {"family": v["family"], "tokens": v["tokens"]} for m, v in sorted(o["models"].items())}}
        text = json.dumps(idx, ensure_ascii=False, indent=1) + "\n"
        out(tt_dir / "index.json", text, stale)
        out(ROOT / "mcp/data/token-tax.json", text, stale)
    out(ROOT / "mcp/data/prices.json", prices_text, stale)
    out(ROOT / "mcp/data/changes.json", changes_text, stale)
    out(ROOT / "js/data/prices.json", prices_text, stale)
    out(ROOT / "js/data/changes.json", changes_text, stale)

    # 4. README price table.
    rows = ["| Model | Provider | Tier | Input | Cached input | Output | Batch input | Batch output |", "|---|---|---|--:|--:|--:|--:|--:|"]
    order = {"flagship": 0, "mid": 1, "small": 2}
    for m in sorted(d["models"], key=lambda m: (order[m["tier"]], m["provider"], -m["pricing"]["standard"]["output"])):
        s, b = m["pricing"]["standard"], m["pricing"]["batch"]
        flag = " ¹" if m["scheduled_changes"] else ""
        name = f"[{m['name']}]({m['source_url']})" + (" *(legacy)*" if m["status"] == "legacy" else "")
        rows.append(f"| {name}<br>`{m['id']}` | {m['provider']} | {m['tier'].title()} | {usd(s['input'])} | {usd(s['cached_input'])} | {usd(s['output'])}{flag} | {usd(b['input'])} | {usd(b['output'])} |")
    notes = []
    for m in d["models"]:
        for c in m["scheduled_changes"]:
            n = c["standard"]
            notes.append(f"{m['name']}: {usd(n['input'])} input / {usd(n['output'])} output from {c['effective']}")
    table = "\n".join(rows) + "\n\nUSD per million tokens, standard tier, text. Checked " + d["checked"] + "."
    if notes:
        table += "\n\n¹ Announced price change: " + "; ".join(notes) + "."
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    a, z = "<!-- prices:start -->", "<!-- prices:end -->"
    new = readme[: readme.index(a) + len(a)] + "\n" + table + "\n" + readme[readme.index(z):]
    out(ROOT / "README.md", new, stale)

    if stale:
        print("Out of date (run python scripts/build.py):", *stale, sep="\n  ")
        return 1
    print("Derived files up to date." if CHECK else "Built.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
