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

read_lexiang_mcp_personal_token() {
  require_system_config
  export SYSTEM_CONFIG_PATH
  python3 - <<'PY'
import json
import os
from pathlib import Path

sys_path = Path(os.environ["SYSTEM_CONFIG_PATH"])
sec_path = sys_path.parent / "system.secrets.json"
tok = os.environ.get("LEXIANG_MCP_PERSONAL_TOKEN", "").strip()
if tok.lower().startswith("bearer "):
    tok = tok[7:].strip()
if not tok and sec_path.is_file():
    try:
        d = json.loads(sec_path.read_text(encoding="utf-8"))
        tok = str(d.get("reportWorkflow", {}).get("lexiangMcpPersonalToken", "")).strip()
        if tok.lower().startswith("bearer "):
            tok = tok[7:].strip()
    except Exception:
        tok = ""
if not tok:
    try:
        d = json.loads(sys_path.read_text(encoding="utf-8"))
        tok = str(d.get("reportWorkflow", {}).get("lexiangMcpPersonalToken", "")).strip()
        if tok.lower().startswith("bearer "):
            tok = tok[7:].strip()
    except Exception:
        tok = ""
if tok and ("<" in tok or "LEXIANG_MCP_PERSONAL_TOKEN" in tok):
    tok = ""
if tok:
    print(tok)
PY
}
