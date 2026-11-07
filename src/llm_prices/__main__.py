"""Command line: ``llm-prices list | cost MODEL | compare``."""
from __future__ import annotations

import argparse
import sys

import llm_prices as lp


def _usd(x: float) -> str:
    if x >= 1:
        return f"${x:,.2f}"
    return f"${x:,.6f}".rstrip("0").rstrip(".") if x < 0.01 else f"${x:,.4f}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="llm-prices", description=f"LLM API prices (checked {lp.CHECKED}).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ls = sub.add_parser("list", help="list models and prices per million tokens")
    ls.add_argument("--provider")
    ls.add_argument("--tier", choices=["flagship", "mid", "small"])
    for name in ("cost", "compare"):
        p = sub.add_parser(name, help="price one request" if name == "cost" else "price one request on every model")
        if name == "cost":
            p.add_argument("model")
        p.add_argument("--input", type=int, required=True, help="prompt tokens, including cached tokens")
        p.add_argument("--output", type=int, required=True, help="output tokens")
        p.add_argument("--cached", type=int, default=0, help="prompt tokens read from cache")
        p.add_argument("--batch", action="store_true", help="use batch prices")
        p.add_argument("--on", help="date (YYYY-MM-DD) for announced price changes")
        p.add_argument("--requests", type=int, default=1, help="multiply by this many requests")
    a = ap.parse_args(argv)

    if a.cmd == "list":
        rows = lp.models(a.provider, a.tier)
        print(f"{'model':28} {'provider':10} {'tier':9} {'input':>8} {'cached':>8} {'output':>8}   USD / 1M tokens, checked {lp.CHECKED}")
        for m in rows:
            r = m.standard
            print(f"{m.id:28} {m.provider:10} {m.tier:9} {r.input:>8g} {r.cached_input:>8g} {r.output:>8g}")
        return 0
    try:
        if a.cmd == "cost":
            c = lp.cost(a.model, a.input, a.output, a.cached, batch=a.batch, on=a.on) * a.requests
            print(f"{a.model}: {_usd(c)}" + (f" for {a.requests:,} requests" if a.requests > 1 else ""))
        else:
            for m, c in lp.compare(a.input, a.output, a.cached, batch=a.batch, on=a.on):
                print(f"{m.id:28} {_usd(c * a.requests):>14}")
    except (KeyError, ValueError) as e:
        print(f"error: {e.args[0]}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
