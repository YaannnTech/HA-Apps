#!/usr/bin/with-contenv bashio
set -e

DATA_DIR=/data
CONFIG_FILE=${DATA_DIR}/dongle.conf
mkdir -p "${DATA_DIR}"

{
    printf 'sip_host=%s\n' "$(bashio::config 'sip_host')"
    printf 'sip_port=%s\n' "$(bashio::config 'sip_port')"
    printf 'sip_user=%s\n' "$(bashio::config 'sip_user')"
    printf 'sip_pass=%s\n' "$(bashio::config 'sip_pass')"
    printf 'sip_expires=%s\n' "$(bashio::config 'sip_expires')"
    printf 'sip_local_port=%s\n' "$(bashio::config 'sip_local_port')"
    printf 'rtp_port=%s\n' "$(bashio::config 'rtp_port')"
    printf 'phoneblock_base_url=%s\n' "$(bashio::config 'phoneblock_base_url')"
    printf 'phoneblock_token=%s\n' "$(bashio::config 'phoneblock_token')"
    printf 'announcement_path=%s\n' "$(bashio::config 'announcement_path')"
} > "${CONFIG_FILE}"
chmod 0600 "${CONFIG_FILE}"

bashio::log.info "Starting PhoneBlock Dongle SIP service"
exec /usr/bin/phoneblock-dongle \
    --service \
    --web 8080 \
    --web-bind 0.0.0.0 \
    --config "${CONFIG_FILE}"
