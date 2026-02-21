from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import click
from rich.console import Console
from rich.table import Table

from kitchenowl_cli.api import ApiClient, ApiError
from kitchenowl_cli.config import load_config


console = Console()


def _client_and_config() -> tuple[ApiClient, dict[str, Any]]:
    cfg = load_config()
    try:
        client = ApiClient(cfg)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc
    return client, cfg


def _resolve_household(cfg: dict[str, Any], household_id: int | None) -> int:
    if household_id:
        return household_id
    target = cfg.get("default_household")
    if not target:
        raise click.ClickException("No household selected; provide --household-id or set a default.")
    return int(target)


def _date_to_epoch_ms(date_value: str | None) -> int | None:
    if not date_value:
        return None
    try:
        parsed = datetime.strptime(date_value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise click.ClickException("Invalid date format. Use YYYY-MM-DD.") from exc
    return int(datetime(parsed.year, parsed.month, parsed.day, tzinfo=timezone.utc).timestamp() * 1000)


def _print_plans(plans: list[dict[str, Any]], household_id: int) -> None:
    table = Table(title=f"Planner entries (household {household_id})")
    table.add_column("Recipe ID", justify="right")
    table.add_column("Recipe")
    table.add_column("Cooking Date")
    table.add_column("Day")
    table.add_column("Yields")
    for entry in plans:
        recipe = entry.get("recipe", {}) if isinstance(entry.get("recipe"), dict) else {}
        table.add_row(
            str(entry.get("recipe_id", recipe.get("id", "-"))),
            str(recipe.get("name", entry.get("name", "-"))),
            str(entry.get("cooking_date", "-")),
            str(entry.get("day", "-")),
            str(entry.get("yields", "-")),
        )
    console.print(table)


def _print_recipes(recipes: list[dict[str, Any]], title: str) -> None:
    table = Table(title=title)
    table.add_column("ID", justify="right")
    table.add_column("Name")
    table.add_column("Yields", justify="right")
    table.add_column("Time", justify="right")
    for recipe in recipes:
        table.add_row(
            str(recipe.get("id", "-")),
            str(recipe.get("name", "-")),
            str(recipe.get("yields", "-")),
            str(recipe.get("time", "-")),
        )
    console.print(table)


@click.group("planner")
def planner() -> None:
    """Planner commands."""


@planner.command("list")
@click.option("--household-id", type=int, help="Override default household.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def list_planner(household_id: int | None, as_json: bool) -> None:
    """List planner entries."""
    client, cfg = _client_and_config()
    hid = _resolve_household(cfg, household_id)
    try:
        data = client.get(f"/api/household/{hid}/planner")
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return

    if not data:
        console.print("No planner entries found.")
        return
    _print_plans(data, hid)


@planner.command("add-recipe")
@click.argument("recipe_id", type=int)
@click.option("--household-id", type=int, help="Override default household.")
@click.option("--date", "date_value", help="Cooking date (YYYY-MM-DD).")
@click.option("--yields", "yields_value", type=int, help="Optional planned yields.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def add_recipe(
    recipe_id: int,
    household_id: int | None,
    date_value: str | None,
    yields_value: int | None,
    as_json: bool,
) -> None:
    """Add a recipe to planner."""
    client, cfg = _client_and_config()
    hid = _resolve_household(cfg, household_id)
    payload: dict[str, Any] = {"recipe_id": recipe_id}
    cooking_date = _date_to_epoch_ms(date_value)
    if cooking_date is not None:
        payload["cooking_date"] = cooking_date
    if yields_value is not None:
        payload["yields"] = yields_value
    try:
        data = client.post(f"/api/household/{hid}/planner/recipe", json=payload)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return
    console.print(f"[green]Planned recipe {recipe_id} for household {hid}.[/green]")


@planner.command("remove-recipe")
@click.argument("recipe_id", type=int)
@click.option("--household-id", type=int, help="Override default household.")
@click.option("--date", "date_value", help="Cooking date (YYYY-MM-DD).")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def remove_recipe(
    recipe_id: int,
    household_id: int | None,
    date_value: str | None,
    yes: bool,
    as_json: bool,
) -> None:
    """Remove a planned recipe entry."""
    if not yes and not click.confirm(f"Remove planned recipe {recipe_id}?", default=False):
        raise click.ClickException("Aborted.")
    client, cfg = _client_and_config()
    hid = _resolve_household(cfg, household_id)
    payload: dict[str, Any] = {}
    cooking_date = _date_to_epoch_ms(date_value)
    if cooking_date is not None:
        payload["cooking_date"] = cooking_date
    try:
        data = client.delete(f"/api/household/{hid}/planner/recipe/{recipe_id}", json=payload or None)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return
    console.print(f"[green]Removed planned recipe {recipe_id} for household {hid}.[/green]")


def _list_recipe_feed(
    path: str,
    *,
    household_id: int | None,
    page: int,
    as_json: bool,
    title: str,
) -> None:
    client, cfg = _client_and_config()
    hid = _resolve_household(cfg, household_id)
    endpoint = f"/api/household/{hid}{path}"
    if page > 0:
        endpoint = f"{endpoint}/{page}"
    try:
        data = client.get(endpoint)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return

    if not data:
        console.print("No recipes found.")
        return
    _print_recipes(data, title)


@planner.command("recent-recipes")
@click.option("--household-id", type=int, help="Override default household.")
@click.option("--page", type=int, default=0, show_default=True, help="Page index.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def recent_recipes(household_id: int | None, page: int, as_json: bool) -> None:
    """List recently planned recipes."""
    _list_recipe_feed(
        "/planner/recent-recipes",
        household_id=household_id,
        page=page,
        as_json=as_json,
        title="Recent recipes",
    )


@planner.command("suggested-recipes")
@click.option("--household-id", type=int, help="Override default household.")
@click.option("--page", type=int, default=0, show_default=True, help="Page index.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def suggested_recipes(household_id: int | None, page: int, as_json: bool) -> None:
    """List suggested recipes."""
    _list_recipe_feed(
        "/planner/suggested-recipes",
        household_id=household_id,
        page=page,
        as_json=as_json,
        title="Suggested recipes",
    )


@planner.command("refresh-suggestions")
@click.option("--household-id", type=int, help="Override default household.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def refresh_suggestions(household_id: int | None, as_json: bool) -> None:
    """Refresh and list suggested recipes."""
    client, cfg = _client_and_config()
    hid = _resolve_household(cfg, household_id)
    try:
        data = client.get(f"/api/household/{hid}/planner/refresh-suggested-recipes")
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return

    if not data:
        console.print("No recipes found.")
        return
    _print_recipes(data, "Suggested recipes (refreshed)")
