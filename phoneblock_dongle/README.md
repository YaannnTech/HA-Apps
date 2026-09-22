# PhoneBlock Dongle for Home Assistant

This app runs the native Linux PhoneBlock SIP spam-call blocker inside Home
Assistant. It is intended to run on the same LAN or VPN path as the Fritz!Box.

It is based on the original [PhoneBlock Dongle project](https://github.com/haumacher/phoneblock/tree/master/phoneblock-dongle),
with the Linux implementation maintained in the [PhoneBlock fork](https://github.com/YaannnTech/phoneblock/tree/linux-core-extraction/phoneblock-dongle).
## Setup

1. Install **PhoneBlock Dongle** from the `HA-Apps` repository.
2. Configure the Fritz!Box SIP extension and PhoneBlock token in the app options.
3. Place an 8 kHz mono raw G.711 A-law announcement in the app's persistent
   data directory so it is visible inside the container as
   `/data/announcement.alaw`, or change the `announcement_path` option.
4. Start the app and open its status page.

The app supports Home Assistant `amd64` and `aarch64` installations. It uses
host networking so SIP and RTP can use their configured UDP ports.
The status page is available through the app's **Open Web UI** link.

## Current scope

- UDP SIP registration with MD5 Digest authentication
- Single active SIP dialog
- PhoneBlock caller classification
- PCMA/8000 RTP announcement playback
- Health and status endpoint

TCP/TLS SIP, full TR-064 provisioning, and the complete ESP32 dashboard are
not included in this first Home Assistant wrapper.
