# Token tax corpus

The same 12 everyday business messages (support replies, refunds, appointments, invoices, password resets, shipping updates, opening hours, product copy, loan applications, fraud warnings and returns) in English and 22 other languages and scripts. Used to measure how many more tokens, and so how much more money, the same content costs in each language on each model.

| Region | Languages (file) |
|---|---|
| Baseline | English (`en`) |
| India | Hindi (`hi`), Hinglish in Latin script (`hi-Latn`), Bengali (`bn`), Marathi (`mr`), Telugu (`te`), Tamil (`ta`), Gujarati (`gu`), Kannada (`kn`), Malayalam (`ml`), Odia (`or`), Punjabi in Gurmukhi (`pa`), Urdu (`ur`) |
| Europe | German (`de`), French (`fr`), Spanish (`es`), Portuguese, Brazil (`pt`), Russian (`ru`) |
| Asia and Middle East | Japanese (`ja`), Chinese, Simplified (`zh`), Korean (`ko`), Arabic (`ar`), Indonesian (`id`) |

Each file has the same 12 lines in the same order. Numbers and times are kept in the form a native writer would use.

## Files

- `<lang>.txt`: the corpus.
- `tokenizers-<date>.json`: counts from public tokenizers that can be run offline.
- `results-<date>.json`: counts from each provider's official token-counting endpoint, produced by `scripts/count_tokens.py`.

## Method

Token tax for a language = tokens for that language's text ÷ tokens for the English text, on the same model. Message overhead added by the counting endpoints is removed before dividing. See `scripts/count_tokens.py`.

Translations were written by AiGanak for this corpus. Corrections from native speakers are welcome as issues or pull requests.

Licence: CC BY 4.0, like the rest of `data/`.

## Open-weight models

`open-weights-<date>.json` holds token counts for open-weight models you can host yourself (Qwen, DeepSeek, Llama 3, Gemma 3, Mistral Nemo and Sarvam-M), counted locally with each model's published Hugging Face tokenizer, raw text without a chat template. Run `python3 scripts/count_open_tokens.py` to reproduce. Sarvam-M uses the same tokenizer as Mistral, so its counts are identical. `index.json` includes these under `open_weights`, separate from the API-measured models.
