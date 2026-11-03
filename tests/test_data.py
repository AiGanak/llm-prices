import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parent.parent
PRICES = json.loads((ROOT / "data/prices.json").read_text(encoding="utf-8"))
CHANGES = json.loads((ROOT / "data/changes.json").read_text(encoding="utf-8"))


def schema(name):
    return json.loads((ROOT / "schema" / name).read_text(encoding="utf-8"))


def test_prices_match_schema():
    jsonschema.validate(PRICES, schema("prices.schema.json"))


def test_changes_match_schema():
    jsonschema.validate(CHANGES, schema("changes.schema.json"))


def test_ids_unique():
    ids = [m["id"] for m in PRICES["models"]]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("m", PRICES["models"], ids=lambda m: m["id"])
def test_price_sanity(m):
    p = m["pricing"]
    for tier in ("standard", "batch"):
        r = p[tier]
        assert r["cached_input"] <= r["input"], "cached input should not cost more than input"
        assert r["output"] >= r["input"], "output is priced at or above input on every listed model"
    for k in ("input", "output"):
        assert p["batch"][k] <= p["standard"][k], "batch should not cost more than standard"
    if "long_context" in p:
        for k in ("input", "output"):
            assert p["long_context"]["standard"][k] >= p["standard"][k]
    assert m["checked"] <= PRICES["checked"]


def test_changes_newest_first():
    dates = [c["date"] for c in CHANGES["changes"]]
    assert dates == sorted(dates, reverse=True)


def test_snapshot_exists_for_current_check():
    assert (ROOT / "data/snapshots" / f"{PRICES['checked']}.json").exists()
