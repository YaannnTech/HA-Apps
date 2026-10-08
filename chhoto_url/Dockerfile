FROM sintan1729/chhoto-url:7.8.3-alpine

ARG BUILD_VERSION
ARG BUILD_ARCH

LABEL \
	io.hass.version="${BUILD_VERSION}" \
	io.hass.type="app" \
	io.hass.arch="${BUILD_ARCH}" \
	org.opencontainers.image.title="Chhoto URL" \
	org.opencontainers.image.source="https://github.com/SinTan1729/chhoto-url"

# jq is used by run.sh to read Home Assistant's /data/options.json and the Supervisor API.
RUN apk add --no-cache jq

# A failed clipboard copy (blocked in the Ingress iframe / over http) wipes CONFIG, crashing the table redraw.
RUN sed -i 's/console\.log(e),clearCachedState(),showAlert(\(.\)Could not copy/console.log(e),showAlert(\1Could not copy/' /app/frontend/base/static/script.js \
	&& ! grep -q 'clearCachedState(),showAlert(.Could not copy' /app/frontend/base/static/script.js \
	&& grep -q 'console.log(e),showAlert(.Could not copy' /app/frontend/base/static/script.js

# navigator.clipboard only exists on HTTPS; fall back to execCommand("copy") on plain HTTP.
RUN sed -i 's#s=Promise.reject(new Error("Unable to get access to clipboard."))#s=new Promise((ok,no)=>{const a=document.createElement("textarea");a.value=n;a.setAttribute("readonly","");a.style.position="fixed";a.style.opacity="0";document.body.appendChild(a);a.select();let c=!1;try{c=document.execCommand("copy")}catch{}a.remove();c?ok():no(new Error("Unable to get access to clipboard."))})#' /app/frontend/base/static/script.js \
	&& grep -q 'c=document.execCommand("copy")' /app/frontend/base/static/script.js

# script.js is served without Cache-Control, so browsers keep stale copies; version the URL.
RUN sed -i "s#src=static/script.js #src=static/script.js?v=${BUILD_VERSION} #" /app/frontend/base/index.html \
	&& grep -q "src=static/script.js?v=${BUILD_VERSION} " /app/frontend/base/index.html

COPY rootfs /

RUN chmod a+x /run.sh

# Replaces the base image's own ENTRYPOINT (/app/chhoto-url) so options can be
# translated into env vars first; run.sh execs the original binary at the end.
ENTRYPOINT ["/run.sh"]
