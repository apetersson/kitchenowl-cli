from kitchenowl_cli.commands import auth as auth_mod


def test_signup_prompts_for_username(monkeypatch):
    prompts: list[str] = []

    def fake_prompt(text, **kwargs):
        prompts.append(text)
        if text == "Username":
            return "alice"
        raise AssertionError(f"Unexpected prompt: {text}")

    monkeypatch.setattr(auth_mod, "load_config", lambda: {})
    monkeypatch.setattr(auth_mod.click, "prompt", fake_prompt)
    monkeypatch.setattr(
        auth_mod,
        "api_signup",
        lambda *args, **kwargs: {"access_token": "a", "refresh_token": "r", "user": {"id": 1}},
    )
    monkeypatch.setattr(auth_mod, "save_config", lambda cfg: None)
    monkeypatch.setattr(auth_mod, "_set_default_household", lambda cfg: None)
    monkeypatch.setattr(auth_mod.console, "print", lambda *args, **kwargs: None)

    auth_mod.signup.callback("https://example.com", None, "Alice", "secret", None, "kitchenowl-cli")

    assert prompts == ["Username"]


def test_login_prints_warning_when_default_household_setup_fails(monkeypatch):
    monkeypatch.setattr(auth_mod, "load_config", lambda: {})
    monkeypatch.setattr(
        auth_mod,
        "api_login",
        lambda *args, **kwargs: {"access_token": "a", "refresh_token": "r", "user": {"id": 1}},
    )
    monkeypatch.setattr(auth_mod, "save_config", lambda cfg: None)
    monkeypatch.setattr(auth_mod, "_set_default_household", lambda cfg: "household endpoint unavailable")

    printed: list[str] = []
    monkeypatch.setattr(auth_mod.console, "print", lambda message: printed.append(str(message)))

    auth_mod.login.callback("https://example.com", "alice", "secret", "kitchenowl-cli")

    assert any("Login successful." in line for line in printed)
    assert any("default household setup failed" in line for line in printed)
