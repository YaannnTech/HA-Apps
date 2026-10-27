ARG PHONEBLOCK_REF=master
ARG PHONEBLOCK_CACHE_BUST=master-4f579571

# Keep the builder's Alpine release in sync with the runtime base image below,
# so the binary links against the same library versions it runs with.
FROM alpine:3.24 AS builder
ARG PHONEBLOCK_REF
ARG PHONEBLOCK_CACHE_BUST
RUN echo "Building PhoneBlock source cache ${PHONEBLOCK_CACHE_BUST}" \
    && apk add --no-cache build-base cjson-dev curl-dev git libmicrohttpd-dev \
         libsrtp-dev openssl-dev pkgconf python3
WORKDIR /src
# Treeless clone (full commit history and tags, file contents only for the
# checkout): the Makefile derives the firmware version from the dongle-v*
# release tags with git describe, like the ESP32 build,
# e.g. 1.7.0-beta3-81-g1a2b3c4.
RUN echo "Cloning PhoneBlock source cache ${PHONEBLOCK_CACHE_BUST}" \
    && git clone --filter=tree:0 --branch "${PHONEBLOCK_REF}" \
    https://github.com/haumacher/phoneblock.git .
WORKDIR /src/phoneblock-dongle/firmware/test
RUN make phoneblock_linux PHONEBLOCK_DATA_DIR=/data

FROM ghcr.io/home-assistant/base:3.24-2026.10.0
ARG BUILD_VERSION
ARG BUILD_ARCH

LABEL \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="app" \
    io.hass.arch="${BUILD_ARCH}" \
    org.opencontainers.image.title="PhoneBlock Dongle" \
    org.opencontainers.image.source="https://github.com/haumacher/phoneblock"

RUN apk add --no-cache ca-certificates cjson curl jq libcurl libmicrohttpd \
    libsrtp nginx openssl
COPY --from=builder /src/phoneblock-dongle/firmware/build/linux-host/phoneblock-dongle /usr/bin/phoneblock-dongle
COPY --from=builder /src/phoneblock-dongle/firmware/build/linux-host/web/ /usr/share/phoneblock-dongle/web/
COPY --from=builder /src/phoneblock-dongle/firmware/i18n/audio /usr/share/phoneblock/announcements
COPY run.sh /run.sh
COPY nginx.conf /etc/nginx/phoneblock.conf.template
RUN chmod a+x /run.sh /usr/bin/phoneblock-dongle

CMD ["/run.sh"]
