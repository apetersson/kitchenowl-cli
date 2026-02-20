from kitchenowl_cli.commands import category as category_mod
from kitchenowl_cli.commands import tag as tag_mod


def test_category_list_uses_household_endpoint(monkeypatch):
    captured: dict[str, object] = {}

    class Client:
        def get(self, path, params=None):
            captured["path"] = path
            return []

    monkeypatch.setattr(category_mod, "_client_and_config", lambda: (Client(), {"default_household": 4}))
    monkeypatch.setattr(category_mod.console, "print", lambda *args, **kwargs: None)

    category_mod.list_categories.callback(None, False)

    assert captured["path"] == "/api/household/4/category"


def test_tag_list_uses_household_endpoint(monkeypatch):
    captured: dict[str, object] = {}

    class Client:
        def get(self, path, params=None):
            captured["path"] = path
            return []

    monkeypatch.setattr(tag_mod, "_client_and_config", lambda: (Client(), {"default_household": 7}))
    monkeypatch.setattr(tag_mod.console, "print", lambda *args, **kwargs: None)

    tag_mod.list_tags.callback(None, False)

    assert captured["path"] == "/api/household/7/tag"
