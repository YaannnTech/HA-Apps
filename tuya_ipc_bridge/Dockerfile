# Declared before the first FROM so it's usable in both FROM lines below
ARG BUILD_FROM

# Build stage: compile tuya-ipc-terminal from upstream source
FROM golang:1.23-alpine AS builder

ARG TUYA_IPC_TERMINAL_REF=fix/rtsp-stream-lockup
ARG TUYA_IPC_TERMINAL_REPO=https://github.com/YaannnTech/tuya-ipc-terminal.git
RUN apk add --no-cache git sed

WORKDIR /src
RUN git init \
    && git remote add origin "${TUYA_IPC_TERMINAL_REPO}" \
    && git fetch --depth 1 origin "${TUYA_IPC_TERMINAL_REF}" \
    && git checkout --detach FETCH_HEAD

# Upstream only renders the QR login token as ASCII art; also print it as plain
# text so the ingress web UI can render a real, scannable QR image in-browser.
RUN sed -i 's#\(qrterminal\.Generate("tuyaSmart--qrLogin?token="+qrCodeToken, qrterminal\.L, os\.Stdout)\)#fmt.Println("QR_LOGIN_URL:tuyaSmart--qrLogin?token=" + qrCodeToken)\n\t\1#' cmd/auth/auth.go

# Upstream logs a packet-forwarding error at ERROR level for every single RTP packet
# still queued for a client that already disconnected (and never marks it inactive,
# since lastActivity is bumped regardless of write success) - downgrade to Trace so a
# disconnected RTSP client doesn't flood the log until the next reconnect/cleanup.
RUN sed -i \
    -e 's#core\.Logger\.Error()\.Err(err)\.Msgf("Error forwarding video packet to UDP client %s", sessionID)#core.Logger.Trace().Err(err).Msgf("Error forwarding video packet to UDP client %s", sessionID)#' \
    -e 's#core\.Logger\.Error()\.Err(err)\.Msgf("Error forwarding video packet to TCP client %s", sessionID)#core.Logger.Trace().Err(err).Msgf("Error forwarding video packet to TCP client %s", sessionID)#' \
    -e 's#core\.Logger\.Error()\.Err(err)\.Msgf("Error forwarding audio packet to UDP client %s", sessionID)#core.Logger.Trace().Err(err).Msgf("Error forwarding audio packet to UDP client %s", sessionID)#' \
    -e 's#core\.Logger\.Error()\.Err(err)\.Msgf("Error forwarding audio packet to TCP client %s", sessionID)#core.Logger.Trace().Err(err).Msgf("Error forwarding audio packet to TCP client %s", sessionID)#' \
    pkg/rtsp/forwarder.go

# The RTSP read loop only notices a dead client via a 60s read deadline, so a failed
# write otherwise keeps repeating for up to 60s before cleanup runs; closing the
# connection on the first failed write unblocks that read loop immediately instead.
RUN sed -i '/if _, err := conn.Write(fullPacket); err != nil {/a\            conn.Close()' pkg/rtsp/forwarder.go

RUN go mod download
RUN CGO_ENABLED=0 go build -o /out/tuya-ipc-terminal .

# Final stage: Home Assistant add-on base
FROM ${BUILD_FROM}

# expect: drives the CLI's interactive password prompt (reads from a real TTY)
# jq: parses add-on options (bashio JSON) in run.sh
# curl: calls the HA persistent_notification service on session expiry
# python3 + py3-pip + qrcode: runs the ingress web UI and renders the QR image server-side
RUN apk add --no-cache expect jq curl python3 py3-pip \
    && pip install --no-cache-dir --break-system-packages qrcode

COPY --from=builder /out/tuya-ipc-terminal /usr/bin/tuya-ipc-terminal
COPY run.sh /run.sh
COPY add_account.exp /usr/bin/add_account.exp
COPY qr_server.py /usr/bin/qr_server.py

RUN chmod a+x /run.sh /usr/bin/add_account.exp /usr/bin/tuya-ipc-terminal /usr/bin/qr_server.py

CMD [ "/run.sh" ]
