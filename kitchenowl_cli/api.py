from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
from requests import RequestException

from .config import config_lock, load_config, save_config


def normalize_server_url(url: str) -> str:
    normalized = url.rstrip("/")
    # Accept both base URLs (https://host) and API URLs (https://host/api)
    # from user input/config without producing /api/api/* requests.
    if normalized.endswith("/api"):
        normalized = normalized[:-4]
    return normalized


def _extract_error(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text.strip() or f"HTTP {response.status_code}"

    if isinstance(payload, dict):
        for key in ("msg", "message", "error", "detail"):
            if key in payload and payload[key]:
                return str(payload[key])
    return str(payload)


@dataclass
class ApiError(Exception):
    message: str
    status_code: int | None = None

    def __str__(self) -> str:
        if self.status_code is None:
            return self.message
        return f"{self.message} (HTTP {self.status_code})"


class ApiClient:
    def __init__(self, config: dict[str, Any]):
        server_url = config.get("server_url")
        if not server_url:
            raise ApiError("No server configured. Run `kitchenowl auth login` first.")
        self.config = config
        self.server_url = normalize_server_url(server_url)
        self.session = requests.Session()

    def _url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.server_url}{path}"

    def _auth_header(self, token_key: str) -> dict[str, str]:
        token = self.config.get(token_key)
        if not token:
            raise ApiError("Not authenticated. Run `kitchenowl auth login`.")
        return {"Authorization": f"Bearer {token}"}

    def refresh_tokens(self) -> None:
        with config_lock():
            latest_config = load_config()
            if latest_config.get("refresh_token"):
                self.config["refresh_token"] = latest_config["refresh_token"]
            if latest_config.get("access_token"):
                self.config["access_token"] = latest_config["access_token"]
            if latest_config.get("user"):
                self.config["user"] = latest_config["user"]
            if latest_config.get("server_url"):
                self.config["server_url"] = latest_config["server_url"]
                self.server_url = normalize_server_url(latest_config["server_url"])

            headers = self._auth_header("refresh_token")
            try:
                response = self.session.get(
                    self._url("/api/auth/refresh"),
                    headers=headers,
                    timeout=30,
                )
            except RequestException as exc:
                raise ApiError(f"Token refresh failed: {exc}") from exc
            if not response.ok:
                raise ApiError(
                    f"Token refresh failed: {_extract_error(response)}",
                    response.status_code,
                )
            payload = response.json()
            self.config["access_token"] = payload["access_token"]
            self.config["refresh_token"] = payload["refresh_token"]
            if "user" in payload:
                self.config["user"] = payload["user"]
            save_config(self.config, already_locked=True)

    def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        auth: str = "access",
        _retry: bool = True,
    ) -> Any:
        headers: dict[str, str] = {}
        if auth == "access":
            headers.update(self._auth_header("access_token"))
        elif auth == "refresh":
            headers.update(self._auth_header("refresh_token"))
        elif auth == "none":
            pass
        else:
            raise ApiError(f"Unsupported auth mode `{auth}`.")

        try:
            response = self.session.request(
                method=method.upper(),
                url=self._url(path),
                json=json,
                params=params,
                headers=headers,
                timeout=30,
            )
        except RequestException as exc:
            raise ApiError(f"Request failed: {exc}") from exc

        if response.status_code == 401 and auth == "access" and _retry:
            self.refresh_tokens()
            return self.request(
                method,
                path,
                json=json,
                params=params,
                auth=auth,
                _retry=False,
            )

        if not response.ok:
            raise ApiError(_extract_error(response), response.status_code)

        if response.text.strip():
            try:
                return response.json()
            except ValueError:
                return response.text
        return None

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return self.request("GET", path, params=params)

    def get_public(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return self.request("GET", path, params=params, auth="none")

    def post(self, path: str, *, json: dict[str, Any] | None = None) -> Any:
        return self.request("POST", path, json=json)

    def delete(self, path: str, *, json: dict[str, Any] | None = None) -> Any:
        return self.request("DELETE", path, json=json)

    def put(self, path: str, *, json: dict[str, Any] | None = None) -> Any:
        return self.request("PUT", path, json=json)


def login(
    server_url: str,
    username: str,
    password: str,
    *,
    device: str = "kitchenowl-cli",
) -> dict[str, Any]:
    url = f"{normalize_server_url(server_url)}/api/auth"
    try:
        response = requests.post(
            url,
            json={
                "username": username,
                "password": password,
                "device": device,
            },
            timeout=30,
        )
    except RequestException as exc:
        raise ApiError(f"Login failed: {exc}") from exc
    if not response.ok:
        raise ApiError(_extract_error(response), response.status_code)
    return response.json()


def signup(
    server_url: str,
    username: str,
    password: str,
    name: str,
    *,
    email: str | None = None,
    device: str = "kitchenowl-cli",
) -> dict[str, Any]:
    url = f"{normalize_server_url(server_url)}/api/auth/signup"
    body: dict[str, Any] = {
        "username": username,
        "password": password,
        "name": name,
        "device": device,
    }
    if email:
        body["email"] = email
    try:
        response = requests.post(
            url,
            json=body,
            timeout=30,
        )
    except RequestException as exc:
        raise ApiError(f"Signup failed: {exc}") from exc
    if not response.ok:
        raise ApiError(_extract_error(response), response.status_code)
    return response.json()
