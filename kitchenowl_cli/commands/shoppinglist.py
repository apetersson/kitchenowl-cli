from __future__ import annotations

import json
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


@click.group()
def shoppinglist() -> None:
    """Shopping list commands."""


@shoppinglist.command("list")
@click.option("--household-id", type=int, help="Override default household.")
@click.option("--recent-limit", type=int, default=5, show_default=True, help="Recent-items limit.")
@click.option("--orderby", type=int, default=0, show_default=True, help="Ordering strategy (0=default, 1=ordering).")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def list_shoppinglists(household_id: int | None, recent_limit: int, orderby: int, as_json: bool) -> None:
    """List shopping lists for a household."""
    client, cfg = _client_and_config()
    hid = _resolve_household(cfg, household_id)
    try:
        data = client.get(
            f"/api/household/{hid}/shoppinglist",
            params={"recent_limit": recent_limit, "orderby": orderby},
        )
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return

    if not isinstance(data, list) or not data:
        console.print("No shopping lists found.")
        return

    table = Table(title=f"Household {hid} Shopping Lists")
    table.add_column("ID", justify="right")
    table.add_column("Name")
    table.add_column("Items", justify="right")
    table.add_column("Recent", justify="right")
    for entry in data:
        table.add_row(
            str(entry.get("id", "-")),
            str(entry.get("name", "-")),
            str(len(entry.get("items", []))),
            str(len(entry.get("recentItems", []))),
        )
    console.print(table)


@shoppinglist.command("create")
@click.argument("name")
@click.option("--household-id", type=int, help="Override default household.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def create_shoppinglist(name: str, household_id: int | None, as_json: bool) -> None:
    """Create a new shopping list."""
    client, cfg = _client_and_config()
    hid = _resolve_household(cfg, household_id)
    try:
        data = client.post(f"/api/household/{hid}/shoppinglist", json={"name": name})
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return

    console.print(f"[green]Created shopping list {data.get('id')} ({data.get('name')}).[/green]")


@shoppinglist.command("delete")
@click.argument("list_id", type=int)
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation.")
def delete_shoppinglist(list_id: int, yes: bool) -> None:
    """Delete a shopping list."""
    if not yes and not click.confirm(f"Delete shopping list {list_id}?", default=False):
        raise click.ClickException("Aborted.")
    client, _ = _client_and_config()
    try:
        client.delete(f"/api/shoppinglist/{list_id}")
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc
    console.print(f"[green]Deleted shopping list {list_id}.[/green]")


@shoppinglist.command("items")
@click.argument("list_id", type=int)
@click.option("--orderby", type=int, default=0, show_default=True, help="Ordering strategy (0=default, 2=name).")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def list_items(list_id: int, orderby: int, as_json: bool) -> None:
    """List items in the shopping list."""
    client, _ = _client_and_config()
    try:
        data = client.get(f"/api/shoppinglist/{list_id}/items", params={"orderby": orderby})
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return

    if not data:
        console.print("No items found.")
        return

    table = Table(title=f"Shopping list {list_id} items")
    table.add_column("Item ID", justify="right")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Category")
    for item in data:
        table.add_row(
            str(item.get("id", "-")),
            str(item.get("name", "-")),
            str(item.get("description", "-")),
            str(item.get("category", "-")),
        )
    console.print(table)


@shoppinglist.command("add-item")
@click.argument("list_id", type=int)
@click.argument("item_id", type=int)
@click.option("--description", default="", help="Optional description.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def add_item(list_id: int, item_id: int, description: str, as_json: bool) -> None:
    """Add or update a single item on the list."""
    client, _ = _client_and_config()
    try:
        data = client.post(
            f"/api/shoppinglist/{list_id}/item/{item_id}",
            json={"description": description},
        )
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return

    console.print(f"[green]Added/updated item {item_id} on list {list_id}.[/green]")


@shoppinglist.command("add-item-by-name")
@click.argument("list_id", type=int)
@click.argument("name")
@click.option("--description", help="Optional description.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def add_item_by_name(list_id: int, name: str, description: str | None, as_json: bool) -> None:
    """Add an item by name, creating it if necessary."""
    client, _ = _client_and_config()
    payload: dict[str, Any] = {"name": name}
    if description is not None:
        payload["description"] = description
    try:
        data = client.post(f"/api/shoppinglist/{list_id}/add-item-by-name", json=payload)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return

    console.print(f"[green]Ensured item '{name}' in list {list_id}.[/green]")


@shoppinglist.command("suggested")
@click.argument("list_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def suggested_items(list_id: int, as_json: bool) -> None:
    """Show suggested items for a shopping list."""
    client, _ = _client_and_config()
    try:
        data = client.get(f"/api/shoppinglist/{list_id}/suggested-items")
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return

    if not data:
        console.print("No suggestions found.")
        return

    table = Table(title=f"Suggested items for list {list_id}")
    table.add_column("Item ID", justify="right")
    table.add_column("Name")
    table.add_column("Category")
    for item in data:
        table.add_row(
            str(item.get("id", "-")),
            str(item.get("name", "-")),
            str(item.get("category", "-")),
        )
    console.print(table)


@shoppinglist.command("remove-item")
@click.argument("list_id", type=int)
@click.argument("item_id", type=int)
@click.option("--removed-at", type=int, default=0, help="Timestamp in milliseconds to record removal.")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation.")
def remove_item(list_id: int, item_id: int, removed_at: int, yes: bool) -> None:
    """Remove an item from the shopping list (mark done)."""
    if not yes and not click.confirm(f"Remove item {item_id} from list {list_id}?", default=False):
        raise click.ClickException("Aborted.")

    payload: dict[str, int | None] = {"item_id": item_id}
    if removed_at > 0:
        payload["removed_at"] = removed_at

    client, _ = _client_and_config()
    try:
        client.delete(f"/api/shoppinglist/{list_id}/item", json=payload)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    console.print(f"[green]Marked item {item_id} as done on list {list_id}.[/green]")
