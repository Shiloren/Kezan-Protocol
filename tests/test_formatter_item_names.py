import kezan.formatter as formatter

def test_format_for_ai_resolves_names(monkeypatch):
    names = {100: "Foo", 200: "Bar", 300: "Baz"}

    def fake_resolver(item_id):
        return names[item_id]

    monkeypatch.setattr(formatter, "resolve_item_name", fake_resolver)
    items = [
        {"id": 100, "ah_price": 1.0, "avg_sell_price": 2.0, "margin": 0.1},
        {"id": 200, "ah_price": 3.0, "avg_sell_price": 4.0, "margin": 0.2},
        {"id": 300, "ah_price": 5.0, "avg_sell_price": 6.0, "margin": 0.3},
    ]

    formatted = formatter.format_for_ai(items)
    assert [item["name"] for item in formatted["items"]] == ["Foo", "Bar", "Baz"]
