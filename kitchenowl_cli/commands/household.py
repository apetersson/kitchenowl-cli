from __future__ import annotations

import json
from typing import Any

import click
from rich.console import Console
from rich.table import Table

from kitchenowl_cli.api import ApiClient, ApiError
from kitchenowl_cli.config import load_config, save_config


console = Console()


@click.group()
def household() -> None:
    """Household commands."""


def _client_and_config() -> tuple[ApiClient, dict[str, Any]]:
    cfg = load_config()
    try:
        client = ApiClient(cfg)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc
    return client, cfg


def _ensure_household(cfg: dict[str, Any], household_id: int | None) -> int:
    if household_id:
        return household_id
    value = cfg.get("default_household")
    if not value:
        raise click.ClickException("No household selected; supply --household-id or set a default.")
    return int(value)


@household.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def list_households(as_json: bool) -> None:
    """List households for the current user."""
    client, cfg = _client_and_config()
    try:
        households = client.get("/api/household")
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(households, indent=2, sort_keys=True))
        return

    if not households:
        console.print("No households found.")
        return

    table = Table(title="Households")
    table.add_column("ID", justify="right")
    table.add_column("Name")
    default_household = cfg.get("default_household")

    for h in households:
        marker = " (default)" if h.get("id") == default_household else ""
        table.add_row(str(h.get("id", "-")), f"{h.get('name', '-')}{marker}")
    console.print(table)


@household.command("use")
@click.argument("household_id", type=int)
def use_household(household_id: int) -> None:
    """Set default household ID."""
    cfg = load_config()
    cfg["default_household"] = household_id
    save_config(cfg)
    console.print(f"[green]Default household set to {household_id}.[/green]")


