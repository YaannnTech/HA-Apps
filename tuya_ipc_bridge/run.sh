#!/usr/bin/with-contenv bashio
set -e

DATA_DIR="/data"
mkdir -p "${DATA_DIR}"
cd "${DATA_DIR}"

RTSP_PORT=$(bashio::config 'rtsp_port')

# The Supervisor prefixes the config.yaml slug with a repository hash for apps installed
# from a custom repository (e.g. "45df7312_tuya_ipc_bridge"), so the panel path can't just
# be hardcoded from config.yaml - fetch the real slug Supervisor assigned instead. The
# panel path is "/app/<slug>" (not "/hassio/ingress/<slug>").
if ! ADDON_INFO=$(curl -fsS \
    -H "Authorization: Bearer ${SUPERVISOR_TOKEN}" \
    http://supervisor/addons/self/info); then
    bashio::log.error "Could not retrieve app information from the Supervisor"
    exit 1
fi
ADDON_SLUG=$(jq -r '.data.slug // "tuya_ipc_bridge"' <<< "${ADDON_INFO}")
if ! INGRESS_PORT=$(jq -er '.data.ingress_port' <<< "${ADDON_INFO}"); then
    bashio::log.error "Could not retrieve the assigned Home Assistant ingress port"
    exit 1
fi
if ! [[ "${INGRESS_PORT}" =~ ^[1-9][0-9]{0,4}$ ]] || (( INGRESS_PORT > 65535 )); then
    bashio::log.error "Supervisor returned an invalid ingress port: ${INGRESS_PORT}"
    exit 1
fi
WEB_UI_LINK="/app/${ADDON_SLUG}"

bashio::log.info "Refreshing camera discovery..."
tuya-ipc-terminal cameras refresh || bashio::log.warning "Camera discovery failed, continuing anyway"
tuya-ipc-terminal cameras list || true

bashio::log.info "Starting ingress web UI (QR login) on port ${INGRESS_PORT}..."
python3 /usr/bin/qr_server.py --port "${INGRESS_PORT}" &

# Calls the HA persistent_notification service through the Supervisor's Core API proxy
# (requires homeassistant_api: true in config.yaml, which injects SUPERVISOR_TOKEN).
notify_ha() {
    local service="$1" notification_id="$2" title="${3:-}" message="${4:-}"
    local payload
    if [ "${service}" = "create" ]; then
        payload=$(jq -n --arg id "${notification_id}" --arg title "${title}" --arg message "${message}" \
            '{notification_id: $id, title: $title, message: $message}')
    else
        payload=$(jq -n --arg id "${notification_id}" '{notification_id: $id}')
    fi
    curl -sf -X POST \
        -H "Authorization: Bearer ${SUPERVISOR_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "${payload}" \
        "http://supervisor/core/api/services/persistent_notification/${service}" >/dev/null 2>&1 || true
}

# Runs "auth test" for one account; its output can contain session data or a user ID.
AUTH_RETRY_DELAY=30
auth_test() {
    AUTH_TEST_OUTPUT=$(tuya-ipc-terminal auth test "$1" "$2" 2>&1 || true)
    grep -q "Session is valid" <<< "${AUTH_TEST_OUTPUT}"
}

auth_diagnostic() {
    local line body status details
    while IFS= read -r line; do
        if [[ "${line}" =~ HTTP\ error:\ ([0-9]{3})\ -\ (.*) ]]; then
            status="${BASH_REMATCH[1]}"
            body="${BASH_REMATCH[2]}"
            # Only numeric codes and known fixed messages are safe to echo from a server response.
            details=$(jq -sr 'if length != 1 or (.[0] | type) != "object" then empty else .[0] |
                (if (.errorCode | type) == "number" and
                    (.errorCode | tostring | test("^-?[0-9]{1,10}$"))
                 then " errorCode=" + (.errorCode | tostring)
                 elif (.errorCode | type) == "string" and
                    (.errorCode | test("^-?[0-9]{1,10}$"))
                 then " errorCode=" + .errorCode
                 elif has("errorCode") then " errorCode=[redacted]" else "" end) +
                (if has("errorMsg") then
                    " errorMsg=" + (if .errorMsg == "session expired" then "session expired"
                    elif .errorMsg == "invalid session" then "invalid session"
                    else "[redacted]" end)
                 else "" end) end' <<< "${body}" 2>/dev/null) || details=""
            printf 'HTTP error: %s%s\n' "${status}" "${details}"
            return
        elif [[ "${line}" == *"not found"* && "${line}" == *"User "* ]]; then
            echo "User not found"
            return
        elif [[ "${line}" == *"invalid session data"* ]]; then
            echo "Invalid session data"
            return
        elif [[ "${line}" == *"Failed to create HTTP client"* ]]; then
            echo "Failed to create HTTP client"
            return
        elif [[ "${line}" == *"Session is invalid"* ]]; then
            echo "Session is invalid"
            return
        elif [[ "${line}" == *"failed to get user"* ]]; then
            echo "Failed to get user"
            return
        fi
    done <<< "${AUTH_TEST_OUTPUT}"
    echo "no details"
}

# Periodically re-validates every stored session; QR/password logins expire after a few
# days, and this surfaces that as a Home Assistant notification instead of silent log spam.
# A failed test is retried once after a short pause, because a single check can fail for
# transient reasons (for example right after the app or the RTSP server started).
check_sessions() {
    local f REGION EMAIL NOTIF_ID valid
    for f in "${DATA_DIR}/.tuya-data"/user_*.json; do
        [ -e "${f}" ] || continue
        REGION=$(jq -r '.region' "${f}") || continue
        EMAIL=$(jq -r '.email' "${f}") || continue
        NOTIF_ID="tuya_ipc_bridge_reauth_$(echo "${REGION}_${EMAIL}" | tr -c 'a-zA-Z0-9' '_')"

        if auth_test "${REGION}" "${EMAIL}"; then
            valid=1
        else
            bashio::log.info "Session test failed for ${EMAIL} (${REGION}); retrying in ${AUTH_RETRY_DELAY} s"
            sleep "${AUTH_RETRY_DELAY}"
            valid=0
            ! auth_test "${REGION}" "${EMAIL}" || valid=1
        fi

        if [ "${valid}" -eq 1 ]; then
            notify_ha dismiss "${NOTIF_ID}"
        else
            bashio::log.warning "Session expired for ${EMAIL} (${REGION}); notifying Home Assistant"
            bashio::log.warning "auth test: $(auth_diagnostic)"
            notify_ha create "${NOTIF_ID}" "Tuya IPC Bridge: re-authentication needed" \
                "The Tuya session for **${EMAIL}** (${REGION}) has expired, so its cameras stopped streaming. [Open Tuya IPC Bridge](${WEB_UI_LINK}) and log in again."
        fi
    done
}

# Set by qr_server.py after a successful login in the web UI.
LOGIN_MARKER="${DATA_DIR}/.login-done"
LOGIN_PROCESSING="${DATA_DIR}/.login-processing"
RTSP_PID_FILE="${DATA_DIR}/.tuya-data/rtsp-${RTSP_PORT}.pid"

# The RTSP server refuses to start with zero authenticated users, so it can't
# just be exec'd here: accounts are only ever added later via the Web UI.
# Keep the app alive and (re)start the RTSP server once/whenever users exist.
RTSP_PID=""
SESSION_CHECK_INTERVAL=3600
# The first check runs a few minutes after the first RTSP start, not in the same
# loop pass: right after the start a check can fail although the session is fine.
# Failed RTSP starts must not postpone an already scheduled session check.
FIRST_SESSION_CHECK_DELAY=300
NEXT_SESSION_CHECK=0
NO_ACCOUNTS_NOTIFIED=0
NO_ACCOUNTS_NOTIF_ID="tuya_ipc_bridge_no_accounts"

start_rtsp() {
    bashio::log.info "Starting RTSP server on port ${RTSP_PORT}..."
    tuya-ipc-terminal cameras refresh || true
    tuya-ipc-terminal rtsp start --port "${RTSP_PORT}" &
    RTSP_PID=$!
    if [ "${NEXT_SESSION_CHECK}" -eq 0 ]; then
        NEXT_SESSION_CHECK=$(( $(date +%s) + FIRST_SESSION_CHECK_DELAY ))
    fi
}

# Stops the running RTSP server and waits until it has exited (SIGKILL after 20 s), so the
# new one can bind the port. The CLI ignores a stale pid file (it checks that the process
# is gone), but it is removed here anyway.
stop_rtsp() {
    if [ -n "${RTSP_PID}" ] && kill -0 "${RTSP_PID}" 2>/dev/null; then
        bashio::log.info "Stopping RTSP server..."
        kill "${RTSP_PID}" 2>/dev/null || true
        for _ in $(seq 1 40); do
            kill -0 "${RTSP_PID}" 2>/dev/null || break
            sleep 0.5
        done
        kill -9 "${RTSP_PID}" 2>/dev/null || true
        wait "${RTSP_PID}" 2>/dev/null || true
    fi
    RTSP_PID=""
    rm -f "${RTSP_PID_FILE}" || bashio::log.warning "Could not remove the RTSP pid file"
}

while true; do
    USER_COUNT=$(find "${DATA_DIR}/.tuya-data" -maxdepth 1 -name 'user_*.json' 2>/dev/null | wc -l)

    if [ "${USER_COUNT}" -eq 0 ]; then
        if [ "${NO_ACCOUNTS_NOTIFIED}" -eq 0 ]; then
            bashio::log.warning "No Tuya accounts configured yet; notifying Home Assistant"
            notify_ha create "${NO_ACCOUNTS_NOTIF_ID}" "Tuya IPC Bridge: No accounts configured!" \
                "No Tuya account is logged in yet, so no cameras are available. [Open Tuya IPC Bridge](${WEB_UI_LINK}) to add one via QR code or password login."
            NO_ACCOUNTS_NOTIFIED=1
        fi
    elif [ "${NO_ACCOUNTS_NOTIFIED}" -eq 1 ]; then
        notify_ha dismiss "${NO_ACCOUNTS_NOTIF_ID}"
        NO_ACCOUNTS_NOTIFIED=0
    fi

    if [ ! -e "${LOGIN_PROCESSING}" ] && [ -e "${LOGIN_MARKER}" ]; then
        mv "${LOGIN_MARKER}" "${LOGIN_PROCESSING}" || \
            bashio::log.warning "Could not queue login processing; retrying on the next loop"
    fi
    if [ -e "${LOGIN_PROCESSING}" ]; then
        USER_COUNT=$(find "${DATA_DIR}/.tuya-data" -maxdepth 1 -name 'user_*.json' 2>/dev/null | wc -l)
        if [ "${USER_COUNT}" -gt 0 ]; then
            bashio::log.info "New login detected; restarting the RTSP server"
            stop_rtsp
            start_rtsp
            check_sessions
            NEXT_SESSION_CHECK=$(( $(date +%s) + SESSION_CHECK_INTERVAL ))
            rm -f "${LOGIN_PROCESSING}" || \
                bashio::log.warning "Could not clear processed login marker; retrying on the next loop"
        fi
    fi

    if [ "${USER_COUNT}" -gt 0 ]; then
        if [ -z "${RTSP_PID}" ] || ! kill -0 "${RTSP_PID}" 2>/dev/null; then
            start_rtsp
        fi

        if [ "$(date +%s)" -ge "${NEXT_SESSION_CHECK}" ]; then
            check_sessions
            NEXT_SESSION_CHECK=$(( $(date +%s) + SESSION_CHECK_INTERVAL ))
        fi
    fi

    sleep 15
done
