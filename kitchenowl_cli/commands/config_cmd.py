from __future__ import annotations

import json

import click
from rich.console import Console
from rich.table import Table

from kitchenowl_cli.api import ApiClient, ApiError, normalize_server_url
from kitchenowl_cli.config import load_config, save_config


console = Console()


@click.group("config")
def config_group() -> None:
    """Configuration commands."""


@config_group.command("show")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def show_config(as_json: bool) -> None:
    """Show saved CLI configuration."""
    cfg = load_config()
    safe = dict(cfg)
    for key in ("access_token", "refresh_token"):
        if safe.get(key):
            safe[key] = f"{str(safe[key])[:12]}..."

    if as_json:
        click.echo(json.dumps(safe, indent=2, sort_keys=True))
        return

    if not safe:
        console.print("No config found.")
        return
    for key, value in safe.items():
        console.print(f"{key}: {value}")


@config_group.command("set-default-household")
@click.argument("household_id", type=int)
def set_default_household(household_id: int) -> None:
    """Set default household ID for recipe commands."""
    cfg = load_config()
    cfg["default_household"] = household_id
    save_config(cfg)
    console.print(f"[green]Default household set to {household_id}.[/green]")


@config_group.command("server-settings")
@click.option("--server", help="KitchenOwl server URL (overrides saved config).")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def server_settings(server: str | None, as_json: bool) -> None:
    """Show read-only server settings exposed by /api/health."""
    cfg = load_config()
    server_url = server or cfg.get("server_url")
    if not server_url:
        raise click.ClickException("No server configured. Provide --server or login first.")

    client = ApiClient({"server_url": normalize_server_url(server_url)})
    health = None
    last_error: ApiError | None = None
    for path in (
        "/api/health",
        "/api/health/8M4F88S8ooi4sMbLBfkkV7ctWwgibW6V",
    ):
        try:
            health = client.get_public(path)
            break
        except ApiError as exc:
            last_error = exc
            continue

    if health is None:
        raise click.ClickException(str(last_error) if last_error else "Could not read server settings.")

    settings = {
        "open_registration": bool(health.get("open_registration", False)),
        "email_mandatory": bool(health.get("email_mandatory", False)),
        "oidc_provider": health.get("oidc_provider", []),
    }
    for key in ("privacy_policy", "terms"):
        if key in health:
            settings[key] = health[key]

    if as_json:
        click.echo(json.dumps(settings, indent=2, sort_keys=True))
        return

    table = Table(show_header=False, box=None)
    table.add_row("server", normalize_server_url(server_url))
    for key, value in settings.items():
        rendered = ", ".join(value) if isinstance(value, list) else str(value)
        table.add_row(key, rendered)
    console.print(table)
