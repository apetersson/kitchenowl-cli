from kitchenowl_cli.commands.recipe import _parse_item


def test_parse_item_defaults():
    item = _parse_item("Sugar")
    assert item["name"] == "Sugar"
    assert item["description"] == ""
    assert item["optional"] is True


def test_parse_item_full():
    item = _parse_item("Tomato|Fresh|false")
    assert item["name"] == "Tomato"
    assert item["description"] == "Fresh"
    assert item["optional"] is False


import pytest


def test_parse_item_invalid():
    with pytest.raises(Exception):
        _parse_item("|missingname")
