import json
import os
import stat

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


def test_save_config_sets_secure_permissions_on_posix(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    monkeypatch.setattr(config_mod, "get_config_path", lambda: path)
    monkeypatch.setattr(config_mod, "get_config_lock_path", lambda: tmp_path / "config.lock")

    config_mod.save_config({"server_url": "https://example.com"})

    if os.name != "nt":
        assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_save_config_already_locked_writes_without_relocking(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    monkeypatch.setattr(config_mod, "get_config_path", lambda: path)

    config_mod.save_config({"a": 1}, already_locked=True)

    assert config_mod.load_config() == {"a": 1}
