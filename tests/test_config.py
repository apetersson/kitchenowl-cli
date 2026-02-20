import json

from kitchenowl_cli import config as config_mod


def test_load_config_returns_empty_for_malformed_json(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    path.write_text("{not-json", encoding="utf-8")
    monkeypatch.setattr(config_mod, "get_config_path", lambda: path)

    assert config_mod.load_config() == {}


def test_load_config_returns_empty_for_non_object(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(["not", "an", "object"]), encoding="utf-8")
    monkeypatch.setattr(config_mod, "get_config_path", lambda: path)

    assert config_mod.load_config() == {}


def test_load_config_sanitizes_invalid_key_types(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "server_url": 123,
                "access_token": ["bad"],
                "refresh_token": "refresh",
                "default_household": "42",
                "user": "invalid",
                "custom": {"k": "v"},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(config_mod, "get_config_path", lambda: path)

    loaded = config_mod.load_config()
    assert "server_url" not in loaded
    assert "access_token" not in loaded
    assert loaded["refresh_token"] == "refresh"
    assert loaded["default_household"] == 42
    assert "user" not in loaded
    assert loaded["custom"] == {"k": "v"}
