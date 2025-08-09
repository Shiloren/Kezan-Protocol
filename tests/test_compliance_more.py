import logging
import pytest

from kezan.compliance import sanitize_dsl_text, detect_prohibited_actions, advisory_preamble


def test_sanitize_and_detect_prohibited_actions(caplog):
    with caplog.at_level(logging.WARNING):
        text = """
        BUY(3)
        craft(2)
        AUTOBUY(1)
        Something about RECOMMEND_BUY(5) should not match.
        """
        sanitized = sanitize_dsl_text(text)
        # BUY/CRAFT replaced to RECOMMEND_*
        assert "RECOMMEND_BUY(3)" in sanitized
        assert "RECOMMEND_CRAFT(2)" in sanitized
        # Warning should mention AUTOBUY
        assert any("AUTOBUY" in rec.message for rec in caplog.records)

    # Detect prohibited tokens should not flag RECOMMEND_BUY or text without '('
    hits = detect_prohibited_actions("RECOMMEND_BUY(1) BUY  CRAFT")
    assert hits == []


def test_advisory_preamble_has_core_terms():
    pre = advisory_preamble()
    # Contains allowed and prohibited hints
    assert "Modo asesor" in pre and "RECOMMEND_BUY" in pre and "AUTOBUY" in pre
