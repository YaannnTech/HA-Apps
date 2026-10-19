#!/usr/bin/with-contenv bashio
set -e

DATA_DIR=/data
CONFIG_FILE=${DATA_DIR}/dongle.conf
mkdir -p "${DATA_DIR}"

if [ -f "${CONFIG_FILE}" ]; then
    bashio::log.info "Using persistent configuration from ${CONFIG_FILE}"
else
    bashio::log.info "No configuration yet; configure the dongle in the web UI"
fi

if ! bashio::config.has_value 'phoneblock_token'; then
    bashio::log.error "Set the PhoneBlock token in the app configuration and restart"
    exit 1
fi
phoneblock_token="$(bashio::config 'phoneblock_token')"
contact_host=""
contact_port=""
bashio::config.has_value 'contact_host' && contact_host="$(bashio::config 'contact_host')"
bashio::config.has_value 'contact_port' && contact_port="$(bashio::config 'contact_port')"
if [ -n "${contact_host}" ] && ! [[ "${contact_host}" =~ ^[A-Za-z0-9._:-]{1,63}$ ]]; then
    bashio::log.error "Advertised host must be a hostname or IP address of at most 63 characters"
    exit 1
fi

config_source="${CONFIG_FILE}"
[ -f "${config_source}" ] || config_source=/dev/null
# Empty values remove the key, so clearing an option restores auto-detection.
( umask 077; PB_TOKEN="${phoneblock_token}" PB_CONTACT_HOST="${contact_host}" \
PB_CONTACT_PORT="${contact_port}" awk '
    BEGIN {
        n = split("pb_token contact_host contact_port", keys, " ")
        vals["pb_token"] = ENVIRON["PB_TOKEN"]
        vals["contact_host"] = ENVIRON["PB_CONTACT_HOST"]
        vals["contact_port"] = ENVIRON["PB_CONTACT_PORT"]
    }
    function emit(  i) {
        if (done) return
        for (i = 1; i <= n; i++) if (vals[keys[i]] != "") print keys[i] "=" vals[keys[i]]
        done = 1
    }
    /^[[:space:]]*\[/ {
        if (in_section) emit()
        in_section = ($0 ~ /^[[:space:]]*\[phoneblock\][[:space:]]*$/)
        seen = seen || in_section
    }
    in_section && /^(pb_token|contact_host|contact_port)=/ { next }
    { print }
    END {
        if (in_section) emit()
        else if (!seen) { print "[phoneblock]"; emit() }
    }
' "${config_source}" > "${CONFIG_FILE}.new" )
mv "${CONFIG_FILE}.new" "${CONFIG_FILE}"
bashio::log.info "Applied PhoneBlock token and advertised address from the app configuration"

# "|| true" is required: under set -e, a missing CONFIG_FILE makes sed exit
# non-zero and that status propagates through the assignment, killing the
# script right here (2>/dev/null only silences sed's stderr, not its exit code).
sip_host="$(sed -n 's/^sip_host=//p' "${CONFIG_FILE}" 2>/dev/null || true)"
sip_port="$(sed -n 's/^sip_port=//p' "${CONFIG_FILE}" 2>/dev/null || true)"
sip_user="$(sed -n 's/^sip_user=//p' "${CONFIG_FILE}" 2>/dev/null || true)"

bashio::log.info "Starting PhoneBlock Dongle SIP service"
bashio::log.info "SIP config: host=${sip_host} port=${sip_port} user=${sip_user}"

if ! addon_info="$(curl -fsS \
    -H "Authorization: Bearer ${SUPERVISOR_TOKEN}" \
    http://supervisor/addons/self/info)"; then
    bashio::log.error "Could not retrieve add-on information from the Supervisor"
    exit 1
fi
if ! ingress_port="$(jq -er '.data.ingress_port' <<< "${addon_info}")"; then
    bashio::log.error "Could not retrieve the assigned Home Assistant ingress port"
    exit 1
fi
if ! [[ "${ingress_port}" =~ ^[1-9][0-9]{0,4}$ ]] || (( ingress_port > 65535 )); then
    bashio::log.error "Supervisor returned an invalid ingress port: ${ingress_port}"
    exit 1
fi
# The Supervisor prefixes the slug with a repository hash for custom repositories.
addon_slug="$(jq -r '.data.slug // "phoneblock_dongle"' <<< "${addon_info}")"
config_link="/config/app/${addon_slug}/config"

# Needs homeassistant_api: true in config.yaml.
notify_ha() {
    local service="$1" notification_id="$2" title="${3:-}" message="${4:-}" payload
    if [ "${service}" = "create" ]; then
        payload="$(jq -n --arg id "${notification_id}" --arg title "${title}" --arg message "${message}" \
            '{notification_id: $id, title: $title, message: $message}')"
    else
        payload="$(jq -n --arg id "${notification_id}" '{notification_id: $id}')"
    fi
    curl -sf -X POST \
        -H "Authorization: Bearer ${SUPERVISOR_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "${payload}" \
        "http://supervisor/core/api/services/persistent_notification/${service}" >/dev/null 2>&1 || true
}

TOKEN_NOTIFICATION_ID="phoneblock_dongle_token_invalid"
notify_token_rejected() {
    notify_ha create "${TOKEN_NOTIFICATION_ID}" "PhoneBlock: token rejected" \
        "PhoneBlock rejected the API token. Open the app's **Configuration** tab ([Open configuration](${config_link})), enter a valid **PhoneBlock token**, save, and restart the app."
}

# Only a definite 401/403 blocks the start; an outage must not keep a good setup offline.
pb_url="$(sed -n 's/^pb_url=//p' "${CONFIG_FILE}" 2>/dev/null || true)"
pb_url="${pb_url:-https://phoneblock.net/phoneblock}"
token_status="$(printf 'Authorization: Bearer %s\n' "${phoneblock_token}" \
    | curl -sS -o /dev/null -w '%{http_code}' --max-time 20 -H @- "${pb_url}/api/test" 2>/dev/null || true)"
case "${token_status}" in
    401|403)
        bashio::log.error "PhoneBlock rejected the token (HTTP ${token_status}); not starting"
        notify_token_rejected
        exit 1
        ;;
    200) notify_ha dismiss "${TOKEN_NOTIFICATION_ID}" ;;
    *) bashio::log.warning "Could not verify the PhoneBlock token (HTTP ${token_status:-none}); starting anyway" ;;
