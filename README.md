# Yaannn's Home Assistant Apps

This repository contains the following Home Assistant apps:

* [Kokoro-FastAPI](https://github.com/YaannnTech/HA-Apps/tree/main/kokoro_fastapi)
  * This Home Assistant app runs the [Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI) text-to-speech server locally on the Home Assistant host.
* [Tuya IPC Bridge](https://github.com/YaannnTech/HA-Apps/tree/main/tuya_ipc_bridge)
  * This Home Assistant app acts as a bridge for some Tuya-variant IP cameras, allowing integration with Home Assistant in cases where the native Tuya integration does not support them.
* [PhoneBlock SPAM-Call Blocker](https://github.com/YaannnTech/HA-Apps/tree/main/phoneblock_dongle)
  * This app runs the [PhoneBlock](https://phoneblock.net/phoneblock/dongle) SIP spam-call blocker inside Home Assistant.
* [Chhoto URL Shortener](https://github.com/YaannnTech/HA-Apps/tree/main/chhoto_url)
  * This app runs [Chhoto URL](https://github.com/SinTan1729/chhoto-url), a simple selfhosted URL shortener, inside Home Assistant.

## Usage

1. Add this repository (`https://github.com/YaannnTech/HA-Apps`) to **Settings → Apps → Install Apps → ⋮ → Repositories → Add**.
2. Or simply press this button: <br>
[![Add Repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FYaannnTech%2FHA-Apps)
2. Refresh the **Install Apps** page.
3. Install the desired app.
