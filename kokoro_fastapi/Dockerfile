FROM ghcr.io/remsky/kokoro-fastapi-cpu:v0.9.1

ARG BUILD_VERSION
ARG BUILD_ARCH

LABEL \
	io.hass.version="${BUILD_VERSION}" \
	io.hass.type="app" \
	io.hass.arch="${BUILD_ARCH}" \
	org.opencontainers.image.title="Kokoro Server" \
	org.opencontainers.image.source="https://github.com/remsky/Kokoro-FastAPI"

COPY rootfs /

USER root
RUN chmod a+x /run.sh

CMD ["/run.sh"]
