#!/usr/bin/env sh
set -eu

DATA_DIR="${DATA_DIR:-/app/data}"
LOG_DIR="${LOG_DIR:-/app/logs}"
SERVER_HOST="${SERVER_HOST:-0.0.0.0}"
SERVER_PORT="${SERVER_PORT:-8000}"
SERVER_WORKERS="${SERVER_WORKERS:-1}"
GROK2API_APP_KEY="${GROK2API_APP_KEY:-grok2api}"
GROK2API_API_KEY="${GROK2API_API_KEY:-}"
GROK2API_BASE_PROXY_URL="${GROK2API_BASE_PROXY_URL:-socks5://warp:1080}"
GROK2API_ASSET_PROXY_URL="${GROK2API_ASSET_PROXY_URL:-$GROK2API_BASE_PROXY_URL}"
GROK2API_BROWSER="${GROK2API_BROWSER:-chrome136}"
GROK2API_USER_AGENT="${GROK2API_USER_AGENT:-Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36}"
CONFIG_FILE="${DATA_DIR}/config.toml"

mkdir -p "$DATA_DIR" "$LOG_DIR"

if [ ! -s "$CONFIG_FILE" ]; then
cat >"$CONFIG_FILE" <<EOF
[app]
app_key = "${GROK2API_APP_KEY}"
api_key = "${GROK2API_API_KEY}"
temporary = true
disable_memory = true
stream = true
thinking = true

[proxy]
base_proxy_url = "${GROK2API_BASE_PROXY_URL}"
asset_proxy_url = "${GROK2API_ASSET_PROXY_URL}"
browser = "${GROK2API_BROWSER}"
user_agent = "${GROK2API_USER_AGENT}"
EOF
fi

if command -v python3 >/dev/null 2>&1; then
  PATCH_PYTHON=python3
else
  PATCH_PYTHON=python
fi

"$PATCH_PYTHON" /workspace/deploy/patch_grok2api_streaming.py

exec granian --interface asgi --host "${SERVER_HOST}" --port "${SERVER_PORT}" --workers "${SERVER_WORKERS}" main:app
