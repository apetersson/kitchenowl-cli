from __future__ import annotations

import json
import os
from contextlib import contextmanager
from json import JSONDecodeError
from pathlib import Path
from typing import Any

try:
    import fcntl
except ImportError:  # pragma: no cover - not available on Windows
    fcntl = None


APP_DIR = "kitchenowl"
CONFIG_FILE = "config.json"


def _config_dir() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / APP_DIR
    return Path.home() / ".config" / APP_DIR


def get_config_path() -> Path:
    return _config_dir() / CONFIG_FILE


def get_config_lock_path() -> Path:
    return _config_dir() / f"{CONFIG_FILE}.lock"


@contextmanager
def config_lock() -> Any:
    lock_path = get_config_lock_path()
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_file = lock_path.open("a+", encoding="utf-8")
    try:
        if fcntl is not None:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        if fcntl is not None:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        lock_file.close()


def _normalize_config(data: dict[str, Any]) -> dict[str, Any]:
    config = dict(data)

    if "server_url" in config and not isinstance(config["server_url"], str):
        config.pop("server_url", None)
    if "access_token" in config and not isinstance(config["access_token"], str):
        config.pop("access_token", None)
    if "refresh_token" in config and not isinstance(config["refresh_token"], str):
        config.pop("refresh_token", None)
    if "user" in config and not isinstance(config["user"], dict):
        config.pop("user", None)

    if "default_household" in config:
        value = config["default_household"]
        if isinstance(value, int):
            pass
        elif isinstance(value, str) and value.isdigit():
            config["default_household"] = int(value)
        else:
            config.pop("default_household", None)

    return config


def load_config() -> dict[str, Any]:
    path = get_config_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return _normalize_config(data)


def _save_config_unlocked(path: Path, config: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")
    if os.name != "nt":
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass


def save_config(config: dict[str, Any], *, already_locked: bool = False) -> None:
    path = get_config_path()
    if already_locked:
        _save_config_unlocked(path, config)
        return
    with config_lock():
        _save_config_unlocked(path, config)


def update_config(**kwargs: Any) -> dict[str, Any]:
    with config_lock():
        config = load_config()
        config.update(kwargs)
        save_config(config, already_locked=True)
        return config


def clear_auth_tokens() -> dict[str, Any]:
    with config_lock():
        config = load_config()
        for key in ("access_token", "refresh_token", "user"):
            config.pop(key, None)
        save_config(config, already_locked=True)
        return config
