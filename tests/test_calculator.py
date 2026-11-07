import pytest

import llm_prices as lp


def test_basic_cost():
    # 2,000 input x $1 + 300 output x $5, per million
    assert lp.cost("gpt-6.1-terra", 2_000, 300) == pytest.approx(0.0035)


def test_cached_tokens():
    # 2,000 uncached x $2 + 4,000 cached x $0.10 + 500 output x $10, per million
    assert lp.cost("claude-sonnet-5-5", 6_000, 500, cached_tokens=4_000) == pytest.approx(0.0094)


def test_batch_is_half_on_openai():
    std = lp.cost("gpt-6.1-sol", 20_000, 800)
    assert lp.cost("gpt-6.1-sol", 20_000, 800, batch=True) == pytest.approx(std / 2)


def test_long_context_applies_to_whole_request():
    m = lp.get("gpt-6-astra")
    r = m.long_context
    expected = (300_000 * r.input + 1_000 * r.output) / 1e6
    assert m.cost(300_000, 1_000) == pytest.approx(expected)
    assert m.cost(272_000, 1_000) == pytest.approx((272_000 * m.standard.input + 1_000 * m.standard.output) / 1e6)


def test_long_context_batch_is_refused():
    with pytest.raises(ValueError):
        lp.cost("gpt-6-astra", 300_000, 1_000, batch=True)


def test_scheduled_change():
    m = lp.get("gemini-4-argon")
    change = m.scheduled[0]
    before = m.rates(on="2026-11-30")
    after = m.rates(on=change["effective"])
    assert before == m.standard
    assert after.input == change["standard"]["input"]
    assert after.output == change["standard"]["output"]


def test_validation():
    with pytest.raises(ValueError):
        lp.cost("gpt-6.1-terra", 100, 10, cached_tokens=200)
    with pytest.raises(KeyError):
        lp.get("no-such-model")


def test_compare_sorted_and_complete():
    rows = lp.compare(2_000, 300, on="2026-11-02")
    costs = [c for _, c in rows]
    assert costs == sorted(costs)
    assert len(rows) == len(lp.models())


def test_filters_and_changes():
    assert {m.provider for m in lp.models(provider="anthropic")} == {"Anthropic"}
    assert all(m.tier == "small" for m in lp.models(tier="small"))
    assert lp.changes()[0]["date"] >= lp.changes()[-1]["date"]


def test_cli(capsys):
    from llm_prices.__main__ import main
    assert main(["cost", "gpt-6.1-terra", "--input", "2000", "--output", "300", "--requests", "1000"]) == 0
    assert "$3.50 for 1,000 requests" in capsys.readouterr().out
    assert main(["cost", "nope", "--input", "1", "--output", "1"]) == 2
