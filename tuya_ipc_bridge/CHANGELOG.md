# 0.11.1

- Still builds fork release v0.2.0 (commit `655cb01`); only the app scripts changed.
- No more false "re-authentication needed" notification right after the app starts: The first session check now runs about 5 minutes after the first RTSP server start, and repeated failed starts do not delay it.
- A failed session check is repeated once after 30 seconds before Home Assistant is notified. When it still fails, the app log shows a short reason (no session data).
- After a successful QR or password login in the Web UI, the app restarts the RTSP server with a fresh camera list and re-checks the sessions, which dismisses an old re-authentication notification. If the Web UI cannot pass the login on to the app, it asks you to restart the app.

# 0.11.0

- Build from fork release v0.2.0 (commit `655cb01`). It adds:
  - Known Chinese Tuya error messages get an English explanation next to the original text.
  - A failed password login, or a password login without cameras, points to QR login (password login does not work for OEM accounts such as LittleElf).
  - Runtime errors, such as a failed login, no longer print the command usage text after the message.
  - A rejected login token request no longer ends in a crash during password login; the Tuya error is shown instead.
  - `TUYA_DEBUG=1` prints the login result fields (redacted) for comparing QR and password sessions. This app does not expose it yet.
- Login page and documentation: Password login works for Tuya Smart and Smart Life accounts, not for OEM accounts (such as LittleElf and many others). Those fail with "wrong account or password" and must use the QR login, scanned with the account's own app. The password form, the QR section and the failure message now say so.

# 0.10.0

- Build from the first release of the maintained [tuya-ipc-terminal fork](https://github.com/YaannnTech/tuya-ipc-terminal), v0.1.0 (commit `c095fa9`), and update the app base image to 21.0.11. The release adds:
  - More camera types are discovered: additional Tuya camera categories and ksdjml (video peephole) cameras.
  - Pending Tuya API requests are cancelled when the bridge stops, so it shuts down cleanly.
  - Video RTP timestamps are corrected (they were inflated), which helps players and NVRs that are strict about timing.
  - The camera speaker is unmuted for talkback.
  - New options in the CLI: an RTSP listen address and opt-in LAN HD HEVC streaming. This app does not expose them yet and keeps the previous behavior.

# 0.9.5

- The login page now offers the regions of the bundled tuya-ipc-terminal, including **brazil**, with a short description of each (e.g. "us-west - West America"). Before, the page had its own list that was missing brazil.
- Documentation: most accounts in the Americas are in **us-west**, and a QR code from the wrong region scans without an error but never completes the login.

# 0.9.4

- Build from the `main` branch of the maintained [tuya-ipc-terminal fork](https://github.com/YaannnTech/tuya-ipc-terminal), pinned to a commit. It adds:
  - `/sd` streams no longer hang on cameras whose SD stream is H.264.
  - A camera that never finishes the WebRTC handshake now fails after 30 s instead of leaving the stream stuck, and the RTSP server no longer hangs on shutdown while such a camera is still starting.
  - A failed or lost camera connection is cleaned up completely and closes its RTSP sessions, so players and NVRs reconnect instead of waiting for a stream that never comes.
  - Disconnected RTSP clients are dropped right away instead of flooding the log, and a client that stops reading no longer stalls the others.
  - A `brazil` region and a `--country-code` option for password login.
  - Updated dependencies (pion WebRTC, paho MQTT, `golang.org/x`), which fixes the known vulnerabilities in code paths the bridge uses.
- Drop the two source patches for the RTSP forwarder log flood and the dead-client cleanup: the fork now fixes both properly.
- Build with Go 1.26 and update the app base image to 21.0.10.

# 0.9.3

- **Breaking**: drop `armv7` support. The Home Assistant app base image is no longer published for `armv7`; existing `armv7` installations stay on 0.9.2.
- Update the app base image to 21.0.8 (Alpine 3.24) and install the QR code library from Alpine packages instead of pip.
- The build now fails loudly if one of the source patches no longer applies, instead of silently shipping without it.
- Documentation: current Home Assistant "Apps" menu paths and wording, mention the tuya-ipc-terminal fork the app builds from, and correct the description of how the QR code is rendered.

# 0.9.2

- Fix native RTSP playback with clients that change camera-path casing, including VLC.
- Generate SDP for the requested HD or SD stream, advertise the matching codec, and align
  HEVC RTP payloads with the advertised payload type.
- Send UDP media to the RTSP client's address and keep RTSP requests responsive while the
  Tuya/WebRTC stream starts.
- Note: All these fixes were made in a personal fork of the upstream tuya-ipc-terminal project, and this HA app has now been switched over to use that fork instead of the original repository. A PR was made for the original author to integrate the fixes into their upstream repository (at which point this add-on would switch back to the official version).

# 0.9.1

- Use the Supervisor-assigned ingress port for the QR login Web UI to avoid conflicts with other host-network apps.

# 0.9.0

- **Breaking**: renamed the add-on from "Tuya IPC Terminal" to "Tuya IPC Bridge" (slug
  `tuya_ipc_terminal` → `tuya_ipc_bridge`, folder renamed to match). Since the slug changed,
  the Supervisor treats this as a new add-on — uninstall the old one and reinstall, then log
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
