# 7.8.2.1

- Initial public release, wrapping the official `sintan1729/chhoto-url:7.8.2-alpine` image as a Home Assistant app for `amd64`, `aarch64`, and `armv7`. The app version follows the upstream image version (mostly, with another digit appended for Home Assistant app versioning).
- Web interface and API on port `4567`, available both as a sidebar panel (Ingress) and through the "Open Web UI" link on the app's Info tab.
- Settings for optional admin password, public site URL, API key, public link creation, WAL database mode, and redirect method.
- **Public Site URL** defaults to Home Assistant's host (from its internal URL, else the host IP) plus the app's published port.
- Short link database stored in the app's persistent data storage.
- Frontend fixes for use inside Home Assistant: the sidebar panel no longer fails with "Something went wrong!", and copying short links to the clipboard also works over plain HTTP.
