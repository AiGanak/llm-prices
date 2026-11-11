"""Measure the language token tax on open-weight models (Qwen, Llama, Gemma, Mistral, DeepSeek, Sarvam)
by counting tokens locally with each model's own published tokenizer. No API keys, no GPU.

    pip install tokenizers
    python3 scripts/count_open_tokens.py            # all models below
    python3 scripts/count_open_tokens.py Qwen/Qwen3-8B sarvamai/sarvam-m   # or chosen repos

Tokenizers are downloaded once from Hugging Face (public repositories only).
Output: data/token-tax/open-weights-<date>.json (kept apart from the API results-*.json files).
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "token-tax"

# Public (ungated) repositories that ship the model's own tokenizer.json.
MODELS = {
    "Qwen/Qwen3-8B": "Qwen (Alibaba)",
    "deepseek-ai/DeepSeek-V3": "DeepSeek",
    "unsloth/Llama-3.2-1B-Instruct": "Llama 3 (Meta)",
    "unsloth/gemma-3-4b-it": "Gemma 3 (Google)",
    "mistralai/Mistral-Nemo-Instruct-2407": "Mistral",
    "sarvamai/sarvam-m": "Sarvam (India)",
}


def main() -> int:
    try:
        from tokenizers import Tokenizer
    except ImportError:
        sys.exit("Run first:  pip install tokenizers")
    repos = sys.argv[1:] or list(MODELS)
    langs = sorted(p.stem for p in CORPUS.glob("*.txt"))
    texts = {l: (CORPUS / f"{l}.txt").read_text(encoding="utf-8").strip() for l in langs}
    out = {"date": date.today().isoformat(), "corpus": "data/token-tax/*.txt", "method":
           "Local count with each model's published Hugging Face tokenizer (tokenizer.json), raw text without chat template "
           "or special tokens. Each language's 12 lines counted as one text.", "models": {}}
    for repo in repos:
        try:
            tok = Tokenizer.from_pretrained(repo)
        except Exception as e:  # gated, renamed or offline
            print(f"- {repo}: skipped ({str(e).splitlines()[0][:120]})")
            continue
        counts = {l: len(tok.encode(texts[l], add_special_tokens=False).ids) for l in langs}
        out["models"][repo] = {"provider": "Open weights", "family": MODELS.get(repo, repo), "tokens": counts}
        worst = max(counts, key=counts.get)
        print(f"- {repo}: en {counts['en']} tokens; highest {worst} {counts[worst] / counts['en']:.2f}x")
    if not out["models"]:
        print("No tokenizers loaded. Check your internet connection to huggingface.co.")
        return 1
    path = CORPUS / f"open-weights-{out['date']}.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nSaved {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