esac

WEB_PORT_FILE=/run/phoneblock-web-port
rm -f "${WEB_PORT_FILE}" "${WEB_PORT_FILE}.tmp"

# The service logs unconditionally; drop full SIP message dumps, keepalives and
# routine registration handshake lines, keeping summaries, warnings and errors.
quiet_log() {
    awk '
        /^[IWE] \([0-9]+\) / {
            dump = ($0 ~ /^I \([0-9]+\) sip: (→|←) .*[0-9]+ bytes\)?:$/)
            if (dump || $0 ~ /^I \([0-9]+\) sip: (→ SIP keepalive ping|challenge: realm=|← [0-9]+ \()/) next
        }
        dump { next }
        { print; fflush() }
    '
}

dongle_args=(--service --web 0 --web-bind 127.0.0.1
    --web-port-file "${WEB_PORT_FILE}" --config "${CONFIG_FILE}")
if bashio::config.true 'verbose_log'; then
    /usr/bin/phoneblock-dongle "${dongle_args[@]}" &
else
    /usr/bin/phoneblock-dongle "${dongle_args[@]}" 2> >(quiet_log >&2) &
fi
dongle_pid=$!

cleanup() {
    kill -TERM "${dongle_pid}" 2>/dev/null || true
    wait "${dongle_pid}" 2>/dev/null || true
    nginx -s quit >/dev/null 2>&1 || true
}
trap cleanup EXIT
trap 'exit 0' INT TERM

attempt=0
while [ ! -s "${WEB_PORT_FILE}" ] && [ "${attempt}" -lt 100 ]; do
    if ! kill -0 "${dongle_pid}" 2>/dev/null; then
        wait "${dongle_pid}" || true
        bashio::log.error "PhoneBlock service exited before binding its web port"
        exit 1
    fi
    sleep 0.1
    attempt=$((attempt + 1))
done
if [ ! -s "${WEB_PORT_FILE}" ]; then
    bashio::log.error "Timed out waiting for PhoneBlock's web port"
    exit 1
fi

web_port="$(cat "${WEB_PORT_FILE}")"
if ! [[ "${web_port}" =~ ^[1-9][0-9]{0,4}$ ]] || (( web_port > 65535 )); then
    bashio::log.error "PhoneBlock published an invalid web port: ${web_port}"
    exit 1
fi

sed -e "s/@INGRESS_PORT@/${ingress_port}/g" \
    -e "s/@WEB_PORT@/${web_port}/g" \
    /etc/nginx/phoneblock.conf.template \
    > /etc/nginx/http.d/default.conf
nginx
bashio::log.info "PhoneBlock web server bound to dynamic loopback port ${web_port}"

# The service re-tests the token daily; surface a rejection without log digging.
token_notified=0
while kill -0 "${dongle_pid}" 2>/dev/null; do
    token_ok="$(curl -sf --max-time 5 "http://127.0.0.1:${web_port}/api/status" \
        | jq -r '.phoneblock.token_ok' 2>/dev/null || true)"
    if [ "${token_ok}" = "false" ] && [ "${token_notified}" -eq 0 ]; then
        bashio::log.error "PhoneBlock rejected the token; notifying Home Assistant"
        notify_token_rejected
        token_notified=1
    elif [ "${token_ok}" = "true" ] && [ "${token_notified}" -eq 1 ]; then
        notify_ha dismiss "${TOKEN_NOTIFICATION_ID}"
        token_notified=0
    fi
    sleep 60 &
    wait $! || true
done

wait "${dongle_pid}"
