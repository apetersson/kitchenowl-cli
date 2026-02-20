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


@click.group("user")
def user() -> None:
    """User administration commands."""


def _print_users(users: list[dict[str, Any]]) -> None:
    table = Table(title="Users")
    table.add_column("ID", justify="right")
    table.add_column("Username")
    table.add_column("Name")
    table.add_column("Email")
    table.add_column("Admin")
    table.add_column("Last seen")
    for entry in users:
        table.add_row(
            str(entry.get("id", "-")),
            str(entry.get("username", "-")),
            str(entry.get("name", "-")),
            str(entry.get("email", "-")),
            "yes" if entry.get("admin") else "no",
            str(entry.get("last_seen", "-")),
        )
    console.print(table)


@user.command("list")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def list_users(as_json: bool) -> None:
    """List all users (admin only)."""
    client, _ = _client_and_config()
    try:
        users = client.get("/api/user/all")
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(users, indent=2, sort_keys=True))
        return

    _print_users(users)


@user.command("get")
@click.argument("user_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def get_user(user_id: int, as_json: bool) -> None:
    """Show a user’s details."""
    client, _ = _client_and_config()
    try:
        user_data = client.get(f"/api/user/{user_id}")
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(user_data, indent=2, sort_keys=True))
        return

    table = Table(show_header=False, box=None)
    table.add_row("ID", str(user_data.get("id", "-")))
    table.add_row("Username", str(user_data.get("username", "-")))
    table.add_row("Name", str(user_data.get("name", "-")))
    table.add_row("Email", str(user_data.get("email", "-")))
    table.add_row("Admin", str(user_data.get("admin", "-")))
    table.add_row("Last seen", str(user_data.get("last_seen", "-")))
    table.add_row("Email verified", str(user_data.get("email_verified", "-")))
    console.print(table)


@user.command("search")
@click.option("--query", required=True, help="Search expression.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def search_users(query: str, as_json: bool) -> None:
    """Search users by name/username."""
    client, _ = _client_and_config()
    try:
        results = client.get("/api/user/search", params={"query": query})
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(results, indent=2, sort_keys=True))
        return

    _print_users(results)


@user.command("create")
@click.option("--username", prompt=True)
@click.option("--name", prompt=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--email")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def create_user(username: str, name: str, password: str, email: str | None, as_json: bool) -> None:
    """Create a new user (admin only)."""
    client, _ = _client_and_config()
    payload: dict[str, Any] = {"username": username, "name": name, "password": password}
    if email:
        payload["email"] = email

    try:
        data = client.post("/api/user/new", json=payload)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return

    created_id = data.get("id")
    created_username = data.get("username")
    if created_id is not None and created_username:
        console.print(f"[green]Created user {created_id} ({created_username}).[/green]")
    elif created_username:
        console.print(f"[green]Created user {created_username}.[/green]")
    else:
        console.print("[green]Created user.[/green]")


@user.command("update")
@click.argument("user_id", type=int)
@click.option("--name")
@click.option("--email")
@click.option("--password", hide_input=True, confirmation_prompt=True)
@click.option("--admin/--no-admin", default=None)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def update_user(
    user_id: int,
    name: str | None,
    email: str | None,
    password: str | None,
    admin: bool | None,
    as_json: bool,
) -> None:
    """Update user details (admin only)."""
    client, _ = _client_and_config()
    payload: dict[str, Any] = {}
    if name is not None:
        payload["name"] = name
    if email is not None:
        payload["email"] = email
    if password is not None:
        payload["password"] = password
    if admin is not None:
        payload["admin"] = admin
    if not payload:
        raise click.ClickException("No update fields provided.")

    try:
        data = client.post(f"/api/user/{user_id}", json=payload)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return

    console.print(f"[green]Updated user {user_id}.[/green]")


@user.command("delete")
@click.argument("user_id", type=int)
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation.")
def delete_user(user_id: int, yes: bool) -> None:
    """Delete a user (admin only)."""
    if not yes and not click.confirm(f"Delete user {user_id}?", default=False):
        raise click.ClickException("Aborted.")
    client, _ = _client_and_config()
    try:
        client.delete(f"/api/user/{user_id}")
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc
    console.print(f"[green]Deleted user {user_id}.[/green]")
