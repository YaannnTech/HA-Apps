# 7.9.3.1

- Update Chhoto URL to upstream release 7.9.3, which no longer logs the OIDC warning when OIDC is not configured ([#153](https://github.com/SinTan1729/chhoto-url/issues/153)) and improves the database cleanup and backup flow.
- Remove this app's workaround that hid the OIDC warning.

# 7.9.2.1

- Update Chhoto URL to upstream release 7.9.2 (includes 7.9.0 and 7.9.1): asynchronous logging, faster password hashing, a password box placeholder, and OIDC login support in the backend and frontend. OIDC is not configurable in this app yet.
- Hide upstream's "OIDC Issuer URL must be non empty." warning, which it logs on every start when OIDC is not configured.

# 7.8.4.2

- Fix **Enable WAL database mode** being ignored when turned off; WAL mode stayed enabled regardless of the setting.

# 7.8.4.1

- Update Chhoto URL to upstream release 7.8.4, which formats hit counts with thousands separators.

# 7.8.3.1

- Update Chhoto URL to upstream release 7.8.3, which fixes malformed public site URLs and missing URL protocols.
- Keep the Home Assistant frontend fixes for clipboard handling and stale browser caches; the Ingress site-URL patch is no longer needed because upstream now uses the current origin.

# 7.8.2.1

- Initial public release, wrapping the official `sintan1729/chhoto-url:7.8.2-alpine` image as a Home Assistant app for `amd64`, `aarch64`, and `armv7`. The app version follows the upstream image version (mostly, with another digit appended for Home Assistant app versioning).
- Web interface and API on port `4567`, available both as a sidebar panel (Ingress) and through the "Open Web UI" link on the app's Info tab.
- Settings for optional admin password, public site URL, API key, public link creation, WAL database mode, and redirect method.
- **Public Site URL** defaults to Home Assistant's host (from its internal URL, else the host IP) plus the app's published port.
- Short link database stored in the app's persistent data storage.
- Frontend fixes for use inside Home Assistant: the sidebar panel no longer fails with "Something went wrong!", and copying short links to the clipboard also works over plain HTTP.
