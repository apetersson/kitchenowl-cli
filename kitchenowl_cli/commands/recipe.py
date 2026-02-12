from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import click
import yaml
from rich.console import Console
from rich.table import Table

from kitchenowl_cli.api import ApiClient, ApiError
from kitchenowl_cli.config import load_config


console = Console()

ALLOWED_FIELDS = {
    "name",
    "description",
    "time",
    "cook_time",
    "prep_time",
    "yields",
    "source",
    "server_curated",
    "photo",
    "visibility",
    "items",
    "tags",
}


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _parse_item(item: str) -> dict[str, Any]:
    parts = [p.strip() for p in item.split("|")]
    if not parts or not parts[0]:
        raise click.ClickException(f"Invalid --item value `{item}`. Use `name|description|optional`.")
    parsed = {
        "name": parts[0],
        "description": "",
        "optional": True,
    }
    if len(parts) > 1 and parts[1]:
        parsed["description"] = parts[1]
    if len(parts) > 2 and parts[2]:
        parsed["optional"] = _as_bool(parts[2])
    return parsed


def _household_id(config: dict[str, Any], arg_household_id: int | None) -> int:
    value = arg_household_id or config.get("default_household")
    if not value:
        raise click.ClickException(
            "No household selected. Pass --household-id or run `kitchenowl household use <id>`."
        )
    return int(value)


def _load_payload_file(path: Path) -> dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(content)
    else:
        data = yaml.safe_load(content)
    if not isinstance(data, dict):
        raise click.ClickException(f"Payload in {path} must be an object/map.")
    return data


def _editable_recipe(recipe: dict[str, Any]) -> dict[str, Any]:
    data = {key: recipe.get(key) for key in ALLOWED_FIELDS if key in recipe}
    data["items"] = [
        {
            "name": item.get("name", ""),
            "description": item.get("description", ""),
            "optional": item.get("optional", True),
        }
        for item in recipe.get("items", [])
    ]
    data["tags"] = [tag["name"] if isinstance(tag, dict) else tag for tag in recipe.get("tags", [])]
    return data


def _normalize_payload(raw: dict[str, Any], *, for_update: bool) -> dict[str, Any]:
    payload = {k: v for k, v in raw.items() if k in ALLOWED_FIELDS and v is not None}
    if not for_update:
        payload.setdefault("description", "")
    if "items" in payload:
        if not isinstance(payload["items"], list):
            raise click.ClickException("`items` must be a list.")
        normalized_items: list[dict[str, Any]] = []
        for item in payload["items"]:
            if not isinstance(item, dict):
                raise click.ClickException("Each recipe item must be an object.")
            name = str(item.get("name", "")).strip()
            if not name:
                raise click.ClickException("Each recipe item requires a non-empty `name`.")
            normalized_items.append(
                {
                    "name": name,
                    "description": str(item.get("description", "")),
                    "optional": bool(item.get("optional", True)),
                }
            )
        payload["items"] = normalized_items
    if "tags" in payload:
        if not isinstance(payload["tags"], list):
            raise click.ClickException("`tags` must be a list.")
        payload["tags"] = [str(t).strip() for t in payload["tags"] if str(t).strip()]
    if not for_update:
        name = str(payload.get("name", "")).strip()
        if not name:
            raise click.ClickException("`name` is required for recipe creation.")
        payload["name"] = name
    return payload


def _print_recipe(recipe: dict[str, Any]) -> None:
    console.print(f"[bold]{recipe.get('name', '-')}[/bold] (id={recipe.get('id', '-')})")
    console.print(f"description: {recipe.get('description', '')}")
    console.print(
        "time: "
        f"{recipe.get('time', '-')}, prep: {recipe.get('prep_time', '-')}, "
        f"cook: {recipe.get('cook_time', '-')}, yields: {recipe.get('yields', '-')}"
    )
    console.print(f"visibility: {recipe.get('visibility', '-')}")
    console.print(f"source: {recipe.get('source', '-')}")

    tags = recipe.get("tags", [])
    if tags:
        tag_names = [t["name"] if isinstance(t, dict) else str(t) for t in tags]
        console.print(f"tags: {', '.join(tag_names)}")
    else:
        console.print("tags: -")

    items = recipe.get("items", [])
    if items:
        table = Table(title="Items")
        table.add_column("Name")
        table.add_column("Description")
        table.add_column("Optional")
        for item in items:
            table.add_row(
                str(item.get("name", "-")),
                str(item.get("description", "")),
                "yes" if item.get("optional", True) else "no",
            )
        console.print(table)
    else:
        console.print("items: -")


