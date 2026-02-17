#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./run_cli_e2e.sh -u USERNAME -p PASSWORD [-s SERVER] [--delete]

  -u USERNAME    KitchenOwl username/email
  -p PASSWORD    KitchenOwl password
  -s SERVER      KitchenOwl server base URL
  --delete       Delete the household after the test so you can inspect the run before cleanup

Example:
  ./run_cli_e2e.sh -u test_user -p password --delete
EOF
  exit 1
}

#SERVER="https://testing-server.exmple"
DELETE_HOUSEHOLD=false

while [[ $# -gt 0 ]]; do
  case $1 in
    -u|--user)
      USERNAME="$2"
      shift 2
      ;;
    -p|--password)
      PASSWORD="$2"
      shift 2
      ;;
    -s|--server)
      SERVER="$2"
      shift 2
      ;;
    --delete)
      DELETE_HOUSEHOLD=true
      shift
      ;;
    *)
      usage
      ;;
  esac
done

if [[ -z "${USERNAME:-}" || -z "${PASSWORD:-}" ]]; then
  usage
fi

CLI="./.venv/bin/kitchenowl"

echo "Logging in to $SERVER"
$CLI auth login --server "$SERVER" --username "$USERNAME" --password "$PASSWORD"

TOKEN_DATA=$(python3 - <<'PY'
import json
from pathlib import Path

cfg = Path.home() / ".config" / "kitchenowl" / "config.json"
data = json.loads(cfg.read_text())
print(data["access_token"])
print(data["user"]["id"])
PY
)
ACCESS_TOKEN=$(printf "%s\n" "$TOKEN_DATA" | sed -n '1p')
USER_ID=$(printf "%s\n" "$TOKEN_DATA" | sed -n '2p')

HH_NAME="CLI Test Run $(date +%Y%m%d-%H%M%S)"
HH_JSON=$($CLI household create --name "$HH_NAME" --description "CLI e2e household" --use --json)
HH_ID=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["id"])' "$HH_JSON")
echo "Created household $HH_ID ($HH_NAME)"

ADMIN_JSON=$($CLI user search --query admin --json 2>/tmp/cli_user_search.json || true)
ADMIN_ID=$(python3 - <<'PY'
import json,sys
data=sys.stdin.read().strip()
if not data:
    print("1")
    sys.exit(0)
try:
    users=json.loads(data)
except Exception:
    print("1")
else:
    if isinstance(users, list) and users:
        print(users[0]["id"])
    else:
        print("1")
PY
<<<"$ADMIN_JSON")
echo "Granting admin user $ADMIN_ID admin rights on household $HH_ID"
curl -sS -X PUT "$SERVER/api/household/$HH_ID/member/$ADMIN_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"admin":true}' >/tmp/cli_admin_member.json
echo "Admin assignment response: $(cat /tmp/cli_admin_member.json)"

LIST_JSON=$($CLI shoppinglist create "CLI Grocery List" --household-id "$HH_ID" --json)
LIST_ID=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["id"])' "$LIST_JSON")
echo "Created shopping list $LIST_ID"

for ITEM in Milk Bread Eggs; do
  $CLI shoppinglist add-item-by-name "$LIST_ID" "$ITEM" --description "Test item" >/tmp/cli_item.log
done

RECIPE1_JSON=$($CLI recipe add --household-id "$HH_ID" \
  --name "CLI Flag Recipe" \
  --description "Scripted via run_cli_e2e" \
  --time 30 \
  --yields 4 \
  --tag cli \
  --item "Lettuce|1 head|false" \
  --json)
RECIPE1_ID=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["id"])' "$RECIPE1_JSON")
echo "Created recipe #$RECIPE1_ID"

cat <<'EOF' >/tmp/run_cli_recipe.yml
name: CLI File Recipe
description: Created from YAML
time: 45
cook_time: 35
prep_time: 10
yields: 6
visibility: 0
items:
  - name: Tomato
    description: 3
    optional: false
tags:
  - file
  - cli
EOF

RECIPE2_JSON=$($CLI recipe add --household-id "$HH_ID" --from-file /tmp/run_cli_recipe.yml --json)
RECIPE2_ID=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["id"])' "$RECIPE2_JSON")
echo "Created recipe #$RECIPE2_ID from file"

TOKEN_DATA=$(python3 - <<'PY'
import json
from pathlib import Path

cfg = Path.home() / ".config" / "kitchenowl" / "config.json"
data = json.loads(cfg.read_text())
print(data["access_token"])
print(data["user"]["id"])
PY
)
ACCESS_TOKEN=$(printf "%s\n" "$TOKEN_DATA" | sed -n '1p')
USER_ID=$(printf "%s\n" "$TOKEN_DATA" | sed -n '2p')
CURL_OPTS=(-sS -H "Authorization: Bearer $ACCESS_TOKEN" -H "Content-Type: application/json")
DATE_MS=$(( $(date +%s) * 1000 ))

curl "${CURL_OPTS[@]}" -X POST "$SERVER/api/household/$HH_ID/planner/recipe" \
  -d "{\"recipe_id\":$RECIPE1_ID,\"cooking_date\":$DATE_MS}" >/tmp/plan.json
echo "Planned recipe $RECIPE1_ID for household $HH_ID"

curl "${CURL_OPTS[@]}" -X POST "$SERVER/api/household/$HH_ID/expense" \
  -d "{\"name\":\"CLI Test Expense\",\"amount\":12.50,\"paid_by\":{\"id\":$USER_ID},\"paid_for\":[{\"id\":$USER_ID}],\"date\":$DATE_MS}" >/tmp/expense.json
echo "Logged expense for household $HH_ID"

echo
echo "Summary"
echo "  Household ID: $HH_ID"
echo "  Shopping list ID: $LIST_ID"
echo "  Recipes: $RECIPE1_ID, $RECIPE2_ID"
echo "  Planner entry: $(cat /tmp/plan.json)"
echo "  Expense entry: $(cat /tmp/expense.json)"

if $DELETE_HOUSEHOLD; then
  echo "Deleting household $HH_ID"
  $CLI household delete "$HH_ID" -y
fi
