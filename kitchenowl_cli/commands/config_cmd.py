from __future__ import annotations

import json

import click
from rich.console import Console

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
