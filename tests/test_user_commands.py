import click

from kitchenowl_cli.api import ApiError
from kitchenowl_cli.commands import user as user_mod


def test_client_and_config_wraps_api_error(monkeypatch):
    monkeypatch.setattr(user_mod, "load_config", lambda: {})

    class BrokenClient:
        def __init__(self, config):
            raise ApiError("No server configured")

    monkeypatch.setattr(user_mod, "ApiClient", BrokenClient)

    try:
        user_mod._client_and_config()
        raise AssertionError("Expected ClickException")
    except click.ClickException as exc:
        assert "No server configured" in str(exc)


def test_create_user_message_without_id_or_username(monkeypatch):
    class Client:
        def post(self, path, json=None):
            return {"status": "ok"}

    monkeypatch.setattr(user_mod, "_client_and_config", lambda: (Client(), {}))
    printed: list[str] = []
    monkeypatch.setattr(user_mod.console, "print", lambda message: printed.append(str(message)))

    user_mod.create_user.callback("alice", "Alice", "secret", None, False)

    assert printed == ["[green]Created user.[/green]"]