@household.command("get")
@click.argument("household_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def get_household(household_id: int, as_json: bool) -> None:
    """Get household details."""
    client, _ = _client_and_config()
    try:
        data = client.get(f"/api/household/{household_id}")
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return

    table = Table(show_header=False, box=None)
    table.add_row("ID", str(data.get("id", "-")))
    table.add_row("Name", str(data.get("name", "-")))
    table.add_row("Description", str(data.get("description", "-")))
    table.add_row("Language", str(data.get("language", "-")))
    table.add_row("Planner feature", str(data.get("planner_feature", "-")))
    table.add_row("Expenses feature", str(data.get("expenses_feature", "-")))
    table.add_row("Verified", str(data.get("verified", "-")))
    console.print(table)


@household.command("create")
@click.option("--name", required=True, help="Household name.")
@click.option("--description", help="Optional description.")
@click.option("--link", help="Optional link.")
@click.option("--language", help="Optional language code.")
@click.option("--planner-feature/--no-planner-feature", default=None)
@click.option("--expenses-feature/--no-expenses-feature", default=None)
@click.option("--use", "set_default", is_flag=True, help="Set created household as default.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def create_household(
    name: str,
    description: str | None,
    link: str | None,
    language: str | None,
    planner_feature: bool | None,
    expenses_feature: bool | None,
    set_default: bool,
    as_json: bool,
) -> None:
    """Create a household."""
    client, cfg = _client_and_config()
    payload: dict[str, Any] = {"name": name}
    if description is not None:
        payload["description"] = description
    if link is not None:
        payload["link"] = link
    if language is not None:
        payload["language"] = language
    if planner_feature is not None:
        payload["planner_feature"] = planner_feature
    if expenses_feature is not None:
        payload["expenses_feature"] = expenses_feature

    try:
        data = client.post("/api/household", json=payload)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if set_default:
        cfg["default_household"] = data["id"]
        save_config(cfg)

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return

    console.print(f"[green]Created household {data.get('id')} ({data.get('name')}).[/green]")
    if set_default:
        console.print(f"Default household set to {data.get('id')}.")


@household.command("update")
@click.argument("household_id", type=int)
@click.option("--name")
@click.option("--description")
@click.option("--link")
@click.option("--planner-feature/--no-planner-feature", default=None)
@click.option("--expenses-feature/--no-expenses-feature", default=None)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def update_household(
    household_id: int,
    name: str | None,
    description: str | None,
    link: str | None,
    planner_feature: bool | None,
    expenses_feature: bool | None,
    as_json: bool,
) -> None:
    """Update household fields."""
    client, _ = _client_and_config()
    payload: dict[str, Any] = {}
    if name is not None:
        payload["name"] = name
    if description is not None:
        payload["description"] = description
    if link is not None:
        payload["link"] = link
    if planner_feature is not None:
        payload["planner_feature"] = planner_feature
    if expenses_feature is not None:
        payload["expenses_feature"] = expenses_feature
    if not payload:
        raise click.ClickException("No update fields provided.")

    try:
        data = client.post(f"/api/household/{household_id}", json=payload)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return
    console.print(f"[green]Updated household {household_id}.[/green]")


@household.command("delete")
@click.argument("household_id", type=int)
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt.")
def delete_household(household_id: int, yes: bool) -> None:
    """Delete a household."""
    if not yes and not click.confirm(f"Delete household {household_id}?", default=False):
        raise click.ClickException("Aborted.")

    client, cfg = _client_and_config()
    try:
        client.delete(f"/api/household/{household_id}")
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if cfg.get("default_household") == household_id:
        cfg.pop("default_household", None)
        save_config(cfg)
        console.print("[yellow]Deleted default household; cleared default_household setting.[/yellow]")
    console.print(f"[green]Deleted household {household_id}.[/green]")


@household.group("member")
def member_group() -> None:
    """Manage household members."""


@member_group.command("list")
@click.option("--household-id", type=int, help="Override default household.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def list_members(household_id: int | None, as_json: bool) -> None:
    """List members of a household."""
    client, cfg = _client_and_config()
    hid = _ensure_household(cfg, household_id)
    try:
        data = client.get(f"/api/household/{hid}")
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    members = data.get("member", [])
    if as_json:
        click.echo(json.dumps(members, indent=2, sort_keys=True))
        return

    if not members:
        console.print("No members found.")
        return

    table = Table(title=f"Household {hid} Members")
    table.add_column("ID", justify="right")
    table.add_column("Name")
    table.add_column("Username")
    table.add_column("Admin")
    table.add_column("Owner")
    table.add_column("Last seen")
    for user in members:
        table.add_row(
            str(user.get("id", "-")),
            str(user.get("name", "-")),
            str(user.get("username", "-")),
            "yes" if user.get("admin") else "no",
            "yes" if user.get("owner") else "no",
            str(user.get("last_seen", "-")),
        )
    console.print(table)


@member_group.command("add")
@click.argument("user_id", type=int)
@click.option("--household-id", type=int, help="Override default household.")
@click.option("--admin/--no-admin", default=True, help="Grant admin rights.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def add_member(
    user_id: int,
    household_id: int | None,
    admin: bool,
    as_json: bool,
) -> None:
    """Add or update a household member."""
    client, cfg = _client_and_config()
    hid = _ensure_household(cfg, household_id)
    try:
        data = client.put(
            f"/api/household/{hid}/member/{user_id}",
            json={"admin": admin},
        )
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return

    console.print(f"[green]Member {user_id} added/updated in household {hid} (admin={admin}).[/green]")


@member_group.command("remove")
@click.argument("user_id", type=int)
@click.option("--household-id", type=int, help="Override default household.")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt.")
def remove_member(user_id: int, household_id: int | None, yes: bool) -> None:
    """Remove a member from a household."""
    if not yes and not click.confirm(f"Remove user {user_id} from the household?", default=False):
        raise click.ClickException("Aborted.")
    client, cfg = _client_and_config()
    hid = _ensure_household(cfg, household_id)
    try:
        client.delete(f"/api/household/{hid}/member/{user_id}")
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc
    console.print(f"[green]Member {user_id} removed from household {hid}.[/green]")
