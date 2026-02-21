from pathlib import Path

import click

from kitchenowl_cli.api import ApiError
from kitchenowl_cli.commands import shoppinglist as shopping_mod


def test_remove_items_uses_bulk_endpoint(monkeypatch):
    calls: list[tuple[str, object]] = []

    class Client:
        def delete(self, path, json=None):
            calls.append((path, json))
            return {"msg": "DONE"}

    monkeypatch.setattr(shopping_mod, "_client_and_config", lambda: (Client(), {}))
    monkeypatch.setattr(shopping_mod.click, "confirm", lambda *args, **kwargs: True)
    monkeypatch.setattr(shopping_mod.console, "print", lambda *args, **kwargs: None)

    shopping_mod.remove_items.callback(12, (5, 6), 0, True, False)

    assert calls == [("/api/shoppinglist/12/items", {"items": [{"item_id": 5}, {"item_id": 6}]})]


def test_remove_items_falls_back_to_legacy_single_delete(monkeypatch):
    calls: list[tuple[str, object]] = []

    class Client:
        def delete(self, path, json=None):
            calls.append((path, json))
            if path.endswith("/items"):
                raise ApiError("Body dropped", 405)
            return {"msg": "DONE"}

    monkeypatch.setattr(shopping_mod, "_client_and_config", lambda: (Client(), {}))
    monkeypatch.setattr(shopping_mod.console, "print", lambda *args, **kwargs: None)

    shopping_mod.remove_items.callback(9, (1, 2), 0, True, False)

    assert calls == [
        ("/api/shoppinglist/9/items", {"items": [{"item_id": 1}, {"item_id": 2}]}),
        ("/api/shoppinglist/9/item", {"item_id": 1}),
        ("/api/shoppinglist/9/item", {"item_id": 2}),
    ]


def test_remove_items_does_not_fallback_on_semantic_400(monkeypatch):
    calls: list[tuple[str, object]] = []

    class Client:
        def delete(self, path, json=None):
            calls.append((path, json))
            raise ApiError("Invalid bulk payload", 400)

    monkeypatch.setattr(shopping_mod, "_client_and_config", lambda: (Client(), {}))
    monkeypatch.setattr(shopping_mod.click, "confirm", lambda *args, **kwargs: True)
    monkeypatch.setattr(shopping_mod.console, "print", lambda *args, **kwargs: None)

    try:
        shopping_mod.remove_items.callback(9, (1, 2), 0, True, False)
        raise AssertionError("Expected ClickException")
    except click.ClickException as exc:
        assert "Invalid bulk payload" in str(exc)

    assert calls == [("/api/shoppinglist/9/items", {"items": [{"item_id": 1}, {"item_id": 2}]})]


def test_clear_list_fetches_ids_then_bulk_removes(monkeypatch):
    calls: list[tuple[str, object]] = []

    class Client:
        def get(self, path, params=None):
            calls.append((path, params))
            return [{"id": 10}, {"id": 11}]

        def delete(self, path, json=None):
            calls.append((path, json))
            return {"msg": "DONE"}

    monkeypatch.setattr(shopping_mod, "_client_and_config", lambda: (Client(), {}))
    monkeypatch.setattr(shopping_mod.console, "print", lambda *args, **kwargs: None)

    shopping_mod.clear_list.callback(3, 0, True, False)

    assert calls[0] == ("/api/shoppinglist/3/items", None)
    assert calls[1] == (
        "/api/shoppinglist/3/items",
        {"items": [{"item_id": 10}, {"item_id": 11}]},
    )


def test_add_items_from_file_parses_json_entries(tmp_path, monkeypatch):
    payloads: list[dict[str, str]] = []
    file_path = tmp_path / "items.json"
    file_path.write_text('[\"Milk\", {\"name\": \"Bread\", \"description\": \"Whole grain\"}]', encoding="utf-8")

    class Client:
        def post(self, path, json=None):
            payloads.append(json)
            return {"msg": "ok"}

    monkeypatch.setattr(shopping_mod, "_client_and_config", lambda: (Client(), {}))
    monkeypatch.setattr(shopping_mod.console, "print", lambda *args, **kwargs: None)

    shopping_mod.add_items_from_file.callback(6, Path(file_path), False)

    assert payloads == [{"name": "Milk"}, {"name": "Bread", "description": "Whole grain"}]


def test_add_items_from_file_reports_invalid_json_as_click_error(tmp_path):
    file_path = tmp_path / "items.json"
    file_path.write_text('["Milk",}', encoding="utf-8")

    try:
        shopping_mod._load_bulk_items_file(file_path)
        raise AssertionError("Expected ClickException")
    except click.ClickException as exc:
        assert f"Invalid JSON in {file_path}:" in str(exc)


def test_add_items_from_file_reports_invalid_yaml_as_click_error(tmp_path):
    file_path = tmp_path / "items.yaml"
    file_path.write_text("name: [unclosed", encoding="utf-8")

    try:
        shopping_mod._load_bulk_items_file(file_path)
        raise AssertionError("Expected ClickException")
    except click.ClickException as exc:
        assert f"Invalid YAML in {file_path}:" in str(exc)
