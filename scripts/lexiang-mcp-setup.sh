#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$SCRIPT_DIR/config.sh"

SECRETS_PATH="${REPO_ROOT}/config/system.secrets.json"
SYSTEM_CONFIG_PATH="${SYSTEM_CONFIG_PATH:-${REPO_ROOT}/config/system.json}"

WRITE_SECRETS=1
WRITE_MCP=1
CLI_TOKEN=""

usage() {
  echo "Usage: bash scripts/lexiang-mcp-setup.sh [--secrets-only | --mcp-only] [--token <lxmcp_...>]" >&2
  echo "  默认：写入 config/system.secrets.json（gitignore）并合并 ~/.cursor/mcp.json 的 lexiang 项。" >&2
  echo "  凭证：--token > 环境变量 LEXIANG_MCP_PERSONAL_TOKEN > 已有 system.secrets.json > 交互输入（需终端）。" >&2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --secrets-only)
      WRITE_SECRETS=1
      WRITE_MCP=0
      shift
      ;;
    --mcp-only)
      WRITE_SECRETS=0
      WRITE_MCP=1
      shift
      ;;
    --token)
      CLI_TOKEN="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

normalize_token() {
  local t="$1"
  t="${t#Bearer }"
  echo "$t" | tr -d '\r\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'
}

read_token_from_secrets_file() {
  [[ -f "$SECRETS_PATH" ]] || return 1
  python3 - <<PY
import json
from pathlib import Path
p = Path("$SECRETS_PATH")
try:
    d = json.loads(p.read_text(encoding="utf-8"))
    v = d.get("reportWorkflow", {}).get("lexiangMcpPersonalToken", "")
    v = str(v).strip()
    if v and not v.startswith("<") and "LEXIANG_MCP_PERSONAL_TOKEN" not in v:
        print(v)
except Exception:
    pass
PY
}

TOK=""
if [[ -n "$CLI_TOKEN" ]]; then
  TOK="$(normalize_token "$CLI_TOKEN")"
elif [[ -n "${LEXIANG_MCP_PERSONAL_TOKEN:-}" ]]; then
  TOK="$(normalize_token "$LEXIANG_MCP_PERSONAL_TOKEN")"
elif [[ -f "$SECRETS_PATH" ]] && s="$(read_token_from_secrets_file)" && [[ -n "$s" ]]; then
  TOK="$(normalize_token "$s")"
elif [[ -t 0 ]]; then
  read -r -s -p "乐享 MCP 个人凭证（lxmcp_...，输入不回显）: " TOKEN_INPUT
  echo "" >&2
  TOK="$(normalize_token "${TOKEN_INPUT:-}")"
else
  echo "未找到凭证：请设置 LEXIANG_MCP_PERSONAL_TOKEN、使用 --token，或先交互运行本脚本写入 system.secrets.json。" >&2
  exit 1
fi

if [[ -z "$TOK" ]]; then
  echo "凭证为空。" >&2
  exit 1
fi
if [[ "$TOK" == *"LEXIANG_MCP_PERSONAL_TOKEN"* ]] || [[ "$TOK" == *"<"* ]]; then
  echo "拒绝写入占位符，请提供真实 lxmcp_ 凭证。" >&2
  exit 1
fi

export SETUP_LEXIANG_TOKEN="$TOK"
export SECRETS_PATH

if [[ "$WRITE_SECRETS" -eq 1 ]]; then
  python3 - <<'PY'
import json
import os
from pathlib import Path
tok = os.environ["SETUP_LEXIANG_TOKEN"]
secrets = Path(os.environ["SECRETS_PATH"])
data = {}
if secrets.exists():
    data = json.loads(secrets.read_text(encoding="utf-8"))
data.setdefault("reportWorkflow", {})["lexiangMcpPersonalToken"] = tok
secrets.parent.mkdir(parents=True, exist_ok=True)
secrets.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("已写入:", secrets)
PY
  chmod 600 "$SECRETS_PATH" 2>/dev/null || true
fi

if [[ "$WRITE_MCP" -eq 1 ]]; then
  CURSOR_ROOT="$(read_system_config "shared.cursorRoot")"
  if [[ -z "$CURSOR_ROOT" ]]; then
    echo "shared.cursorRoot 为空，跳过 mcp.json。" >&2
    exit 1
  fi
  MCP_JSON="${CURSOR_ROOT}/mcp.json"
  export MCP_JSON SYSTEM_CONFIG_PATH
  python3 - <<'PY'
import json
import os
from pathlib import Path

mcp_path = Path(os.environ["MCP_JSON"])
tok = os.environ["SETUP_LEXIANG_TOKEN"]
sys_path = Path(os.environ["SYSTEM_CONFIG_PATH"])
base = json.loads(sys_path.read_text(encoding="utf-8"))
rw = base.get("reportWorkflow", {})
srv = rw.get("lexiangMcpServer") or {}
name = srv.get("name") or "lexiang"
url = srv.get("url")
transport = srv.get("transportType") or "streamable-http"
if not url:
    raise SystemExit("system.json 缺少 reportWorkflow.lexiangMcpServer.url")

data = {}
if mcp_path.exists():
    data = json.loads(mcp_path.read_text(encoding="utf-8"))
servers = data.setdefault("mcpServers", {})
servers[name] = {
    "enabled": True,
    "url": url,
    "transportType": transport,
    "headers": {"Authorization": f"Bearer {tok}"},
}
mcp_path.parent.mkdir(parents=True, exist_ok=True)
mcp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("已合并:", mcp_path, "→ mcpServers[" + name + "]")
PY
  echo "请重启 Cursor 或重载 MCP 使连接生效。" >&2
fi
