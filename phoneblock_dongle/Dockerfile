ARG PHONEBLOCK_REF=linux-core-extraction
ARG PHONEBLOCK_CACHE_BUST=sip-cseq-fix-20260922

FROM alpine:3.20 AS builder
ARG PHONEBLOCK_REF
ARG PHONEBLOCK_CACHE_BUST
RUN echo "Building PhoneBlock source cache ${PHONEBLOCK_CACHE_BUST}" \
    && apk add --no-cache build-base cjson-dev curl-dev git openssl-dev pkgconf
WORKDIR /src
RUN echo "Cloning PhoneBlock source cache ${PHONEBLOCK_CACHE_BUST}" \
    && git clone --depth 1 --branch "${PHONEBLOCK_REF}" \
    https://github.com/YaannnTech/phoneblock.git .
WORKDIR /src/phoneblock-dongle/firmware/test
RUN make phoneblock_linux

FROM ghcr.io/home-assistant/base:latest
ARG BUILD_VERSION
ARG BUILD_ARCH

LABEL \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="app" \
    io.hass.arch="${BUILD_ARCH}" \
    org.opencontainers.image.title="PhoneBlock Dongle" \
    org.opencontainers.image.source="https://github.com/YaannnTech/phoneblock"

RUN apk add --no-cache ca-certificates cjson libcurl openssl
COPY --from=builder /src/phoneblock-dongle/firmware/test/phoneblock_linux /usr/bin/phoneblock-dongle
COPY run.sh /run.sh
RUN chmod a+x /run.sh /usr/bin/phoneblock-dongle

CMD ["/run.sh"]
