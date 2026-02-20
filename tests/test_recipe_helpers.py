import pytest
from click.testing import CliRunner

from kitchenowl_cli.commands.recipe import _editable_recipe, _normalize_payload, _parse_ingredient, _parse_item
from kitchenowl_cli.main import cli


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


def test_normalize_payload_prefers_items_when_both_present_for_update():
    payload = _normalize_payload(
        {
            "items": [{"name": "Edited step", "description": "updated", "optional": False}],
            "ingredients": [{"name": "Stale ingredient", "description": "old", "optional": True}],
        },
        for_update=True,
    )

    assert payload["items"] == [{"name": "Edited step", "description": "updated", "optional": False}]


def test_normalize_payload_uses_ingredients_when_items_missing():
    payload = _normalize_payload(
        {"ingredients": [{"name": "Salt", "description": "1 tsp", "optional": False}]},
        for_update=True,
    )

    assert payload["items"] == [{"name": "Salt", "description": "1 tsp", "optional": False}]


def test_editable_recipe_does_not_duplicate_items_as_ingredients():
    editable = _editable_recipe(
        {
            "name": "Soup",
            "items": [{"name": "Step", "description": "Do thing", "optional": True}],
        }
    )

    assert editable["items"] == [{"name": "Step", "description": "Do thing", "optional": True}]
    assert editable["ingredients"] == []


def test_recipe_add_rejects_invalid_visibility():
    runner = CliRunner()
    result = runner.invoke(cli, ["recipe", "add", "--household-id", "1", "--name", "Soup", "--visibility", "3"])

    assert result.exit_code != 0
    assert "Invalid value for '--visibility'" in result.output
