import requests
import pytest

from kitchenowl_cli.api import ApiClient, ApiError, _extract_error, login, normalize_server_url, signup


class DummyResponse:
    def __init__(self, json_data=None, text="", status_code=400, ok=False):
        self._json = json_data
        self.text = text
        self.status_code = status_code
        self.ok = ok

    def json(self):
        if isinstance(self._json, Exception):
            raise self._json
        return self._json


class DummySession:
    def __init__(self, response=None, error: Exception | None = None):
        self.response = response
        self.error = error

    def request(self, *args, **kwargs):
        if self.error:
            raise self.error
        return self.response

    def get(self, *args, **kwargs):
        if self.error:
            raise self.error
        return self.response


def test_normalize_server_url_trims_trailing_slash():
    assert normalize_server_url("https://example.com/") == "https://example.com"
    assert normalize_server_url("https://example.com") == "https://example.com"


def test_extract_error_from_json_message():
    resp = DummyResponse(json_data={"message": "boom"}, ok=False)
    assert _extract_error(resp) == "boom"


def test_extract_error_falls_back_to_text():
    resp = DummyResponse(json_data=ValueError("boom"), text="plain text", ok=False)
    msg = _extract_error(resp)
    assert "plain text" in msg


def test_request_transport_error_wrapped():
    client = ApiClient({"server_url": "https://example.com", "access_token": "a", "refresh_token": "r"})
    client.session = DummySession(error=requests.ConnectionError("offline"))

    with pytest.raises(ApiError, match="Request failed"):
        client.get("/api/health")


def test_get_public_uses_auth_none_without_tokens():
    response = DummyResponse(json_data={"ok": True}, text='{"ok": true}', status_code=200, ok=True)
    client = ApiClient({"server_url": "https://example.com"})
    client.session = DummySession(response=response)

    assert client.get_public("/api/health") == {"ok": True}


def test_request_rejects_unknown_auth_mode():
    client = ApiClient({"server_url": "https://example.com", "access_token": "a", "refresh_token": "r"})

    with pytest.raises(ApiError, match="Unsupported auth mode"):
        client.request("GET", "/api/health", auth="invalid")


def test_login_transport_error_wrapped(monkeypatch):
    def fail(*args, **kwargs):
        raise requests.Timeout("timed out")

    monkeypatch.setattr("kitchenowl_cli.api.requests.post", fail)

    with pytest.raises(ApiError, match="Login failed"):
        login("https://example.com", "user", "pass")


def test_signup_transport_error_wrapped(monkeypatch):
    def fail(*args, **kwargs):
        raise requests.ConnectionError("refused")

    monkeypatch.setattr("kitchenowl_cli.api.requests.post", fail)

    with pytest.raises(ApiError, match="Signup failed"):
        signup("https://example.com", "user", "pass", "User")
