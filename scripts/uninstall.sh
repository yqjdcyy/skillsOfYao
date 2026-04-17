#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"
DEFAULT_REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEFAULT_CURSOR_ROOT="$(read_system_config "shared.cursorRoot")"

REPO_ROOT="$DEFAULT_REPO_ROOT"
CURSOR_ROOT="$DEFAULT_CURSOR_ROOT"

usage() {
  echo "Usage: bash scripts/uninstall.sh [--repo-root <path>] [--cursor-root <path>]"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --cursor-root)
      CURSOR_ROOT="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$CURSOR_ROOT" ]]; then
  echo "系统配置缺少 shared.cursorRoot，请优先提供。" >&2
  exit 1
fi

SKILLS_ROOT="${CURSOR_ROOT}/skills"
COMMANDS_ROOT="${CURSOR_ROOT}/commands"
REPO_REALPATH="$(python3 - <<'PY' "$REPO_ROOT"
from pathlib import Path
import sys
print(Path(sys.argv[1]).resolve())
PY
)"

declare -a REMOVED_SKILLS=()
declare -a REMOVED_COMMANDS=()
declare -a REMOVED_LOCAL_SKILLS=()
declare -a SKIPPED=()

belongs_to_repo() {
  local target_path="$1"
  python3 - <<'PY' "$target_path" "$REPO_REALPATH"
from pathlib import Path
import sys
target = Path(sys.argv[1]).resolve()
repo = Path(sys.argv[2]).resolve()
print(str(target).startswith(str(repo)))
PY
}

remove_links_in_dir() {
  local dir_path="$1"
  local label="$2"
  [[ -d "$dir_path" ]] || return 0

  while IFS= read -r -d '' entry; do
    [[ -L "$entry" ]] || continue
    if [[ "$(belongs_to_repo "$entry")" == "True" ]]; then
      rm "$entry"
      if [[ "$label" == "skill" ]]; then
        REMOVED_SKILLS+=("$entry")
      else
        REMOVED_COMMANDS+=("$entry")
      fi
    else
      SKIPPED+=("$entry")
    fi
  done < <(find "$dir_path" -maxdepth 1 -type l -print0)
}

remove_links_in_dir "$SKILLS_ROOT" "skill"
remove_links_in_dir "$COMMANDS_ROOT" "command"

while IFS= read -r local_skills_root; do
  [[ -n "$local_skills_root" ]] || continue
  [[ -d "$local_skills_root" ]] || continue

  while IFS= read -r -d '' entry; do
    [[ -L "$entry" ]] || continue
    if [[ "$(belongs_to_repo "$entry")" == "True" ]]; then
      rm "$entry"
      REMOVED_LOCAL_SKILLS+=("$entry")
    else
      SKIPPED+=("$entry")
    fi
  done < <(find "$local_skills_root" -maxdepth 1 -type l -print0)
done < <(read_system_config_lines "localExposure.projectSkillRoots")

echo "Uninstall summary"
echo "Removed skills: ${#REMOVED_SKILLS[@]}"
printf '  - %s\n' "${REMOVED_SKILLS[@]:-}"
echo "Removed commands: ${#REMOVED_COMMANDS[@]}"
printf '  - %s\n' "${REMOVED_COMMANDS[@]:-}"
echo "Removed local skills: ${#REMOVED_LOCAL_SKILLS[@]}"
printf '  - %s\n' "${REMOVED_LOCAL_SKILLS[@]:-}"
echo "Skipped external links: ${#SKIPPED[@]}"
printf '  - %s\n' "${SKIPPED[@]:-}"
