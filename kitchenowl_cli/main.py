from __future__ import annotations

import click

from kitchenowl_cli.commands.auth import auth
from kitchenowl_cli.commands.config_cmd import config_group
from kitchenowl_cli.commands.household import household
from kitchenowl_cli.commands.recipe import recipe
from kitchenowl_cli.commands.shoppinglist import shoppinglist
from kitchenowl_cli.commands.user import user


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """KitchenOwl API CLI."""


cli.add_command(auth)
cli.add_command(config_group)
cli.add_command(household)
cli.add_command(recipe)
cli.add_command(shoppinglist)
cli.add_command(user)


if __name__ == "__main__":
    cli()
