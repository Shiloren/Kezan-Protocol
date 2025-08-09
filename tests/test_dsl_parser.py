import pytest

from kezan.dsl import parse_rules, validate_rules, DSLParseError


def test_parse_simple_rule_and_validate_ok():
    text = (
        'RULE "flip"\n'
        'WHEN price < p50_30d*0.75 AND vol_7d > 800\n'
        'THEN RECOMMEND_BUY(qty=10, target=p50_7d*0.98, eta_h=36); ALERT("flip","ok")\n'
        'WITH PRIORITY=90, ENABLED=true\n'
    )
    rules = parse_rules(text)
    assert len(rules) == 1
    r = rules[0]
    assert r.name == "flip"
    assert "price < p50_30d*0.75" in r.condition
    assert len(r.actions) == 2
    assert r.actions[0].name == "RECOMMEND_BUY"
    assert r.metadata.get("PRIORITY") == 90
    issues = validate_rules(rules)
    assert issues == []


def test_parse_rejects_prohibited_actions():
    text = (
        'RULE "bad"\n'
        'WHEN TRUE\n'
        'THEN BUY(qty=1)\n'
    )
    rules = parse_rules(text)
    issues = validate_rules(rules)
    assert any("Acción prohibida" in x for x in issues)


def test_parse_invalid_structure():
    with pytest.raises(DSLParseError):
        parse_rules('WHEN TRUE\nTHEN ALERT("x","y")')
