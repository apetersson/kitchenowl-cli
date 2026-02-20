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


def _parse_paid_for(entries: tuple[str, ...]) -> list[dict[str, int]]:
    parsed: list[dict[str, int]] = []
    for entry in entries:
        value = entry.strip()
        if not value:
            continue
        if ":" in value:
            raw_user, raw_factor = value.split(":", 1)
        else:
            raw_user, raw_factor = value, "1"
        try:
            user_id = int(raw_user)
            factor = int(raw_factor)
        except ValueError as exc:
            raise click.ClickException(
                f"Invalid --paid-for value `{entry}`. Use `user_id` or `user_id:factor`."
            ) from exc
        if factor <= 0:
            raise click.ClickException("`factor` in --paid-for must be greater than 0.")
        parsed.append({"id": user_id, "factor": factor})
    return parsed


def _print_expenses(expenses: list[dict[str, Any]], title: str) -> None:
    table = Table(title=title)
    table.add_column("ID", justify="right")
    table.add_column("Name")
    table.add_column("Amount", justify="right")
    table.add_column("Paid by")
    table.add_column("Date")
    table.add_column("Category")
    for expense in expenses:
        paid_by = expense.get("paid_by", {})
        category = expense.get("category", {})
        table.add_row(
            str(expense.get("id", "-")),
            str(expense.get("name", "-")),
            str(expense.get("amount", "-")),
            str(paid_by.get("name", paid_by.get("id", "-")) if isinstance(paid_by, dict) else paid_by),
            str(expense.get("date", "-")),
            str(category.get("name", "-") if isinstance(category, dict) else category or "-"),
        )
    console.print(table)


def _print_categories(categories: list[dict[str, Any]]) -> None:
    table = Table(title="Expense categories")
    table.add_column("ID", justify="right")
    table.add_column("Name")
    table.add_column("Color")
    table.add_column("Budget", justify="right")
    for category in categories:
        table.add_row(
            str(category.get("id", "-")),
            str(category.get("name", "-")),
            str(category.get("color", "-")),
            str(category.get("budget", "-")),
        )
    console.print(table)


@click.group("expense")
def expense() -> None:
    """Expense commands."""


@expense.command("list")
@click.option("--household-id", type=int, help="Override default household.")
@click.option("--view", type=int, help="Backend view filter.")
@click.option("--start-after-id", type=int, help="Start after expense ID.")
@click.option("--start-after-date", help="Start after date (YYYY-MM-DD).")
@click.option("--end-before-date", help="End before date (YYYY-MM-DD).")
@click.option("--search", help="Search query.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def list_expenses(
    household_id: int | None,
    view: int | None,
    start_after_id: int | None,
    start_after_date: str | None,
    end_before_date: str | None,
    search: str | None,
    as_json: bool,
) -> None:
    """List household expenses."""
    client, cfg = _client_and_config()
    hid = _resolve_household(cfg, household_id)

    params: dict[str, Any] = {}
    if view is not None:
        params["view"] = view
    if start_after_id is not None:
        params["startAfterId"] = start_after_id
    if start_after_date:
        params["startAfterDate"] = _date_to_epoch_ms(start_after_date)
    if end_before_date:
        params["endBeforeDate"] = _date_to_epoch_ms(end_before_date)
    if search:
        params["search"] = search

    try:
        data = client.get(f"/api/household/{hid}/expense", params=params or None)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return

    if not data:
        console.print("No expenses found.")
        return
    _print_expenses(data, f"Expenses (household {hid})")


@expense.command("create")
@click.option("--household-id", type=int, help="Override default household.")
@click.option("--name", required=True)
@click.option("--amount", type=float, required=True)
@click.option("--paid-by", type=int, required=True, help="User ID that paid.")
@click.option("--paid-for", "paid_for", multiple=True, required=True, help="`user_id` or `user_id:factor`.")
@click.option("--description")
@click.option("--date", "date_value", help="Expense date (YYYY-MM-DD).")
@click.option("--category", type=int, help="Expense category ID.")
@click.option(
    "--exclude-from-statistics/--include-in-statistics",
    default=None,
    help="Exclude this expense from statistics calculations.",
)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def create_expense(
    household_id: int | None,
    name: str,
    amount: float,
    paid_by: int,
    paid_for: tuple[str, ...],
    description: str | None,
    date_value: str | None,
    category: int | None,
    exclude_from_statistics: bool | None,
    as_json: bool,
) -> None:
    """Create an expense."""
    client, cfg = _client_and_config()
    hid = _resolve_household(cfg, household_id)

    payload: dict[str, Any] = {
        "name": name,
        "amount": amount,
        "paid_by": {"id": paid_by},
        "paid_for": _parse_paid_for(paid_for),
    }
    if description is not None:
        payload["description"] = description
    if date_value:
        payload["date"] = _date_to_epoch_ms(date_value)
    if category is not None:
        payload["category"] = category
    if exclude_from_statistics is not None:
        payload["exclude_from_statistics"] = exclude_from_statistics

    try:
        data = client.post(f"/api/household/{hid}/expense", json=payload)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return
    console.print(f"[green]Created expense {data.get('id', '-')}.[/green]")


