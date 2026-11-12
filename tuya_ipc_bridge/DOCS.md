# Tuya IPC Bridge — Home Assistant App

Wraps [tuya-ipc-terminal](https://github.com/seydx/tuya-ipc-terminal) by seydx (a Go CLI that authenticates with Tuya Smart Life cloud accounts, discovers IPC/camera devices, and bridges their streams to standard RTSP) as a Home Assistant app so you can add Tuya cameras to Home Assistant with the built-in **generic RTSP camera** platform or **go2rtc**.

## Installation

1. In Home Assistant, go to **Settings → Apps → Install Apps**.
2. Click the **⋮** menu (top right) → **Repositories** → add this repository's URL (`https://github.com/YaannnTech/HA-Apps`).
3. Find **Tuya IPC Bridge** and click **Install**. The image is built locally from the Go source at install time, from the maintained [tuya-ipc-terminal fork](https://github.com/YaannnTech/tuya-ipc-terminal), which adds RTSP and WebRTC fixes to the original project.

## Adding Tuya accounts

Open this app's **Web UI** (Ingress panel, from its Info page). It has forms for both
QR-code login and email/password login, plus a live list of currently authenticated accounts.

## Adding an account via QR code

In the Web UI, under **Add account via QR code**:

1. Select the account's region and enter its email. The region is the Tuya data center of the account, not where you live: most accounts in the Americas are in **us-west** (West America), and Brazilian accounts use **brazil**. If the QR login never completes after scanning, try another region.
2. Click **Start QR login** — a real, scannable QR code appears in the page (rendered
   by the app itself; the login URL is never sent to a third-party QR service).
3. Scan it with the Tuya Smart / Smart Life app, or with the OEM app the account belongs to (such as LittleElf). The page polls automatically and shows
   *success* or *error* once the login completes.

> **Important**: this QR code is not a normal URL — it only works with the Tuya / Smart Life (or variants) app's own built-in QR scanner, **not** your phone's regular Camera app (which won't recognize it at all). In the app, use the scan icon on the **Me**/**Profile** tab (the same one used for "log in via QR code" on Tuya's web portal), then point it at the screen. The code also expires after about a minute, so scan it promptly after it appears.

## Adding an account via email/password

Password login works for Tuya Smart and Smart Life accounts. It does not work for OEM accounts (such as LittleElf and many others): they fail with "wrong account or password" even with the correct password. Use the QR login above for those and scan the code with the account's own app.

## Notifications

Tuya sessions (both QR and password logins) expire after a few days, and the app can't do anything useful with zero accounts logged in. In both cases it creates a Home Assistant persistent notification (Settings → Notifications) with a link back to this app's Web UI:

- **No accounts configured**: Shown when the app finds no logged-in account, dismissed once the first one is added.
- **Re-authentication needed**: Stored sessions are checked about every hour. The first check runs about 5 minutes after the RTSP server first starts (at app start, or after the first login), even if it keeps exiting (for example with no cameras); a login triggers an earlier check.
  A failed check is repeated once after 30 seconds; if it still fails, the notification prompts you to log in again and the app log shows a short reason.
  After a successful login in the Web UI, the app restarts the RTSP server with a fresh camera list and re-checks the sessions, so the notification is dismissed without restarting the app. If the Web UI cannot pass the login on to the app, it asks you to restart the app.

## Adding cameras to Home Assistant

After the app has started, check the log for discovered camera names, then add each one as a generic camera, replacing `HOMEASSISTANT_HOST` with your Home Assistant host's IP/hostname:

```yaml
camera:
  - platform: generic
    stream_source: rtsp://HOMEASSISTANT_HOST:8553/LivingRoomCamera
    name: "Living Room Camera"
```

Or, if you use the [go2rtc](https://github.com/AlexxIT/go2rtc) app:

```yaml
streams:
  living_room:
    - rtsp://HOMEASSISTANT_HOST:8553/LivingRoomCamera
```

## Troubleshooting

- Check the app log — authentication and camera discovery output is printed on every start.
- For streams that drop, check the app log for `stream_diag` connection diagnostics.
- If login keeps failing, verify the account/region/password. A QR code from the wrong region scans without an error but the login never completes.
- "Authentication failed" or "wrong account or password" on password login for an OEM account (such as LittleElf and many others): Password login does not work for these accounts; use QR login and scan the code with the account's own app.
- If cameras don't appear, confirm they're online in the Tuya Smart / Smart Life / other Tuya variant app first.

## Limitations

This app only wraps and automates the upstream CLI; it does not add functionality beyond what `tuya-ipc-terminal` itself supports (see its
[README](https://github.com/seydx/tuya-ipc-terminal) for supported camera types, codecs, and known limitations).
