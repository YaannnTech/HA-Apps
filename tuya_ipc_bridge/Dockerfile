# Declared before the first FROM so they are usable in the FROM lines below
ARG BUILD_FROM

# Prebuilt tuya-ipc-terminal from the YaannnTech fork's multi-arch image,
# pinned by digest so the same app version always ships the same binary
ARG TUYA_IPC_TERMINAL_IMAGE=ghcr.io/yaannntech/tuya-ipc-terminal:0.5.0@sha256:b24af3bfce5bab24d5b1b5a1b9222ff292d94d070d3c54db8b4c5a38eef4840b
FROM ${TUYA_IPC_TERMINAL_IMAGE} AS tuya

# Final stage: Home Assistant app base
FROM ${BUILD_FROM}

# jq: parses Supervisor API responses and stored session files in run.sh
# curl: calls the HA persistent_notification service on session expiry
# python3 + py3-qrcode: runs the ingress web UI and renders the QR image server-side
RUN apk add --no-cache jq curl python3 py3-qrcode

COPY --from=tuya /usr/local/bin/tuya-ipc-terminal /usr/bin/tuya-ipc-terminal
COPY run.sh /run.sh
COPY qr_server.py /usr/bin/qr_server.py

RUN chmod a+x /run.sh /usr/bin/tuya-ipc-terminal /usr/bin/qr_server.py

CMD [ "/run.sh" ]
