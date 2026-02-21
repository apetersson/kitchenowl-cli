#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$ROOT_DIR" ]]; then
  ROOT_DIR="$SCRIPT_DIR"
fi
PACKAGE_DIR="$SCRIPT_DIR"
PACKAGE_NAME="kitchenowl-cli"

usage() {
  cat <<EOF
Usage: tag-and-push.sh [--allow-any-branch] [major|minor|patch|<version>|v<version>]

Bumps the $PACKAGE_NAME version, commits, tags, and pushes.
Default bump is patch if no argument is provided.
Use a literal version (e.g. v0.1.6 or 0.1.6) to force that number.
By default this script must be run from the main branch.
EOF
  exit 1
}

allow_any_branch=false
bump_input=""
for arg in "$@"; do
  case "$arg" in
    --allow-any-branch)
      allow_any_branch=true
      ;;
    -h|--help)
      usage
      ;;
    *)
      if [[ -n "$bump_input" ]]; then
        echo "Unexpected argument: $arg"
        usage
      fi
      bump_input="$arg"
      ;;
  esac
done

arg=${bump_input:-patch}
bump_type=""
direct_version=""
if [[ "$arg" =~ ^(major|minor|patch)$ ]]; then
  bump_type=$arg
elif [[ "$arg" =~ ^v?([0-9]+\.[0-9]+\.[0-9]+)$ ]]; then
  direct_version=${BASH_REMATCH[1]}
else
  echo "Invalid bump type or version: $arg"
  usage
fi

cd "$ROOT_DIR"
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$allow_any_branch" != true && "$current_branch" != "main" ]]; then
  echo "Releases must be created from the main branch. Current branch: $current_branch. Re-run with --allow-any-branch to override this check."
  exit 1
fi

PACKAGE_REL=$(python3 - <<PY
import os
print(os.path.relpath("$PACKAGE_DIR", "$ROOT_DIR"))
PY
)
if [[ "$PACKAGE_REL" == "." ]]; then
  PACKAGE_PREFIX=""
else
  PACKAGE_PREFIX="$PACKAGE_REL/"
fi
SCHEMA_FILES=(
  "${PACKAGE_PREFIX}pyproject.toml"
  "${PACKAGE_PREFIX}kitchenowl_cli/__init__.py"
)

if [[ -n $(git status --porcelain) ]]; then
  echo "Working tree is dirty. Please commit or stash your changes first."
  exit 1
fi

cd "$PACKAGE_DIR"
current_version=$(python3 - <<'PY'
import tomllib, pathlib
path = pathlib.Path('pyproject.toml')
data = tomllib.loads(path.read_text())
print(data['project']['version'])
PY
)

if [[ -n "$direct_version" ]]; then
  new_version="$direct_version"
else
  IFS='.' read -r -a parts <<< "$current_version"
  while [[ ${#parts[@]} -lt 3 ]]; do
    parts+=(0)
  done
  major=${parts[0]}
  minor=${parts[1]}
  patch=${parts[2]}

  case "$bump_type" in
    major)
      major=$((major + 1))
      minor=0
      patch=0
      ;;
    minor)
      minor=$((minor + 1))
      patch=0
      ;;
    patch)
      patch=$((patch + 1))
      ;;
  esac

  new_version="$major.$minor.$patch"
fi

python3 - <<PY
from pathlib import Path
pyproject = Path('pyproject.toml')
text = pyproject.read_text()
old = 'version = "' + "$current_version" + '"'
new = 'version = "' + "$new_version" + '"'
if old not in text:
    raise SystemExit('Unable to locate version line in pyproject.toml')
pyproject.write_text(text.replace(old, new, 1))
PY

python3 - <<PY
from pathlib import Path
import re
init_file = Path('kitchenowl_cli/__init__.py')
text = init_file.read_text()
new = '__version__ = "' + "$new_version" + '"'
pattern = r"__version__\s*=\s*[\"'].*[\"']"
if not re.search(pattern, text):
    raise SystemExit('Unable to locate __version__ line in __init__.py')
text = re.sub(pattern, new, text, count=1)
init_file.write_text(text)
PY

cd "$ROOT_DIR"
modified_files=()
while IFS= read -r file; do
  [[ -n "$file" ]] && modified_files+=("$file")
done < <(
  {
    git diff --name-only
    git diff --name-only --cached
  } | awk 'NF' | sort -u
)

untracked_files=()
while IFS= read -r file; do
  [[ -n "$file" ]] && untracked_files+=("$file")
done < <(git ls-files --others --exclude-standard)
unexpected_changes=()

for file in "${modified_files[@]+"${modified_files[@]}"}"; do
  [[ -n "$file" ]] || continue
  is_expected=false
  for expected_file in "${SCHEMA_FILES[@]}"; do
    if [[ "$file" == "$expected_file" ]]; then
      is_expected=true
      break
    fi
  done

  if [[ "$is_expected" != true ]]; then
    unexpected_changes+=("$file")
  fi
done

for file in "${untracked_files[@]+"${untracked_files[@]}"}"; do
  [[ -n "$file" ]] || continue
  unexpected_changes+=("$file")
done

if (( ${#unexpected_changes[@]} > 0 )); then
  echo "Unexpected working tree changes detected after rewriting files:"
  printf '  %s\n' "${unexpected_changes[@]}"
  echo "Please clean your working tree and try again."
  exit 1
fi

git add "${SCHEMA_FILES[@]}"
commit_message="chore: bump $PACKAGE_NAME to $new_version"
git commit -m "$commit_message"
tag_name="v$new_version"
git tag -a "$tag_name" -m "Release $PACKAGE_NAME $new_version"
git push origin HEAD
git push origin "$tag_name"

echo "Released $PACKAGE_NAME $new_version"
