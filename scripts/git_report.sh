#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"
DEFAULT_REPO_ROOT="$(read_system_config "shared.repoRoot")"

REPO_ROOT="$DEFAULT_REPO_ROOT"
PATHS_INPUT=""
COMMIT_MESSAGE=""

usage() {
  echo "Usage: bash scripts/git_report.sh --paths \"<path1> <path2> ...\" --message \"<commit-message>\" [--repo-root <path>]"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --paths)
      PATHS_INPUT="$2"
      shift 2
      ;;
    --message)
      COMMIT_MESSAGE="$2"
      shift 2
      ;;
    --repo-root)
      REPO_ROOT="$2"
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

if [[ -z "$PATHS_INPUT" || -z "$COMMIT_MESSAGE" ]]; then
  usage >&2
  exit 1
fi

if [[ -z "$REPO_ROOT" ]]; then
  echo "系统配置缺少 shared.repoRoot，请优先提供。" >&2
  exit 1
fi

cd "$REPO_ROOT"

read -r -a TARGET_PATHS <<< "$PATHS_INPUT"

echo "Target status:"
git status --short -- "${TARGET_PATHS[@]}"

if [[ -z "$(git status --short -- "${TARGET_PATHS[@]}")" ]]; then
  echo "No changes to commit for the given paths."
  exit 0
fi

git add -- "${TARGET_PATHS[@]}"
git commit -m "$COMMIT_MESSAGE"

echo
echo "Latest commit:"
git log -1 --stat --oneline
echo
echo "Branch status:"
git status --short --branch
