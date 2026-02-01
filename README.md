# kitchenowl-cli

Command-line client for KitchenOwl's `/api` endpoints, covering auth, household, recipe, shopping list, and user workflows.

## Supported CLI surface

- `kitchenowl auth [login|logout|status|signup]` — JWT login with refresh, logout and signup helpers.  
- `kitchenowl config [show|set-default-household]` — manage stored tokens/default household.  
- `kitchenowl household [list|use|get|create|update|delete]` and `kitchenowl household member [list|add|remove]`.  
- `kitchenowl recipe [list|get|add|edit|delete]` with JSON/YAML payload support and flag-based editors.  
- `kitchenowl shoppinglist [list|create|delete|items|add-item|add-item-by-name|suggested|remove-item]` plus the dedicated `remove-item` command to mark items done.  
- `kitchenowl user [list|get|search|create|update|delete]` for admins.
- `run_cli_e2e.sh` script exercises login, household creation, lists, recipes, planner, expenses, and optionally house cleanup.

## Quick install

```bash
cd /Users/andreas/Documents/code/kitchenowl/kitchenowl-cli
python3 -m pip install -e .
```

## Quick start examples

```bash
kitchenowl auth login --server https://your-kitchenowl.example.com
kitchenowl household list
kitchenowl household member list --household-id 42
kitchenowl household member add 17 --household-id 42 --admin
kitchenowl shoppinglist create "Weekly List" --household-id 42
kitchenowl shoppinglist add-item-by-name 12 Milk --description "2L"
kitchenowl shoppinglist remove-item 12 456 -y
kitchenowl recipe add --name "Tomato Soup" --description "Simple soup" --household-id 42 --yields 2 --time 25
kitchenowl recipe edit 123 --description "Updated"
kitchenowl recipe delete 123
kitchenowl user list
kitchenowl auth signup --username newuser --name "New User"
```

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

- Planner CLI commands (beyond the end-to-end script that calls `/planner/recipe`).  
- Expense management (create/edit/delete categories or entries) via CLI wrappers.  
- Shopping list item bulk operations (remove multiple items at once) and the planner suggestion refresh endpoints.  
- More advanced user workflows (password resets, token management, server admin tooling) are still API-only.
