import click

from kitchenowl_cli.commands import planner as planner_mod


def test_date_to_epoch_ms_conversion():
    value = planner_mod._date_to_epoch_ms("2026-02-20")
    assert value == 1771545600000


def test_date_to_epoch_ms_invalid_value():
    try:
        planner_mod._date_to_epoch_ms("20-02-2026")
        raise AssertionError("Expected ClickException")
    except click.ClickException as exc:
        assert "YYYY-MM-DD" in str(exc)


def test_add_recipe_uses_expected_endpoint_and_payload(monkeypatch):
    captured: dict[str, object] = {}

    class Client:
        def post(self, path, json=None):
            captured["path"] = path
            captured["json"] = json
            return {"msg": "ok"}

    monkeypatch.setattr(planner_mod, "_client_and_config", lambda: (Client(), {"default_household": 3}))
    monkeypatch.setattr(planner_mod.console, "print", lambda *args, **kwargs: None)

    planner_mod.add_recipe.callback(42, None, "2026-02-20", 6, False)

    assert captured["path"] == "/api/household/3/planner/recipe"
    assert captured["json"] == {"recipe_id": 42, "cooking_date": 1771545600000, "yields": 6}


def test_recent_recipes_uses_page_endpoint(monkeypatch):
    captured: dict[str, object] = {}

    class Client:
        def get(self, path):
            captured["path"] = path
            return []

    monkeypatch.setattr(planner_mod, "_client_and_config", lambda: (Client(), {"default_household": 9}))
    monkeypatch.setattr(planner_mod.console, "print", lambda *args, **kwargs: None)

    planner_mod.recent_recipes.callback(None, 2, False)

    assert captured["path"] == "/api/household/9/planner/recent-recipes/2"


def test_refresh_suggestions_calls_refresh_endpoint(monkeypatch):
    captured: dict[str, object] = {}

    class Client:
        def get(self, path):
            captured["path"] = path
            return []

    monkeypatch.setattr(planner_mod, "_client_and_config", lambda: (Client(), {"default_household": 5}))
    monkeypatch.setattr(planner_mod.console, "print", lambda *args, **kwargs: None)

    planner_mod.refresh_suggestions.callback(None, False)

    assert captured["path"] == "/api/household/5/planner/refresh-suggested-recipes"
