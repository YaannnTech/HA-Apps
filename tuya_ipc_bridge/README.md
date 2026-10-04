# Tuya IPC Bridge for Home Assistant

Bridges Tuya Smart / Smart Life cameras' IPC streams to standard RTSP, so they can be added to Home Assistant like any other RTSP camera — via the built-in **generic camera** platform or **go2rtc**.

Built by wrapping [seydx/tuya-ipc-terminal](https://github.com/seydx/tuya-ipc-terminal), a Go CLI that authenticates with Tuya's cloud, discovers your cameras, and does the actual bridging.

## Why does this exist?

Not all "Tuya" cameras work with the native Home Assistant Tuya integration, nor do all of them support ONVIF/RTSP out of the box. In many cameras, that setting is missing, which is especially true for devices that require another Tuya-variant app to control them (i.e. "LittleElf"). The only choice one has in that case is to use their browser based IPC stream instead, which is what the underlying [seydx/tuya-ipc-terminal](https://github.com/seydx/tuya-ipc-terminal) does.

## Highlights

- **Web UI** (Ingress) for adding accounts — QR-code login or email/password
- Automatic camera discovery and RTSP server startup once an account is logged in.
- Home Assistant notifications when no account is configured yet, or when a session expires and needs re-authentication.

See the **Documentation** tab for full setup, usage, and troubleshooting instructions.

## Installation & Usage

1. If not already done in HA, add this repository (`https://github.com/YaannnTech/HA-Apps`) to **Settings → Apps → Install Apps → ⋮ → Repositories → Add**.
2. Or simply press this button: <br>
[![Add Repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FYaannnTech%2FHA-Apps)
3. Install **Tuya IPC Bridge**.
3. Start the app, **then** configure accounts through the included Web UI.

## Settings

- **RTSP Port**: Port the bridged RTSP server listens on. The default is `8553`.
- Tuya accounts are configured through the app's Ingress Web UI using QR code or password login.

The app supports Home Assistant `amd64`, `aarch64`, and `armv7` installations.