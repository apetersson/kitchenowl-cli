from kitchenowl_cli.commands.recipe import _parse_ingredient, _parse_item


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


def test_parse_ingredient_defaults():
    ingredient = _parse_ingredient("Sugar")
    assert ingredient["name"] == "Sugar"
    assert ingredient["description"] == ""
    assert ingredient["optional"] is True


def test_parse_ingredient_full():
    ingredient = _parse_ingredient("Tomato|Fresh|false")
    assert ingredient["name"] == "Tomato"
    assert ingredient["description"] == "Fresh"
    assert ingredient["optional"] is False


def test_parse_ingredient_invalid():
    with pytest.raises(Exception):
        _parse_ingredient("|missingname")
