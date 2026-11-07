# PhoneBlock for Home Assistant

This app runs the native Linux PhoneBlock SIP spam-call blocker inside Home Assistant. It is intended to run on the same network as a Fritz!Box or other compatible router.

It installs the released Linux version of the [PhoneBlock Dongle firmware](https://github.com/haumacher/phoneblock/tree/master/phoneblock-dongle) from the upstream [PhoneBlock APT repository](https://haumacher.github.io/phoneblock/apt/), the same package a Raspberry Pi uses. The app version follows the firmware version, plus the app build: For example, 1.7.0-beta9-1 is firmware 1.7.0-beta9, first app build. PhoneBlock releases the 1.7.0 betas as version 2.0.0; until 2.0.0 is out, the app follows the beta channel.

## Setup

1. If not already done in HA, add this repository (`https://github.com/YaannnTech/HA-Apps`) to **Settings → Apps → Install Apps → ⋮ → Repositories → Add**, or simply press this button: <br>
[![Add Repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FYaannnTech%2FHA-Apps)
2. Install the **PhoneBlock** app.
3. Start the app and open the **PhoneBlock** Web UI.
4. Link your PhoneBlock account there: The web UI shows a code, which you enter on phoneblock.net. Alternatively, paste a PhoneBlock API token (starts with `pbt_`) into **PhoneBlock token** on the app's **Configuration** tab, save, and restart the app.
5. Configure the SIP profile in the web UI, then choose and preview a localized announcement or upload your own raw 8 kHz mono G.711 A-law file.

For NAT or routed setups, optionally set **Advertised host** and **Advertised SIP port** in the same tab; leave them empty to detect the address automatically.

The log omits full SIP messages, keepalives and routine registration handshakes. Enable **Verbose log** in the Configuration tab and restart the app when you need them for troubleshooting.

A token in **PhoneBlock token** is applied on every start, replacing a linked one, and checked with PhoneBlock. If PhoneBlock rejects it, the app does not start and Home Assistant shows a **PhoneBlock: token rejected** notification; the same notification appears if a token expires later (detected by the daily check). Update **PhoneBlock token** or clear it, then restart the app; the notification is dismissed once a token is accepted. If PhoneBlock can't be reached at start, the app starts anyway. With the field empty, a linked token is kept across restarts and updates.

Call recording is opt-in in the web UI's dialog settings. Recordings and the call list are stored in the app's data, so they are part of the app's backups; recordings use up to 200 MB.

On first start the app takes Home Assistant's timezone; you can change it later in the web UI's settings. The web UI's log panel shows the service's warnings and errors.

The app supports Home Assistant `amd64` and `aarch64` installations. It uses
host networking so SIP and RTP can use their configured UDP ports.
The shared PhoneBlock web UI is available through the app's **Open Web UI** link. Firmware upload, Wi-Fi factory reset, and email reporting are ESP-only and are hidden in the Linux UI.

## Current scope

- UDP SIP registration with MD5 Digest authentication
- Single active SIP dialog
- PhoneBlock caller classification
- PCMA/8000 RTP announcement playback or interactive dialog, with optional call recording
- Shared firmware status/configuration web UI
- Health endpoint for Home Assistant ingress

The shared Linux UI includes Fritz!Box TR-064 provisioning, 2FA, and phonebook actions. These use the same TR-064 implementation as the ESP build, but have not yet been verified against a Fritz!Box from the HA container. SIP registration is UDP-only on Linux.

ESP-only functions are not available in the Linux app: Wi-Fi provisioning, firmware upload/update, factory reset, mail reporting, live log streaming, crash tests, and chip/heap/task diagnostics. Firmware update checks currently report that no update is available.
