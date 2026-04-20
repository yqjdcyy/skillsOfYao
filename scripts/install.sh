#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"
DEFAULT_REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEFAULT_CURSOR_ROOT="$(read_system_config "shared.cursorRoot")"
TIMESTAMP="$(date +%Y%m%d%H%M%S)"

REPO_ROOT="$DEFAULT_REPO_ROOT"
CURSOR_ROOT="$DEFAULT_CURSOR_ROOT"

usage() {
  echo "Usage: bash scripts/install.sh [--repo-root <path>] [--cursor-root <path>]"
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

mkdir -p "$SKILLS_ROOT" "$COMMANDS_ROOT"

declare -a INSTALLED_SKILLS=()
declare -a SKIPPED_SKILLS=()
declare -a INSTALLED_COMMANDS=()
declare -a SKIPPED_COMMANDS=()
declare -a RELINKED_LOCAL_SKILLS=()
declare -a SKIPPED_LOCAL_SKILLS=()
declare -a CONFLICTS=()

is_same_target() {
  local existing_target="$1"
  local expected_target="$2"
  [[ "$(python3 - <<'PY' "$existing_target" "$expected_target"
from pathlib import Path
import sys
print(Path(sys.argv[1]).resolve() == Path(sys.argv[2]).resolve())
PY
)" == "True" ]]
}

link_entry() {
  local source_path="$1"
  local target_path="$2"
  local label="$3"

  if [[ -L "$target_path" ]]; then
    local existing_target
    existing_target="$(readlink "$target_path")"
    if is_same_target "$existing_target" "$source_path"; then
      if [[ "$label" == "skill" ]]; then
        SKIPPED_SKILLS+=("$target_path")
      else
        SKIPPED_COMMANDS+=("$target_path")
      fi
      return 0
    fi
    CONFLICTS+=("$target_path -> $existing_target")
    return 1
  fi

  if [[ -e "$target_path" ]]; then
    CONFLICTS+=("$target_path (existing non-symlink)")
    return 1
  fi

  ln -s "$source_path" "$target_path"
  if [[ "$label" == "skill" ]]; then
    INSTALLED_SKILLS+=("$target_path")
  else
    INSTALLED_COMMANDS+=("$target_path")
  fi
}

relink_local_skill_entry() {
  local source_path="$1"
  local target_path="$2"

  if [[ -L "$target_path" ]]; then
    local existing_target
    existing_target="$(readlink "$target_path")"
    if is_same_target "$existing_target" "$source_path"; then
      SKIPPED_LOCAL_SKILLS+=("$target_path")
      return 0
    fi
    rm "$target_path"
  elif [[ -e "$target_path" ]]; then
    local backup_root
    backup_root="$(dirname "$target_path")/_backup_before_skillsOfYao_relink"
    mkdir -p "$backup_root"
    mv "$target_path" "$backup_root/$(basename "$target_path")-${TIMESTAMP}"
  fi

  ln -s "$source_path" "$target_path"
  RELINKED_LOCAL_SKILLS+=("$target_path")
}

while IFS= read -r -d '' skill_file; do
  skill_dir="$(dirname "$skill_file")"
  skill_name="$(basename "$skill_dir")"
  link_entry "$skill_dir" "${SKILLS_ROOT}/${skill_name}" "skill"
done < <(
  find \
    "${REPO_ROOT}/learning" \
    "${REPO_ROOT}/work" \
    "${REPO_ROOT}/work/document-output" \
    "${REPO_ROOT}/work/workflow" \
    "${REPO_ROOT}/life" \
    -mindepth 2 -maxdepth 2 -name SKILL.md -print0 2>/dev/null
)

while IFS= read -r -d '' command_file; do
  command_name="$(basename "$command_file")"
  link_entry "$command_file" "${COMMANDS_ROOT}/${command_name}" "command"
done < <(
  find "${REPO_ROOT}/commands" -type f -name '*.md' -print0 2>/dev/null
)

while IFS= read -r local_skills_root; do
  [[ -n "$local_skills_root" ]] || continue
  if [[ ! -d "$local_skills_root" ]]; then
    CONFLICTS+=("${local_skills_root} (configured local skill root missing)")
    continue
  fi

  while IFS= read -r -d '' skill_file; do
    skill_dir="$(dirname "$skill_file")"
    skill_name="$(basename "$skill_dir")"
    relink_local_skill_entry "$skill_dir" "${local_skills_root}/${skill_name}"
  done < <(
    find \
      "${REPO_ROOT}/learning" \
      "${REPO_ROOT}/work" \
      "${REPO_ROOT}/work/document-output" \
      "${REPO_ROOT}/work/workflow" \
      "${REPO_ROOT}/life" \
      -mindepth 2 -maxdepth 2 -name SKILL.md -print0 2>/dev/null
  )
done < <(read_system_config_lines "localExposure.projectSkillRoots")

if [[ ${#CONFLICTS[@]} -gt 0 ]]; then
  echo "Conflicts detected:" >&2
  printf '  - %s\n' "${CONFLICTS[@]}" >&2
  echo "Resolve conflicts manually, then rerun install.sh." >&2
  exit 1
fi

echo "Install summary"
echo "Installed skills: ${#INSTALLED_SKILLS[@]}"
printf '  - %s\n' "${INSTALLED_SKILLS[@]:-}"
echo "Skipped skills: ${#SKIPPED_SKILLS[@]}"
printf '  - %s\n' "${SKIPPED_SKILLS[@]:-}"
echo "Installed commands: ${#INSTALLED_COMMANDS[@]}"
printf '  - %s\n' "${INSTALLED_COMMANDS[@]:-}"
echo "Skipped commands: ${#SKIPPED_COMMANDS[@]}"
printf '  - %s\n' "${SKIPPED_COMMANDS[@]:-}"
echo "Relinked local skills: ${#RELINKED_LOCAL_SKILLS[@]}"
printf '  - %s\n' "${RELINKED_LOCAL_SKILLS[@]:-}"
echo "Skipped local skills: ${#SKIPPED_LOCAL_SKILLS[@]}"
printf '  - %s\n' "${SKIPPED_LOCAL_SKILLS[@]:-}"

echo ""
if [[ -t 0 ]]; then
  read -r -p "是否配置乐享 MCP 凭证（写入 config/system.secrets.json 并合并 Cursor mcp.json）？[y/N] " _lexiang_ans || true
  if [[ "${_lexiang_ans:-}" =~ ^[yY] ]]; then
    bash "$SCRIPT_DIR/lexiang-mcp-setup.sh" || echo "乐享 MCP 配置未成功，可稍后执行: bash scripts/lexiang-mcp-setup.sh" >&2
  fi
else
  echo "可选：bash scripts/lexiang-mcp-setup.sh   # 乐享 MCP 凭证（或设 LEXIANG_MCP_PERSONAL_TOKEN 后执行）"
fi
