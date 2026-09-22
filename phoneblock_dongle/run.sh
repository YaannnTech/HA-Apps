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

sip_host="$(sed -n 's/^sip_host=//p' "${CONFIG_FILE}" 2>/dev/null)"
sip_port="$(sed -n 's/^sip_port=//p' "${CONFIG_FILE}" 2>/dev/null)"
sip_user="$(sed -n 's/^sip_user=//p' "${CONFIG_FILE}" 2>/dev/null)"
sip_pass="$(sed -n 's/^sip_pass=//p' "${CONFIG_FILE}" 2>/dev/null)"
sip_pass_len="${#sip_pass}"

bashio::log.info "Starting PhoneBlock Dongle SIP service"
bashio::log.info "SIP config: host=${sip_host} port=${sip_port} user=${sip_user} pass_len=${sip_pass_len}"

exec /usr/bin/phoneblock-dongle \
    --service \
    --web 8080 \
    --web-bind 0.0.0.0 \
    --config "${CONFIG_FILE}"
