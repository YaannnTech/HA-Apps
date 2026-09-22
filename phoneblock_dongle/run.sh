#!/usr/bin/with-contenv bashio
set -e

DATA_DIR=/data
CONFIG_FILE=${DATA_DIR}/dongle.conf
mkdir -p "${DATA_DIR}"

if [ ! -f "${CONFIG_FILE}" ]; then
    bashio::log.info "Creating initial configuration from add-on options"
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
    printf 'fritzbox_host=%s\n' "$(bashio::config 'fritzbox_host')"
    printf 'fritzbox_port=%s\n' "$(bashio::config 'fritzbox_port')"
    printf 'fritzbox_admin_user=%s\n' "$(bashio::config 'fritzbox_admin_user')"
    printf 'fritzbox_admin_pass=%s\n' "$(bashio::config 'fritzbox_admin_pass')"
    printf 'fritzbox_phone_name=%s\n' "$(bashio::config 'fritzbox_phone_name')"
} > "${CONFIG_FILE}"
chmod 0600 "${CONFIG_FILE}"
else
    bashio::log.info "Using persistent configuration from ${CONFIG_FILE}"
fi

sip_host="$(sed -n 's/^sip_host=//p' "${CONFIG_FILE}")"
sip_port="$(sed -n 's/^sip_port=//p' "${CONFIG_FILE}")"
sip_user="$(sed -n 's/^sip_user=//p' "${CONFIG_FILE}")"
sip_pass="$(sed -n 's/^sip_pass=//p' "${CONFIG_FILE}")"
sip_pass_len="${#sip_pass}"

bashio::log.info "Starting PhoneBlock Dongle SIP service"
bashio::log.info "SIP config: host=${sip_host} port=${sip_port} user=${sip_user} pass_len=${sip_pass_len}"

if [ -z "${sip_user}" ] && [ -n "$(bashio::config 'fritzbox_admin_pass')" ]; then
    bashio::log.info "Provisioning SIP credentials through Fritz!Box TR-064"
    /usr/bin/phoneblock-dongle --config "${CONFIG_FILE}" --provision-sip
fi

exec /usr/bin/phoneblock-dongle \
    --service \
    --web 8080 \
    --web-bind 0.0.0.0 \
    --config "${CONFIG_FILE}"
