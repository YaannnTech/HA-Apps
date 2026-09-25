#!/usr/bin/with-contenv bashio
set -e

DATA_DIR=/data
CONFIG_FILE=${DATA_DIR}/dongle.conf
mkdir -p "${DATA_DIR}"

if [ -f "${CONFIG_FILE}" ]; then
    bashio::log.info "Using persistent configuration from ${CONFIG_FILE}"
else
    bashio::log.info "No configuration yet; configure the dongle in the web UI"
    printf 'announcement_path=/data/announcement.alaw\n' > "${CONFIG_FILE}"
fi

if ! grep -q '^announcement_path=' "${CONFIG_FILE}" 2>/dev/null; then
    printf '\nannouncement_path=/data/announcement.alaw\n' >> "${CONFIG_FILE}"
fi
if ! grep -q '^announcement_custom_path=' "${CONFIG_FILE}" 2>/dev/null; then
    printf 'announcement_custom_path=/data/announcement.alaw\n' >> "${CONFIG_FILE}"
fi

# "|| true" is required: under set -e, a missing CONFIG_FILE makes sed exit
# non-zero and that status propagates through the assignment, killing the
# script right here (2>/dev/null only silences sed's stderr, not its exit code).
sip_host="$(sed -n 's/^sip_host=//p' "${CONFIG_FILE}" 2>/dev/null || true)"
sip_port="$(sed -n 's/^sip_port=//p' "${CONFIG_FILE}" 2>/dev/null || true)"
sip_user="$(sed -n 's/^sip_user=//p' "${CONFIG_FILE}" 2>/dev/null || true)"
sip_pass="$(sed -n 's/^sip_pass=//p' "${CONFIG_FILE}" 2>/dev/null || true)"
sip_pass_len="${#sip_pass}"

bashio::log.info "Starting PhoneBlock Dongle SIP service"
bashio::log.info "SIP config: host=${sip_host} port=${sip_port} user=${sip_user} pass_len=${sip_pass_len}"

if ! ingress_port="$(curl -fsS \
    -H "Authorization: Bearer ${SUPERVISOR_TOKEN}" \
    http://supervisor/addons/self/info | jq -er '.data.ingress_port')"; then
    bashio::log.error "Could not retrieve the assigned Home Assistant ingress port"
    exit 1
fi
if ! [[ "${ingress_port}" =~ ^[1-9][0-9]{0,4}$ ]] || (( ingress_port > 65535 )); then
    bashio::log.error "Supervisor returned an invalid ingress port: ${ingress_port}"
    exit 1
fi

sed "s/@INGRESS_PORT@/${ingress_port}/g" \
    /etc/nginx/phoneblock.conf.template \
    > /etc/nginx/http.d/default.conf
nginx

exec /usr/bin/phoneblock-dongle \
    --service \
    --web 8080 \
    --web-bind 127.0.0.1 \
    --config "${CONFIG_FILE}"
