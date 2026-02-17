from kitchenowl_cli.api import _extract_error, normalize_server_url


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
