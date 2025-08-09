import re

from kezan.compliance import sanitize_dsl_text, detect_prohibited_actions


def test_sanitize_replaces_buy_and_craft():
    text = "BUY(qty=1,target=100); CRAFT(qty=2,target=200)"
    out = sanitize_dsl_text(text)
    assert "RECOMMEND_BUY(" in out
    assert "RECOMMEND_CRAFT(" in out
    # No acciones prohibidas detectadas tras saneo
    assert detect_prohibited_actions(out) == []


def test_detects_other_prohibited_actions():
    text = "POST(listing); UNDERCUT(); AUTOBUY()"
    hits = detect_prohibited_actions(text)
    assert set(hits) >= {"POST", "UNDERCUT", "AUTOBUY"}
