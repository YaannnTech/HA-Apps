#!/usr/bin/with-contenv bashio
set -e

DATA_DIR="/data"
mkdir -p "${DATA_DIR}"
cd "${DATA_DIR}"

RTSP_PORT=$(bashio::config 'rtsp_port')

# The Supervisor prefixes the config.yaml slug with a repository hash for add-ons installed
# from a custom repository (e.g. "45df7312_tuya_ipc_bridge"), so the panel path can't just
# be hardcoded from config.yaml - fetch the real slug Supervisor assigned instead. Confirmed
# working panel path is "/<slug>" directly (not "/hassio/ingress/<slug>").
if ! ADDON_INFO=$(curl -fsS \
    -H "Authorization: Bearer ${SUPERVISOR_TOKEN}" \
    http://supervisor/addons/self/info); then
    bashio::log.error "Could not retrieve add-on information from the Supervisor"
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

# Periodically re-validates every stored session; QR/password logins expire after a few
# days, and this surfaces that as a Home Assistant notification instead of silent log spam.
check_sessions() {
    for f in "${DATA_DIR}/.tuya-data"/user_*.json; do
        [ -e "${f}" ] || continue
        REGION=$(jq -r '.region' "${f}")
        EMAIL=$(jq -r '.email' "${f}")
        NOTIF_ID="tuya_ipc_bridge_reauth_$(echo "${REGION}_${EMAIL}" | tr -c 'a-zA-Z0-9' '_')"

        if tuya-ipc-terminal auth test "${REGION}" "${EMAIL}" 2>/dev/null | grep -q "Session is valid"; then
            notify_ha dismiss "${NOTIF_ID}"
        else
            bashio::log.warning "Session expired for ${EMAIL} (${REGION}); notifying Home Assistant"
            notify_ha create "${NOTIF_ID}" "Tuya IPC Bridge: re-authentication needed" \
                "The Tuya session for **${EMAIL}** (${REGION}) has expired, so its cameras stopped streaming. [Open Tuya IPC Bridge](${WEB_UI_LINK}) and log in again."
        fi
    done
}

# The RTSP server refuses to start with zero authenticated users, so it can't
# just be exec'd here: accounts are only ever added later via the Web UI.
# Keep the add-on alive and (re)start the RTSP server once/whenever users exist.
RTSP_PID=""
SESSION_CHECK_INTERVAL=3600
LAST_SESSION_CHECK=0
NO_ACCOUNTS_NOTIFIED=0
NO_ACCOUNTS_NOTIF_ID="tuya_ipc_bridge_no_accounts"
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

    if [ "${USER_COUNT}" -gt 0 ]; then
        if [ -z "${RTSP_PID}" ] || ! kill -0 "${RTSP_PID}" 2>/dev/null; then
            bashio::log.info "Starting RTSP server on port ${RTSP_PORT}..."
            tuya-ipc-terminal cameras refresh || true
            tuya-ipc-terminal rtsp start --port "${RTSP_PORT}" &
            RTSP_PID=$!
        fi
    fi

    NOW=$(date +%s)
    if [ "${USER_COUNT}" -gt 0 ] && [ $((NOW - LAST_SESSION_CHECK)) -ge "${SESSION_CHECK_INTERVAL}" ]; then
        LAST_SESSION_CHECK=${NOW}
        check_sessions
    fi

    sleep 15
done
