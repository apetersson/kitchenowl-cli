from kitchenowl_cli.commands import recipe as recipe_mod


def test_search_recipes_uses_household_endpoint_and_params(monkeypatch):
    captured: dict[str, object] = {}

    class Client:
        def get(self, path, params=None):
            captured["path"] = path
            captured["params"] = params
            return []

    monkeypatch.setattr(
        recipe_mod,
        "load_config",
        lambda: {
            "server_url": "https://example.com",
            "access_token": "a",
            "refresh_token": "r",
            "default_household": 7,
        },
    )
    monkeypatch.setattr(recipe_mod, "ApiClient", lambda cfg: Client())
    monkeypatch.setattr(recipe_mod.console, "print", lambda *args, **kwargs: None)

    recipe_mod.search_recipes.callback(None, "soup", 2, "en", False, False)

    assert captured["path"] == "/api/household/7/recipe/search"
    assert captured["params"] == {"query": "soup", "page": 2, "only_ids": False, "language": "en"}


def test_search_recipes_by_tag_uses_global_endpoint(monkeypatch):
    captured: dict[str, object] = {}

    class Client:
        def get(self, path, params=None):
            captured["path"] = path
            captured["params"] = params
            return []

    monkeypatch.setattr(
        recipe_mod,
        "load_config",
        lambda: {"server_url": "https://example.com", "access_token": "a", "refresh_token": "r"},
    )
    monkeypatch.setattr(recipe_mod, "ApiClient", lambda cfg: Client())
    monkeypatch.setattr(recipe_mod.console, "print", lambda *args, **kwargs: None)

    recipe_mod.search_recipes_by_tag.callback("vegan", 1, "de", False)

    assert captured["path"] == "/api/recipe/search-tag"
    assert captured["params"] == {"tag": "vegan", "page": 1, "language": "de"}
