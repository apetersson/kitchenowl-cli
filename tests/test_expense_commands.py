from kitchenowl_cli.commands import expense as expense_mod


def test_create_expense_builds_expected_payload(monkeypatch):
    captured: dict[str, object] = {}

    class Client:
        def post(self, path, json=None):
            captured["path"] = path
            captured["json"] = json
            return {"id": 1}

    monkeypatch.setattr(expense_mod, "_client_and_config", lambda: (Client(), {"default_household": 4}))
    monkeypatch.setattr(expense_mod.console, "print", lambda *args, **kwargs: None)

    expense_mod.create_expense.callback(
        None,
        "Dinner",
        45.5,
        10,
        ("10:1", "11:2"),
        "Team dinner",
        "2026-02-20",
        3,
        True,
        False,
    )

    assert captured["path"] == "/api/household/4/expense"
    assert captured["json"] == {
        "name": "Dinner",
        "amount": 45.5,
        "paid_by": {"id": 10},
        "paid_for": [{"id": 10, "factor": 1}, {"id": 11, "factor": 2}],
        "description": "Team dinner",
        "date": 1771545600000,
        "category": 3,
        "exclude_from_statistics": True,
    }


def test_update_expense_posts_only_given_fields(monkeypatch):
    captured: dict[str, object] = {}

    class Client:
        def post(self, path, json=None):
            captured["path"] = path
            captured["json"] = json
            return {"id": 22}

    monkeypatch.setattr(expense_mod, "_client_and_config", lambda: (Client(), {}))
    monkeypatch.setattr(expense_mod.console, "print", lambda *args, **kwargs: None)

    expense_mod.update_expense.callback(
        22,
        None,
        19.9,
        None,
        (),
        None,
        None,
        None,
        True,
        None,
        False,
    )

    assert captured["path"] == "/api/expense/22"
    assert captured["json"] == {"amount": 19.9, "category": None}


def test_list_expenses_uses_query_params(monkeypatch):
    captured: dict[str, object] = {}

    class Client:
        def get(self, path, params=None):
            captured["path"] = path
            captured["params"] = params
            return []

    monkeypatch.setattr(expense_mod, "_client_and_config", lambda: (Client(), {"default_household": 9}))
    monkeypatch.setattr(expense_mod.console, "print", lambda *args, **kwargs: None)

    expense_mod.list_expenses.callback(None, 1, 100, "2026-02-01", "2026-02-20", "milk", False)

    assert captured["path"] == "/api/household/9/expense"
    assert captured["params"] == {
        "view": 1,
        "startAfterId": 100,
        "startAfterDate": 1769904000000,
        "endBeforeDate": 1771545600000,
        "search": "milk",
    }


def test_overview_endpoint_mapping(monkeypatch):
    captured: dict[str, object] = {}

    class Client:
        def get(self, path, params=None):
            captured["path"] = path
            captured["params"] = params
            return {}

    monkeypatch.setattr(expense_mod, "_client_and_config", lambda: (Client(), {"default_household": 5}))
    monkeypatch.setattr(expense_mod.console, "print", lambda *args, **kwargs: None)

    expense_mod.overview_expenses.callback(None, 1, 2, 6, 0, False)

    assert captured["path"] == "/api/household/5/expense/overview"
    assert captured["params"] == {"view": 1, "frame": 2, "steps": 6, "page": 0}


def test_category_create_uses_expected_endpoint(monkeypatch):
    captured: dict[str, object] = {}

    class Client:
        def post(self, path, json=None):
            captured["path"] = path
            captured["json"] = json
            return {"id": 7, "name": "Food"}

    monkeypatch.setattr(expense_mod, "_client_and_config", lambda: (Client(), {"default_household": 2}))
    monkeypatch.setattr(expense_mod.console, "print", lambda *args, **kwargs: None)

    expense_mod.create_expense_category.callback(None, "Food", 12, 250.0, False)

    assert captured["path"] == "/api/household/2/expense/categories"
    assert captured["json"] == {"name": "Food", "color": 12, "budget": 250.0}