def _build_payload_from_flags(
    *,
    name: str | None,
    description: str | None,
    time: int | None,
    cook_time: int | None,
    prep_time: int | None,
    yields_value: int | None,
    source: str | None,
    visibility: int | None,
    tags: tuple[str, ...],
    items: tuple[str, ...],
    clear_tags: bool = False,
    clear_items: bool = False,
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if name is not None:
        payload["name"] = name
    if description is not None:
        payload["description"] = description
    if time is not None:
        payload["time"] = time
    if cook_time is not None:
        payload["cook_time"] = cook_time
    if prep_time is not None:
        payload["prep_time"] = prep_time
    if yields_value is not None:
        payload["yields"] = yields_value
    if source is not None:
        payload["source"] = source
    if visibility is not None:
        payload["visibility"] = visibility
    if clear_tags:
        payload["tags"] = []
    elif tags:
        payload["tags"] = list(tags)
    if clear_items:
        payload["items"] = []
    elif items:
        payload["items"] = [_parse_item(item) for item in items]
    return payload


@click.group()
def recipe() -> None:
    """Recipe commands."""


@recipe.command("list")
@click.option("--household-id", type=int, help="Override configured default household.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def list_recipes(household_id: int | None, as_json: bool) -> None:
    """List recipes in a household."""
    cfg = load_config()
    hid = _household_id(cfg, household_id)
    try:
        client = ApiClient(cfg)
        recipes = client.get(f"/api/household/{hid}/recipe")
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(recipes, indent=2, sort_keys=True))
        return

    table = Table(title=f"Recipes (household {hid})")
    table.add_column("ID", justify="right")
    table.add_column("Name")
    table.add_column("Yields", justify="right")
    table.add_column("Time", justify="right")
    table.add_column("Tags")
    table.add_column("Items", justify="right")

    for r in recipes:
        tags = r.get("tags", [])
        tag_names = [t.get("name", "-") if isinstance(t, dict) else str(t) for t in tags]
        table.add_row(
            str(r.get("id", "-")),
            str(r.get("name", "-")),
            str(r.get("yields", "-")),
            str(r.get("time", "-")),
            ", ".join(tag_names[:3]),
            str(len(r.get("items", []))),
        )
    console.print(table)


@recipe.command("get")
@click.argument("recipe_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def get_recipe(recipe_id: int, as_json: bool) -> None:
    """Get recipe details."""
    cfg = load_config()
    try:
        client = ApiClient(cfg)
        data = client.get(f"/api/recipe/{recipe_id}")
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return
    _print_recipe(data)


@recipe.command("add")
@click.option("--household-id", type=int, help="Override configured default household.")
@click.option("--name")
@click.option("--description")
@click.option("--time", type=int)
@click.option("--cook-time", type=int)
@click.option("--prep-time", type=int)
@click.option("--yields", "yields_value", type=int)
@click.option("--source")
@click.option("--visibility", type=int, help="0=private, 1=link, 2=public.")
@click.option("--tag", "tags", multiple=True, help="Repeatable recipe tag.")
@click.option("--item", "items", multiple=True, help="Repeatable: name|description|optional")
@click.option("--from-file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def add_recipe(
    household_id: int | None,
    name: str | None,
    description: str | None,
    time: int | None,
    cook_time: int | None,
    prep_time: int | None,
    yields_value: int | None,
    source: str | None,
    visibility: int | None,
    tags: tuple[str, ...],
    items: tuple[str, ...],
    from_file: Path | None,
    as_json: bool,
) -> None:
    """Create a recipe."""
    cfg = load_config()
    hid = _household_id(cfg, household_id)

    if from_file:
        raw_payload = _load_payload_file(from_file)
    else:
        flagged_payload = _build_payload_from_flags(
            name=name,
            description=description,
            time=time,
            cook_time=cook_time,
            prep_time=prep_time,
            yields_value=yields_value,
            source=source,
            visibility=visibility,
            tags=tags,
            items=items,
        )
        if flagged_payload:
            raw_payload = flagged_payload
        else:
            template = {
                "name": "",
                "description": "",
                "time": 0,
                "cook_time": 0,
                "prep_time": 0,
                "yields": 1,
                "visibility": 0,
                "source": "",
                "items": [],
                "tags": [],
            }
            edited = click.edit(yaml.safe_dump(template, sort_keys=False))
            if edited is None:
                raise click.ClickException("Aborted.")
            parsed = yaml.safe_load(edited)
            if not isinstance(parsed, dict):
                raise click.ClickException("Editor content must be a YAML object.")
            raw_payload = parsed

    payload = _normalize_payload(raw_payload, for_update=False)
    try:
        client = ApiClient(cfg)
        data = client.post(f"/api/household/{hid}/recipe", json=payload)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return
    console.print(f"[green]Created recipe {data.get('id')}.[/green]")
    _print_recipe(data)


@recipe.command("edit")
@click.argument("recipe_id", type=int)
@click.option("--name")
@click.option("--description")
@click.option("--time", type=int)
@click.option("--cook-time", type=int)
@click.option("--prep-time", type=int)
@click.option("--yields", "yields_value", type=int)
@click.option("--source")
@click.option("--visibility", type=int, help="0=private, 1=link, 2=public.")
@click.option("--tag", "tags", multiple=True, help="Repeatable recipe tag.")
@click.option("--item", "items", multiple=True, help="Repeatable: name|description|optional")
@click.option("--clear-tags", is_flag=True, help="Clear all tags.")
@click.option("--clear-items", is_flag=True, help="Clear all items.")
@click.option("--from-file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def edit_recipe(
    recipe_id: int,
    name: str | None,
    description: str | None,
    time: int | None,
    cook_time: int | None,
    prep_time: int | None,
    yields_value: int | None,
    source: str | None,
    visibility: int | None,
    tags: tuple[str, ...],
    items: tuple[str, ...],
    clear_tags: bool,
    clear_items: bool,
    from_file: Path | None,
    as_json: bool,
) -> None:
    """Edit an existing recipe."""
    cfg = load_config()
    try:
        client = ApiClient(cfg)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if from_file:
        raw_payload = _load_payload_file(from_file)
    else:
        flagged_payload = _build_payload_from_flags(
            name=name,
            description=description,
            time=time,
            cook_time=cook_time,
            prep_time=prep_time,
            yields_value=yields_value,
            source=source,
            visibility=visibility,
            tags=tags,
            items=items,
            clear_tags=clear_tags,
            clear_items=clear_items,
        )
        if flagged_payload:
            raw_payload = flagged_payload
        else:
            try:
                existing = client.get(f"/api/recipe/{recipe_id}")
            except ApiError as exc:
                raise click.ClickException(str(exc)) from exc
            editable = _editable_recipe(existing)
            edited = click.edit(yaml.safe_dump(editable, sort_keys=False))
            if edited is None:
                raise click.ClickException("Aborted.")
            parsed = yaml.safe_load(edited)
            if not isinstance(parsed, dict):
                raise click.ClickException("Editor content must be a YAML object.")
            raw_payload = parsed

    payload = _normalize_payload(raw_payload, for_update=True)
    if not payload:
        raise click.ClickException("No changes provided.")

    try:
        data = client.post(f"/api/recipe/{recipe_id}", json=payload)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return
    console.print(f"[green]Updated recipe {recipe_id}.[/green]")
    _print_recipe(data)


@recipe.command("delete")
@click.argument("recipe_id", type=int)
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt.")
def delete_recipe(recipe_id: int, yes: bool) -> None:
    """Delete a recipe."""
    if not yes and not click.confirm(f"Delete recipe {recipe_id}?", default=False):
        raise click.ClickException("Aborted.")

    cfg = load_config()
    try:
        client = ApiClient(cfg)
        client.delete(f"/api/recipe/{recipe_id}")
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    console.print(f"[green]Deleted recipe {recipe_id}.[/green]")
