# kitchenowl-cli

Command-line client for KitchenOwl's `/api` endpoints, covering auth, household, recipe, shopping list, and user workflows.

## Supported CLI surface

- `kitchenowl auth [login|logout|status|signup]` — JWT login with refresh, logout and signup helpers.  
- `kitchenowl category [list]` and `kitchenowl tag [list]` — discovery commands for household categories and tags.
- `kitchenowl config [show|set-default-household|server-settings]` — manage stored tokens/default household and inspect read-only server flags from `/api/health`.  
- `kitchenowl expense [list|create|update|delete|overview|balance]` and `kitchenowl expense category [list|create]`.
- `kitchenowl household [list|use|get|create|update|delete]` and `kitchenowl household member [list|add|remove]`.  
- `kitchenowl planner [list|add-recipe|remove-recipe|recent-recipes|suggested-recipes|refresh-suggestions]`.
- `kitchenowl recipe [list|get|add|edit|delete]` with JSON/YAML payload support and flag-based editors, including ingredients management.  
- `kitchenowl recipe [search|search-by-tag]` for discovery and filtering.
- `kitchenowl shoppinglist [list|create|delete|items|add-item|add-item-by-name|add-items-from-file|suggested|remove-item|remove-items|clear]`.  
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

For test/development dependencies:

```bash
cd kitchenowl-cli
uv sync --extra dev
uv run pytest
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
kitchenowl shoppinglist remove-items 12 456 457 -y
kitchenowl shoppinglist clear 12 -y
kitchenowl recipe add --name "Tomato Soup" --description "Simple soup" --household-id 42 --yields 2 --time 25 --ingredient "Tomatoes|6 pcs|false" --ingredient "Salt|1 tsp|false"
kitchenowl recipe edit 123 --description "Updated" --ingredient "Basil|a handful|true"
kitchenowl recipe search --household-id 42 --query soup
kitchenowl recipe search-by-tag --tag vegetarian
kitchenowl recipe delete 123
kitchenowl planner add-recipe 123 --household-id 42 --date 2026-02-20
kitchenowl expense create --household-id 42 --name "Groceries" --amount 35.5 --paid-by 17 --paid-for 17:1 --paid-for 21:1
kitchenowl expense overview --household-id 42 --view 0 --frame 2
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

- Advanced category/tag management commands (create/update/delete/merge) beyond discovery/listing.  
- More advanced auth/admin workflows (OIDC login, password reset/email verification, token management, deeper server admin tooling) are still API-only.
- Data portability and advanced media workflows (import/export wrappers, upload helpers, recipe scraping shortcuts) are still API-only.

## Troubleshooting

- `No server configured` or `Not authenticated`:
  Run `kitchenowl auth login` and confirm `kitchenowl config show`.
- Network/transport failures:
  The CLI now wraps transport errors as user-facing messages. Verify server URL, DNS, and connectivity.
- Corrupted config file:
  The CLI defensively recovers malformed config content, but you can reset with:
  `rm ~/.config/kitchenowl/config.json` and re-login.
- Token refresh edge cases in concurrent CLI usage:
  Retry the command once; if refresh token rotation invalidates the session chain, run `kitchenowl auth login` again.

## Release Notes (v0.2 Progress)

- Stability and blocker fixes:
  - Recipe edit payload handling corrected to avoid stale item overwrite behavior.
  - Transport-level request failures now surface through `ApiError` with cleaner CLI messages.
  - User command init/auth/config error handling aligned with Click-friendly failures.
  - Config parsing hardened for malformed JSON and invalid key types.
  - Signup prompt semantics and e2e admin lookup behavior fixed.
- New command surfaces:
  - Planner command group.
  - Expense command group with category/overview/balance flows.
  - Recipe search and search-by-tag commands.
  - Shopping list bulk operations.
  - Category/tag discovery listing commands.
- Scope split:
  - Core blocker/stability and main CLI surfaces are implemented.
  - Remaining advanced admin/auth/data workflows are tracked for follow-up releases.
