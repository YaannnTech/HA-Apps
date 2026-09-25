# PhoneBlock Dongle for Home Assistant

This app runs the native Linux PhoneBlock SIP spam-call blocker inside Home Assistant. It is intended to run on the same network as a Fritz!Box or other compatible router.

It is based on the original [PhoneBlock Dongle project](https://github.com/haumacher/phoneblock/tree/master/phoneblock-dongle), with the Linux implementation currently maintained in this [PhoneBlock fork](https://github.com/YaannnTech/phoneblock/tree/linux-core-extraction/phoneblock-dongle).

## Setup

1. Install **PhoneBlock Dongle** from the `HA-Apps` repository.
2. Configure the Fritz!Box SIP extension and PhoneBlock token in the app options.
3. Start the app and open its Web UI page to configure it.
4. In the Web UI, either choose and preview one of the pre-recorded localized announcements, or upload and preview your own raw 8 kHz mono G.711 A-law file.

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
