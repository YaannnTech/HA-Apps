# Declared before the first FROM so they are usable in the FROM lines below
ARG BUILD_FROM

# Prebuilt tuya-ipc-terminal from the YaannnTech fork's multi-arch image,
# pinned by digest so the same app version always ships the same binary
ARG TUYA_IPC_TERMINAL_IMAGE=ghcr.io/yaannntech/tuya-ipc-terminal:0.3.1@sha256:6903dc407eac0ef6742520e847e7540770f5d838d9840e4ce5a2eccb835fca5d
FROM ${TUYA_IPC_TERMINAL_IMAGE} AS tuya

# Final stage: Home Assistant app base
FROM ${BUILD_FROM}

# expect: drives the CLI's interactive password prompt (reads from a real TTY)
# jq: parses Supervisor API responses and stored session files in run.sh
# curl: calls the HA persistent_notification service on session expiry
# python3 + py3-qrcode: runs the ingress web UI and renders the QR image server-side
RUN apk add --no-cache expect jq curl python3 py3-qrcode

COPY --from=tuya /usr/local/bin/tuya-ipc-terminal /usr/bin/tuya-ipc-terminal
COPY run.sh /run.sh
COPY add_account.exp /usr/bin/add_account.exp
COPY qr_server.py /usr/bin/qr_server.py

RUN chmod a+x /run.sh /usr/bin/add_account.exp /usr/bin/tuya-ipc-terminal /usr/bin/qr_server.py

CMD [ "/run.sh" ]
