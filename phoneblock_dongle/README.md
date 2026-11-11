# PhoneBlock for Home Assistant

![PhoneBlock and AnswerBot](https://raw.githubusercontent.com/YaannnTech/HA-Apps/main/.github/images/phoneblock-answerbot.png)

[PhoneBlock](https://github.com/haumacher/phoneblock) by haumacher is a community-maintained database of spam phone numbers at [phoneblock.net](https://phoneblock.net/).

This app runs the Linux build of the [PhoneBlock Dongle](https://phoneblock.net/phoneblock/dongle) inside Home Assistant, so no ESP32 dongle is needed. It registers as a SIP phone on a Fritz!Box or other SIP router and takes over calls from known spam numbers.

## Highlights

- Blocks calls from numbers PhoneBlock knows as spam.
- Plays an announcement in your language (or your own) or runs an interactive dialog.
- Optional call recording.
- Setup wizard in the web UI: Sets itself up on a Fritz!Box with just the admin password and connects your PhoneBlock account by code.

## Requirements

- A PhoneBlock account (register on [phoneblock.net](https://phoneblock.net/)).
- A Fritz!Box or other router with a SIP registrar on the same network.
- Home Assistant on `amd64` or `aarch64`.

## Installation

1. If not already done in HA, add this repository (`https://github.com/YaannnTech/HA-Apps`) to **Settings → Apps → Install Apps → ⋮ → Repositories → Add**, or simply press this button: <br>
[![Add Repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FYaannnTech%2FHA-Apps)
2. Install the **PhoneBlock** app.
3. Start the app and open its web UI.
4. Follow the setup wizard in the web UI.

See the **Documentation** tab for configuration, options and troubleshooting.
