from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from kitchenowl_cli.api import ApiClient, ApiError, login as api_login, normalize_server_url, signup as api_signup
from kitchenowl_cli.config import clear_auth_tokens, load_config, save_config


console = Console()


@click.group()
def auth() -> None:
    """Authentication commands."""


@auth.command()
@click.option("--server", help="KitchenOwl server URL (e.g. https://kitchenowl.example.com).")
@click.option("--username", help="Username or email.")
@click.option("--password", help="Password.")
@click.option("--device", default="kitchenowl-cli", show_default=True, help="Device label for token tracking.")
def login(server: str | None, username: str | None, password: str | None, device: str) -> None:
    """Login and store access + refresh tokens."""
    cfg = load_config()
    if server is not None:
        server_url = server
    else:
        default_server = cfg.get("server_url", "")
        server_url = click.prompt(
            "Server URL",
            default=default_server,
            show_default=bool(default_server),
        )
    if not username:
        username = click.prompt("Username or email")
    if not password:
        password = click.prompt("Password", hide_input=True)

    try:
        payload = api_login(server_url, username, password, device=device)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    cfg["server_url"] = normalize_server_url(server_url)
    cfg["access_token"] = payload["access_token"]
    cfg["refresh_token"] = payload["refresh_token"]
    cfg["user"] = payload.get("user")
    save_config(cfg)

    try:
        client = ApiClient(cfg)
        households = client.get("/api/household")
        if households and isinstance(households, list) and not cfg.get("default_household"):
            cfg["default_household"] = households[0]["id"]
            save_config(cfg)
    except ApiError:
        pass

    console.print("[green]Login successful.[/green]")
    if cfg.get("default_household"):
        console.print(f"Default household: {cfg['default_household']}")


@auth.command()
@click.option("--server", help="KitchenOwl server URL (e.g. https://kitchenowl.example.com).")
@click.option("--username", help="New username.")
@click.option("--name", help="Full name.")
@click.option("--password", help="Password.")
@click.option("--email", help="Optional email.")
@click.option("--device", default="kitchenowl-cli", show_default=True, help="Device label for token tracking.")
def signup(
    server: str | None,
    username: str | None,
    name: str | None,
    password: str | None,
    email: str | None,
    device: str,
) -> None:
    """Register a new user and store its tokens."""
    cfg = load_config()
    if server is not None:
        server_url = server
    else:
        default_server = cfg.get("server_url", "")
        server_url = click.prompt(
            "Server URL",
            default=default_server,
            show_default=bool(default_server),
        )
    if not username:
        username = click.prompt("Username or email")
    if not name:
        name = click.prompt("Full name")
    if not password:
        password = click.prompt("Password", hide_input=True)

    try:
        payload = api_signup(
            server_url,
            username,
            password,
            name,
            email=email,
            device=device,
        )
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    cfg["server_url"] = normalize_server_url(server_url)
    cfg["access_token"] = payload["access_token"]
    cfg["refresh_token"] = payload["refresh_token"]
    cfg["user"] = payload.get("user")
    save_config(cfg)

    try:
        client = ApiClient(cfg)
        households = client.get("/api/household")
        if households and isinstance(households, list) and not cfg.get("default_household"):
            cfg["default_household"] = households[0]["id"]
            save_config(cfg)
    except ApiError:
        pass

    console.print("[green]Signup successful.[/green]")
    if cfg.get("default_household"):
        console.print(f"Default household: {cfg['default_household']}")


@auth.command()
def status() -> None:
    """Show current auth status."""
    cfg = load_config()
    if not cfg.get("server_url"):
        console.print("No server configured.")
        return

    table = Table(show_header=False, box=None)
    table.add_row("Server", str(cfg["server_url"]))
    table.add_row("Default household", str(cfg.get("default_household", "-")))

    if not cfg.get("access_token"):
        table.add_row("Logged in", "No")
        console.print(table)
        return

    try:
        client = ApiClient(cfg)
        user = client.get("/api/user")
        table.add_row("Logged in", "Yes")
        table.add_row("User", f"{user.get('name', '-')} (id={user.get('id', '-')})")
    except ApiError as exc:
        table.add_row("Logged in", f"No ({exc})")
    console.print(table)


@auth.command()
def logout() -> None:
    """Clear stored auth tokens."""
    clear_auth_tokens()
    console.print("[green]Logged out.[/green]")
