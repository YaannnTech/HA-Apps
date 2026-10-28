# The released Linux service from the upstream APT repository
# (https://haumacher.github.io/phoneblock/apt/), the same package and version
# as on a Raspberry Pi. The app version follows it (see AGENTS.md).
ARG PHONEBLOCK_VERSION=1.7.0~beta7
ARG PHONEBLOCK_SUITE=trixie
ARG PHONEBLOCK_CHANNEL=beta
# Fingerprint of the repository's signing key, checked before it is trusted.
ARG PHONEBLOCK_REPO_FINGERPRINT=0A1948B95F45BADD626CB753ADFAC8AA5581163F

# Keep the Debian release in sync with PHONEBLOCK_SUITE: the package is
# built per suite against that release's libraries.
FROM ghcr.io/home-assistant/base-debian:trixie-2026.10.3
ARG BUILD_VERSION
ARG BUILD_ARCH
ARG PHONEBLOCK_VERSION
ARG PHONEBLOCK_SUITE
ARG PHONEBLOCK_CHANNEL
ARG PHONEBLOCK_REPO_FINGERPRINT

LABEL \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="app" \
    io.hass.arch="${BUILD_ARCH}" \
    org.opencontainers.image.title="PhoneBlock Dongle" \
    org.opencontainers.image.source="https://github.com/haumacher/phoneblock"

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl gpg jq \
         nginx tzdata \
    && curl -fsSLo /usr/share/keyrings/phoneblock-dongle.gpg \
         https://haumacher.github.io/phoneblock/apt/phoneblock-dongle.gpg \
    && gpg --show-keys --with-colons /usr/share/keyrings/phoneblock-dongle.gpg \
         | grep -q "^fpr:::::::::${PHONEBLOCK_REPO_FINGERPRINT}:$" \
    && echo "deb [signed-by=/usr/share/keyrings/phoneblock-dongle.gpg] https://haumacher.github.io/phoneblock/apt ${PHONEBLOCK_SUITE} ${PHONEBLOCK_CHANNEL}" \
         > /etc/apt/sources.list.d/phoneblock-dongle.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
         "phoneblock-dongle=${PHONEBLOCK_VERSION}" \
    && apt-get purge -y gpg && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    # The package keeps its state in /var/lib/phoneblock; the app's persistent
    # storage is /data, where builds before 1.7.0-beta7-1 kept the same files.
    && rm -rf /var/lib/phoneblock && ln -s /data /var/lib/phoneblock \
    # The stock site listens on port 80, which host networking would take
    # from the host; run.sh writes the Ingress site instead.
    && rm -f /etc/nginx/sites-enabled/default

COPY run.sh /run.sh
COPY nginx.conf /etc/nginx/phoneblock.conf.template
RUN chmod a+x /run.sh

CMD ["/run.sh"]
