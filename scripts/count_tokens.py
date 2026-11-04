"""Measure the "token tax": how many tokens the same text costs in each language, per model,
using each provider's official token-counting endpoint.

    export ANTHROPIC_API_KEY=...   # optional, any provider without a key is skipped
    export ANTHROPIC_WORKSPACE_ID=... # only if your Anthropic key is not scoped to a workspace
    export GEMINI_API_KEY=...
    export OPENAI_API_KEY=...
    python3 scripts/count_tokens.py

Keys are read from the environment only and never written anywhere.
Output: data/token-tax/results-<date>.json (raw counts) and a summary table on screen.
Standard library only; no install needed.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "token-tax"

MODELS = {
    "Anthropic": ["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5", "claude-fable-5-1"],
    "OpenAI": ["gpt-6-astra", "gpt-6.1-sol", "gpt-6.1-terra", "gpt-6-luna"],
    "Google": ["gemini-4-argon", "gemini-3.1-pro-preview", "gemini-3.8-flash", "gemini-3.5-flash-lite"],
}
KEYS = {"Anthropic": "ANTHROPIC_API_KEY", "OpenAI": "OPENAI_API_KEY", "Google": "GEMINI_API_KEY"}


def post(url: str, body: dict, headers: dict) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"content-type": "application/json", **headers})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 529) and attempt < 4:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}") from None
        except urllib.error.URLError as e:
            if "CERTIFICATE_VERIFY_FAILED" in str(e.reason):
                sys.exit("Python cannot verify HTTPS certificates. On a Mac with Python from python.org, run once:\n"
                         f'  open "/Applications/Python {sys.version_info.major}.{sys.version_info.minor}/Install Certificates.command"\n'
                         "then run this script again.")
            raise RuntimeError(f"network error: {e.reason}") from None
    raise RuntimeError("unreachable")


def count(provider: str, model: str, text: str, key: str) -> int:
    if provider == "Anthropic":
        r = post("https://api.anthropic.com/v1/messages/count_tokens",
                 {"model": model, "messages": [{"role": "user", "content": text}]},
                 {"x-api-key": key, "anthropic-version": "2023-06-01",
                  **({"anthropic-workspace-id": os.environ["ANTHROPIC_WORKSPACE_ID"]} if os.environ.get("ANTHROPIC_WORKSPACE_ID") else {})})
        return r["input_tokens"]
    if provider == "OpenAI":
        r = post("https://api.openai.com/v1/responses/input_tokens", {"model": model, "input": text},
                 {"authorization": f"Bearer {key}"})
        return r["input_tokens"]
    r = post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:countTokens",
             {"contents": [{"parts": [{"text": text}]}]}, {"x-goog-api-key": key})
    return r["totalTokens"]


def main() -> int:
    only = set(sys.argv[1:])  # optional: provider names to run, e.g. Anthropic
    langs = sorted(p.stem for p in CORPUS.glob("*.txt"))
    texts = {l: (CORPUS / f"{l}.txt").read_text(encoding="utf-8").strip() for l in langs}
    out = {"date": date.today().isoformat(), "corpus": "data/token-tax/*.txt", "method":
           "Official count endpoint per model. Each language's 12 lines are sent as one user message; "
           "message overhead is removed by subtracting count('x') - 1.", "models": {}}
    for provider, models in MODELS.items():
        if only and provider not in only:
            continue
        key = os.environ.get(KEYS[provider])
        if not key:
            print(f"- {provider}: no {KEYS[provider]} set, skipped")
            continue
        for model in models:
            try:
                overhead = count(provider, model, "x", key) - 1
            except RuntimeError as e:
                print(f"- {model}: skipped ({e})")
                continue
            counts = {}
            for l in langs:
                counts[l] = count(provider, model, texts[l], key) - overhead
                time.sleep(0.15)
            out["models"][model] = {"provider": provider, "overhead": overhead, "tokens": counts}
            en = counts["en"]
            worst = max(counts, key=counts.get)
            print(f"- {model}: en {en} tokens; highest {worst} {counts[worst] / en:.2f}x")
    if not out["models"]:
        print("No models measured. Set at least one API key.")
        return 1
    path = CORPUS / (f"results-{out['date']}" + ("-" + "-".join(sorted(only)).lower() if only else "") + ".json")
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nSaved {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
