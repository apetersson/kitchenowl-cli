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


@click.group("category")
def category() -> None:
    """Category commands."""


@category.command("list")
@click.option("--household-id", type=int, help="Override default household.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def list_categories(household_id: int | None, as_json: bool) -> None:
    """List item categories for a household."""
    client, cfg = _client_and_config()
    hid = _resolve_household(cfg, household_id)
    try:
        data = client.get(f"/api/household/{hid}/category")
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return
    if not data:
        console.print("No categories found.")
        return

    table = Table(title=f"Categories (household {hid})")
    table.add_column("ID", justify="right")
    table.add_column("Name")
    table.add_column("Ordering", justify="right")
    for category_data in data:
        table.add_row(
            str(category_data.get("id", "-")),
            str(category_data.get("name", "-")),
            str(category_data.get("ordering", "-")),
        )
    console.print(table)
