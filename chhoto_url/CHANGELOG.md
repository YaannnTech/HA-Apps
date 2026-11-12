# 7.11.4.1

- Update Chhoto URL to upstream release 7.11.4.
- Fix: Logging in to the web interface and the API always failed when no **Password** is set. It works again: With no password set, you are logged in without asking ([#163](https://github.com/SinTan1729/chhoto-url/pull/163)).
- Fix: After resetting a link's hit count when editing it, the count showed 1 instead of 0 ([#164](https://github.com/SinTan1729/chhoto-url/pull/164)).

# 7.11.3.1

- Update Chhoto URL to upstream release 7.11.3 (includes 7.11.0 to 7.11.2): a **Public Site URL** without a scheme but with a port (for example `s.example.com:4567`) is handled now ([#156](https://github.com/SinTan1729/chhoto-url/issues/156)).
- The link handler answers HEAD requests, notes and search support Unicode better, and the frontend no longer has a race condition for the site URL.
- Upstream hardened the backend after security reports: an invalid password or API key hash now stops the server instead of leaving it without a login.
- Upstream also limits the number of spawned threads, allows adding several links in one request only with the API key (at most 2000 links), and sizes the number of parallel password checks to the memory available to the container.
- Upstream's health check was reworked; the app's health check still works and the app reports as healthy.

# 7.10.8.2

- Home Assistant now checks the app's health with upstream's own health check, which includes the database, instead of only testing that the port answers. The app shows as started once it is healthy, and with **Watchdog** on, Home Assistant restarts it when it turns unhealthy.
- Drop the `armv7` architecture, which Home Assistant no longer supports since 2025.12.

# 7.10.8.1

- Update Chhoto URL to upstream release 7.10.8 (includes 7.9.6 to 7.10.7): links can be enabled and disabled, many frontend improvements (mobile view, tooltips, info dialog), custom certificates for OIDC, a faster database layer, and fixes for expiry times and public mode caching.
- Upstream reworked its login cookies, so you have to log in to the admin page once after this update. Logins then survive app restarts and updates again.
- The database is migrated to a new format on the first start, and upstream backs it up first (in `backups` next to the database, now named with a timestamp). Older app versions cannot read the migrated database, so restore an app backup if you need to go back.
- New installs generate the session key in the base64 format upstream now expects; existing keys keep working.
- Upstream checks the **API Key** differently now: a short or simple key logs "Provided API key is insecure" on start, and the log suggests a secure key you can use instead. The key keeps working either way.

# 7.9.5.1

- Update Chhoto URL to upstream release 7.9.5 (includes 7.9.4): more robust cleanup of expired links, and no plaintext-password warning in the log when neither a password nor an API key is set.
- Stay logged in to the admin page across app restarts and updates. The app now generates a session key once and keeps it in its persistent data storage (upstream's new `CHHOTO_SESSION_MASTER_KEY`).

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
