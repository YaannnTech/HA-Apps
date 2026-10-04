# PhoneBlock for Home Assistant

This app runs the native Linux PhoneBlock SIP spam-call blocker inside Home Assistant. It is intended to run on the same network as a Fritz!Box or other compatible router.

It is based on the original [PhoneBlock Dongle project](https://github.com/haumacher/phoneblock/tree/master/phoneblock-dongle), with the Linux implementation currently maintained in this [PhoneBlock fork](https://github.com/YaannnTech/phoneblock/tree/linux-core-extraction/phoneblock-dongle).

## Setup

1. If not already done in HA, add this repository (`https://github.com/YaannnTech/HA-Apps`) to **Settings → Apps → Install Apps → ⋮ → Repositories → Add**.
2. Or simply press this button: <br>
[![Add Repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FYaannnTech%2FHA-Apps)
3. Install the **PhoneBlock** app.
4. Configure the Fritz!Box SIP extension and PhoneBlock token in the app options.
5. Start the app and open the **PhoneBlock** Web UI to configure it.
6. In the Web UI, either choose and preview one of the pre-recorded localized announcements, or upload and preview your own raw 8 kHz mono G.711 A-law file.

The app supports Home Assistant `amd64` and `aarch64` installations. It uses
host networking so SIP and RTP can use their configured UDP ports.
The status page is available through the app's **Open Web UI** link.

## Current scope

- UDP SIP registration with MD5 Digest authentication
- Single active SIP dialog
- PhoneBlock caller classification
- PCMA/8000 RTP announcement playback
- Health and status endpoint

The HA-App currently supports UDP SIP only. Full TR-064 provisioning and the complete ESP32 dashboard are not yet exposed in this Home Assistant wrapper.
