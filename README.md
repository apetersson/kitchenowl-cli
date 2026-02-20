# kitchenowl-cli

Command-line client for KitchenOwl's `/api` endpoints, covering auth, household, recipe, shopping list, and user workflows.

## Supported CLI surface

- `kitchenowl auth [login|logout|status|signup]` — JWT login with refresh, logout and signup helpers.  
- `kitchenowl config [show|set-default-household|server-settings]` — manage stored tokens/default household and inspect read-only server flags from `/api/health`.  
- `kitchenowl household [list|use|get|create|update|delete]` and `kitchenowl household member [list|add|remove]`.  
- `kitchenowl recipe [list|get|add|edit|delete]` with JSON/YAML payload support and flag-based editors, including ingredients management.  
- `kitchenowl shoppinglist [list|create|delete|items|add-item|add-item-by-name|suggested|remove-item]` plus the dedicated `remove-item` command to mark items done.  
- `kitchenowl user [list|get|search|create|update|delete]` for admins.
- `run_cli_e2e.sh` script exercises login, household creation, lists, recipes, planner, expenses, and optionally house cleanup.

## Install

Recommended for normal usage (installs globally via `pipx`):

```bash
pipx install kitchenowl-cli
```

The installed command is:

```bash
kitchenowl --help
```

For local development / modifying this CLI:

```bash
cd kitchenowl-cli
python3 -m pip install -e .
```

## Publish to PyPI via GitHub Actions

This repository includes `.github/workflows/publish.yml` for Trusted Publishing.

One-time setup:
- In PyPI, create a Trusted Publisher for this GitHub repository and workflow file.
- In GitHub, keep the repository public and allow Actions to run.

Release flow:

```bash
git tag v0.1.1
git push origin v0.1.1
```

Then create a GitHub Release for that tag (or publish from the Releases UI).  
When the release is published, the workflow builds and uploads `kitchenowl-cli` to PyPI.

## Quick start examples

```bash
kitchenowl auth login --server https://your-kitchenowl.example.com
# tip: both https://host and https://host/api are accepted
kitchenowl config server-settings
kitchenowl household list
kitchenowl household member list --household-id 42
kitchenowl household member add 17 --household-id 42 --admin
kitchenowl shoppinglist create "Weekly List" --household-id 42
kitchenowl shoppinglist add-item-by-name 12 Milk --description "2L"
kitchenowl shoppinglist remove-item 12 456 -y
kitchenowl recipe add --name "Tomato Soup" --description "Simple soup" --household-id 42 --yields 2 --time 25 --ingredient "Tomatoes|6 pcs|false" --ingredient "Salt|1 tsp|false"
kitchenowl recipe edit 123 --description "Updated" --ingredient "Basil|a handful|true"
kitchenowl recipe delete 123
kitchenowl user list
kitchenowl auth signup --username newuser --name "New User"
```

`auth login` / `auth signup` will always ask for the server URL when `--server` is not provided, using your last saved server as the default.

## Read-only server settings

Inspect the public read-only settings exposed by the server health endpoint (works without login if you pass `--server`):

```bash
kitchenowl config server-settings --server https://your-kitchenowl.example.com
kitchenowl config server-settings --json
```

This currently shows:
- `open_registration`
- `email_mandatory`
- `oidc_provider`
- `privacy_policy` (if configured)
- `terms` (if configured)

## File-based recipe editing

```bash
kitchenowl recipe add --household-id 1 --from-file recipe.yml
kitchenowl recipe edit 42 --from-file recipe.yml
```

Example `recipe.yml`:

```yaml
name: Tomato Soup
description: Simple soup
time: 25
cook_time: 20
prep_time: 5
yields: 2
visibility: 0
source: ""
items:
  - name: Blend
    description: Blend until smooth
    optional: false
ingredients:
  - name: Tomatoes
    description: 6 pcs
    optional: false
  - name: Salt
    description: 1 tsp
    optional: false
tags:
  - soup
  - vegetarian
```

## What’s not implemented yet

- Expense management via CLI wrappers (entries, categories, overview/balance).  
- Shopping list bulk operations (`clear`, multi-remove, file-based bulk add).  
- Dedicated category/tag discovery and management commands beyond current recipe/tag usage flows.  
- More advanced auth/admin workflows (OIDC login, password reset/email verification, token management, deeper server admin tooling) are still API-only.
