# 0.9.2

- Fix native RTSP playback with clients that change camera-path casing, including VLC.
- Generate SDP for the requested HD or SD stream, advertise the matching codec, and align
  HEVC RTP payloads with the advertised payload type.
- Send UDP media to the RTSP client's address and keep RTSP requests responsive while the
  Tuya/WebRTC stream starts.

# 0.9.1

- Use the Supervisor-assigned ingress port for the QR login Web UI to avoid conflicts with other host-network apps.

# 0.9.0

- **Breaking**: renamed the add-on from "Tuya IPC Terminal" to "Tuya IPC Bridge" (slug
  `tuya_ipc_terminal` \u2192 `tuya_ipc_bridge`, folder renamed to match). Since the slug changed,
  the Supervisor treats this as a new add-on \u2014 uninstall the old one and reinstall, then log
  your accounts back in via the Web UI.

# 0.4.6

- Add a `README.md` inside the add-on folder with a short intro, shown on the add-on's Info
  tab (distinct from the full `DOCS.md`, shown under Documentation).

# 0.4.5

- Confirmed working notification link format is "/<slug>" directly, not
  "/hassio/ingress/<slug>". Restored the clickable link using the real Supervisor-assigned
  slug fetched from the Supervisor API.

# 0.4.4

- The `/hassio/ingress/<slug>` deep link in notifications proved unreliable (clicking it
  just redirected to the default dashboard instead of opening the add-on). Replaced with
  plain-text navigation instructions (Settings → Add-ons → Tuya IPC Terminal → Open Web UI).

# 0.4.3

- Fix the "Open Tuya IPC Terminal" notification link: it hardcoded the `config.yaml` slug
  (`tuya_ipc_terminal`), but the Supervisor actually prefixes it with a repository hash for
  add-ons installed from a custom repository, so that path didn't resolve. Now fetches the
  real assigned slug from the Supervisor API (`/addons/self/info`) at startup.

# 0.4.2

- Add an original `icon.png`/`logo.png` (CCTV camera silhouette with streaming arcs, teal
  gradient background) shown in the Add-on Store and Info page. No Tuya branding/trademarks
  used.

# 0.4.1

- Add a note to the `rtsp_port` description on the Configuration tab pointing to the Web UI
  for account management, since it's now the only visible field there.

# 0.4.0

- **Breaking**: removed the config-based `accounts` option. All account management (QR and
  password login) now happens exclusively through the Web UI, which already supported both.
  If you were using config-based accounts, log them back in via the Web UI after upgrading.
- Added a "no accounts configured" Home Assistant persistent notification, shown as soon as
  the add-on starts with zero logged-in accounts and dismissed once the first one is added
  (same mechanism as the existing re-authentication notification).

# 0.3.2

- The Configuration tab doesn't render `description` text for list/array-type options (only
  `name`), so the QR/password Web UI hint for `accounts` wasn't visible. Moved it into the
  `name` itself, which does render.

# 0.3.1

- Add a direct link to the add-on's Web UI (Ingress panel) in the `accounts` config option's
  description, so the QR/password login alternative is discoverable right on the
  Configuration tab.

# 0.3.0

- Web UI now also supports email/password login (in addition to QR), so all interactive
  account management lives in one place. The `accounts` config option remains for optional
  headless/scripted provisioning — clarified this split in the Configuration tab labels and
  DOCS.md.

# 0.2.4

- Add `translations/en.yaml` with friendly names/descriptions for the Configuration tab
  fields (previously showed raw option keys like `rtsp_port`).

# 0.2.3

- Fix the real cause of repeated "Error forwarding ... packet" log lines (previous release
  only downgraded their log level): the RTSP read loop only detects a dead client via its
  60s read deadline, so failed writes kept repeating for up to a minute per disconnect.
  Now closes the TCP connection immediately on the first failed write, which unblocks the
  read loop right away and triggers normal client cleanup.

# 0.2.2

- Patch upstream to stop flooding the log with "Error forwarding video/audio packet to
  ... client" once an RTSP client disconnects: it kept logging at ERROR level for every
  packet indefinitely (the dead client is never marked inactive since `lastActivity` is
  bumped regardless of write success). Downgraded to Trace level, which isn't printed by
  default. Purely cosmetic — doesn't affect other connected clients.

# 0.2.1

- Fix `notify_ha`/`check_sessions` crashing the add-on with "unbound variable" under `set -u`
  when called with only 2 args (the `dismiss` case doesn't pass title/message).

# 0.2.0

- Add a session-expiry watchdog: every stored account is re-validated hourly, and an expired
  session now creates a Home Assistant persistent notification (with a link back to the
  add-on's Web UI) instead of only logging a warning. The notification auto-dismisses once
  the session is valid again. Requires `homeassistant_api: true` (Supervisor Core API proxy).

# 0.1.7

- Fix the misleading "No accounts configured" warning on startup: it only checked the
  add-on's `accounts` config option, not accounts added via the QR web UI (which are stored
  as session files, not config). Now also checks for existing session files before warning.

# 0.1.6

- Give the QR code a solid white background with quiet-zone padding (the SVG itself is
  transparent, so it was showing the dark page background through it).

# 0.1.5

- Fix QR codes not being recognized by the Tuya Smart / Smart Life app: replaced the
  vendored client-side JS renderer (davidshimjs/qrcodejs) with server-side generation via
  the well-maintained Python `qrcode` library, served as an SVG image.

# 0.1.4

- Fix "Start QR login" returning 404: generated links/forms used absolute paths
  (`/qr/start`, `/qrcode.min.js`, ...) which bypass the Ingress proxy's per-session token
  prefix. All URLs are now prefixed with the `X-Ingress-Path` header HA sends on every
  proxied request.

# 0.1.3

- Fix the RTSP-start retry loop never detecting logged-in accounts: `auth list`'s
  "No authenticated users found." message also contains the substring "authenticated user",
  so the old `grep` check always matched. Now checks for session files on disk instead.

# 0.1.2

- Fix startup crashing when no accounts are configured yet (`jq length` on an empty/null
  options value, and the RTSP server exiting fatally with zero authenticated users). The
  add-on now stays up and starts the RTSP server automatically once an account is added via
  config or the QR web UI.

# 0.1.1

- Add Ingress web UI for QR-code login: renders a real, scannable QR code in the browser
  and polls until login completes. Upstream source is patched at build time to expose the
  raw QR login token (previously only rendered as terminal ASCII art).

# 0.1.0

- Initial release: builds `tuya-ipc-terminal` from upstream source, automates email/password
  login, refreshes camera discovery, and runs the bridged RTSP server.
