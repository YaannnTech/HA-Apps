#!/usr/bin/env bash
set -euo pipefail

get_option() {
    if [[ ! -r /data/options.json ]]; then
        echo "Unable to read /data/options.json; the app image must run as root" >&2
        exit 1
    fi

    python - "$1" "$2" <<'PY'
import json
import sys

with open("/data/options.json", encoding="utf-8") as options_file:
    options = json.load(options_file)

value = options.get(sys.argv[1], sys.argv[2])
if isinstance(value, bool):
    print(str(value).lower())
else:
    print(value)
PY
}

export HOST=0.0.0.0
export PORT=8880
export DEVICE_TYPE=cpu
export DOWNLOAD_MODEL=true
api_log_level="$(get_option api_log_level Info)"
export API_LOG_LEVEL="${api_log_level^^}"
# Upstream's entrypoint hardcodes uvicorn's --log-level debug, which logs every request,
# including the Supervisor watchdog's /health check every few seconds. Keep that request
# log for the Debug level only; uvicorn reads its options from UVICORN_* variables.
if [[ "${API_LOG_LEVEL}" != "DEBUG" ]]; then
    export UVICORN_ACCESS_LOG=false
fi
export DEFAULT_VOICE="$(get_option default_voice am_fenrir)"
export ENABLE_WEB_PLAYER="$(get_option enable_web_player true)"
export ENABLE_SSML="$(get_option enable_ssml true)"

cd /app
exec /app/entrypoint.sh