@expense.command("update")
@click.argument("expense_id", type=int)
@click.option("--name")
@click.option("--amount", type=float)
@click.option("--paid-by", type=int, help="User ID that paid.")
@click.option("--paid-for", "paid_for", multiple=True, help="`user_id` or `user_id:factor`.")
@click.option("--description")
@click.option("--date", "date_value", help="Expense date (YYYY-MM-DD).")
@click.option("--category", type=int, help="Expense category ID.")
@click.option("--clear-category", is_flag=True, help="Remove assigned category.")
@click.option(
    "--exclude-from-statistics/--include-in-statistics",
    default=None,
    help="Exclude this expense from statistics calculations.",
)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def update_expense(
    expense_id: int,
    name: str | None,
    amount: float | None,
    paid_by: int | None,
    paid_for: tuple[str, ...],
    description: str | None,
    date_value: str | None,
    category: int | None,
    clear_category: bool,
    exclude_from_statistics: bool | None,
    as_json: bool,
) -> None:
    """Update an expense."""
    client, _ = _client_and_config()
    payload: dict[str, Any] = {}
    if name is not None:
        payload["name"] = name
    if amount is not None:
        payload["amount"] = amount
    if paid_by is not None:
        payload["paid_by"] = {"id": paid_by}
    if paid_for:
        payload["paid_for"] = _parse_paid_for(paid_for)
    if description is not None:
        payload["description"] = description
    if date_value:
        payload["date"] = _date_to_epoch_ms(date_value)
    if category is not None:
        payload["category"] = category
    if clear_category:
        payload["category"] = None
    if exclude_from_statistics is not None:
        payload["exclude_from_statistics"] = exclude_from_statistics
    if not payload:
        raise click.ClickException("No update fields provided.")

    try:
        data = client.post(f"/api/expense/{expense_id}", json=payload)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return
    console.print(f"[green]Updated expense {expense_id}.[/green]")


@expense.command("delete")
@click.argument("expense_id", type=int)
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation.")
def delete_expense(expense_id: int, yes: bool) -> None:
    """Delete an expense."""
    if not yes and not click.confirm(f"Delete expense {expense_id}?", default=False):
        raise click.ClickException("Aborted.")
    client, _ = _client_and_config()
    try:
        client.delete(f"/api/expense/{expense_id}")
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc
    console.print(f"[green]Deleted expense {expense_id}.[/green]")


@expense.group("category")
def expense_category() -> None:
    """Expense category commands."""


@expense_category.command("list")
@click.option("--household-id", type=int, help="Override default household.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def list_expense_categories(household_id: int | None, as_json: bool) -> None:
    """List expense categories."""
    client, cfg = _client_and_config()
    hid = _resolve_household(cfg, household_id)
    try:
        data = client.get(f"/api/household/{hid}/expense/categories")
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return
    if not data:
        console.print("No expense categories found.")
        return
    _print_categories(data)


@expense_category.command("create")
@click.option("--household-id", type=int, help="Override default household.")
@click.option("--name", required=True)
@click.option("--color", type=int, default=0, show_default=True)
@click.option("--budget", type=float)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def create_expense_category(
    household_id: int | None,
    name: str,
    color: int,
    budget: float | None,
    as_json: bool,
) -> None:
    """Create an expense category."""
    client, cfg = _client_and_config()
    hid = _resolve_household(cfg, household_id)
    payload: dict[str, Any] = {"name": name, "color": color}
    if budget is not None:
        payload["budget"] = budget
    try:
        data = client.post(f"/api/household/{hid}/expense/categories", json=payload)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return
    console.print(f"[green]Created expense category {data.get('id', '-')} ({data.get('name', '-')}).[/green]")


@expense.command("overview")
@click.option("--household-id", type=int, help="Override default household.")
@click.option("--view", type=int)
@click.option("--frame", type=int)
@click.option("--steps", type=int)
@click.option("--page", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def overview_expenses(
    household_id: int | None,
    view: int | None,
    frame: int | None,
    steps: int | None,
    page: int | None,
    as_json: bool,
) -> None:
    """Show expense overview aggregates."""
    client, cfg = _client_and_config()
    hid = _resolve_household(cfg, household_id)
    params: dict[str, Any] = {}
    if view is not None:
        params["view"] = view
    if frame is not None:
        params["frame"] = frame
    if steps is not None:
        params["steps"] = steps
    if page is not None:
        params["page"] = page

    try:
        data = client.get(f"/api/household/{hid}/expense/overview", params=params or None)
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return
    if not data:
        console.print("No overview data found.")
        return
    console.print(json.dumps(data, indent=2, sort_keys=True))


@expense.command("balance")
@click.option("--household-id", type=int, help="Override default household.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
def recalculate_balances(household_id: int | None, as_json: bool) -> None:
    """Recalculate household expense balances (admin only)."""
    client, cfg = _client_and_config()
    hid = _resolve_household(cfg, household_id)
    try:
        data = client.get(f"/api/household/{hid}/expense/recalculate-balances")
    except ApiError as exc:
        raise click.ClickException(str(exc)) from exc

    if as_json:
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return
    console.print(f"[green]Recalculated expense balances for household {hid}.[/green]")
