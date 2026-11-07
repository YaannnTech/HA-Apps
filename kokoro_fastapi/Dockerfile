FROM ghcr.io/remsky/kokoro-fastapi-cpu:v0.9.2

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

# Home Assistant shows the app as started once this passes, and its
# watchdog restarts the app when it turns unhealthy. The long start period
# covers the model download on the first start.
HEALTHCHECK --interval=30s --timeout=10s --start-period=10m --retries=3 \
	CMD curl -fsS -o /dev/null http://127.0.0.1:8880/health || exit 1

CMD ["/run.sh"]
