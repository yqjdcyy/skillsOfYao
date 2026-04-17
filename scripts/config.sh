#!/usr/bin/env bash
set -euo pipefail

CONFIG_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_REPO_ROOT="$(cd "$CONFIG_SCRIPT_DIR/.." && pwd)"
SYSTEM_CONFIG_PATH="${SYSTEM_CONFIG_PATH:-${CONFIG_REPO_ROOT}/config/system.json}"

require_system_config() {
  if [[ ! -f "$SYSTEM_CONFIG_PATH" ]]; then
    echo "缺少系统配置文件: $SYSTEM_CONFIG_PATH" >&2
    echo "请优先提供并创建该配置文件后再执行。" >&2
    exit 1
  fi
}

read_system_config() {
  local key="$1"
  require_system_config
  python3 - <<'PY' "$SYSTEM_CONFIG_PATH" "$key"
import json
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
key = sys.argv[2]
data = json.loads(config_path.read_text(encoding="utf-8"))
value = data
for part in key.split("."):
    if isinstance(value, dict) and part in value:
        value = value[part]
    else:
        print("")
        raise SystemExit(0)

if isinstance(value, list):
    print(" ".join(str(item) for item in value))
elif value is None:
    print("")
else:
    print(str(value))
PY
}

read_system_config_lines() {
  local key="$1"
  require_system_config
  python3 - <<'PY' "$SYSTEM_CONFIG_PATH" "$key"
import json
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
key = sys.argv[2]
data = json.loads(config_path.read_text(encoding="utf-8"))
value = data
for part in key.split("."):
    if isinstance(value, dict) and part in value:
        value = value[part]
    else:
        raise SystemExit(0)

if isinstance(value, list):
    for item in value:
        print(str(item))
elif value is None:
    raise SystemExit(0)
else:
    print(str(value))
PY
}
