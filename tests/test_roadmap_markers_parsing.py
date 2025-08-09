from pathlib import Path


def test_roadmap_contains_stages_and_compliance_markers():
    # Resolve repository root from this test file path
    root = Path(__file__).resolve().parents[1]
    roadmap = root / "docs" / "ROADMAP.md"
    assert roadmap.exists(), "ROADMAP.md no existe"
    text = roadmap.read_text(encoding="utf-8")
    # Ensure new metadata keys are present at least once
    assert "{stage:" in text
    assert "{compliance:" in text
    assert "Now (0–4 semanas)" in text or "Now (0-4 semanas)" in text
