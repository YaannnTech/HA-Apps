# Yaannn's Home Assistant Apps

Self-hosted services packaged as Home Assistant apps (formerly called add-ons).

[![Add repository to my Home Assistant][add-repo-badge]][add-repo]

[![CI](https://github.com/YaannnTech/HA-Apps/actions/workflows/ci.yml/badge.svg)](https://github.com/YaannnTech/HA-Apps/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/github/license/YaannnTech/HA-Apps)][license]
![Architectures: amd64, aarch64](https://img.shields.io/badge/arch-amd64%20%7C%20aarch64-blue)

## Apps

| | App | Version | Description |
|:-:|---|---|---|
| <img src="phoneblock_dongle/icon.png" width="48" alt=""> | [PhoneBlock][readme-phoneblock] | ![Version][v-phoneblock] | Runs the [PhoneBlock][phoneblock-dongle] SIP spam-call blocker in HA, no ESP32 dongle needed. |
| <img src="chhoto_url/icon.png" width="48" alt=""> | [Chhoto URL][readme-chhoto] | ![Version][v-chhoto] | Runs [Chhoto URL][chhoto-upstream], a simple self-hosted URL shortener. |
| <img src="kokoro_fastapi/icon.png" width="48" alt=""> | [Kokoro-FastAPI][readme-kokoro] | ![Version][v-kokoro] | Runs the [Kokoro-FastAPI][kokoro-upstream] text-to-speech server locally on the Home Assistant host. |
| <img src="tuya_ipc_bridge/icon.png" width="48" alt=""> | [Tuya IPC Bridge][readme-tuya] | ![Version][v-tuya] | Bridges Tuya IP camera streams to RTSP for cameras the native Tuya integration does not support. |

## Installation

1. Press the **Add repository** button above, or add `https://github.com/YaannnTech/HA-Apps` under **Settings > Apps > Install Apps > (three-dot menu) > Repositories**.
2. Refresh the **Install Apps** page.
3. Install the app you want. Each app's page explains its setup and options.

## Support

Found a bug or have a feature request? Please open an [issue](https://github.com/YaannnTech/HA-Apps/issues) and say which app and version you are using.

## Credits

These apps package the work of the following projects:

- [PhoneBlock][phoneblock-upstream] by haumacher
- [Chhoto URL][chhoto-upstream] by SinTan1729
- [Kokoro-FastAPI][kokoro-upstream] by remsky
- [tuya-ipc-terminal][tuya-upstream] by seydx, via the [YaannnTech fork][tuya-fork]

## License

[MIT][license]

[license]: https://github.com/YaannnTech/HA-Apps/blob/main/LICENSE
[add-repo-badge]: https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg
[add-repo]: https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FYaannnTech%2FHA-Apps
[phoneblock-dongle]: https://phoneblock.net/phoneblock/dongle
[phoneblock-upstream]: https://github.com/haumacher/phoneblock
[chhoto-upstream]: https://github.com/SinTan1729/chhoto-url
[kokoro-upstream]: https://github.com/remsky/Kokoro-FastAPI
[tuya-upstream]: https://github.com/seydx/tuya-ipc-terminal
[tuya-fork]: https://github.com/YaannnTech/tuya-ipc-terminal
[readme-phoneblock]: phoneblock_dongle/README.md
[readme-chhoto]: chhoto_url/README.md
[readme-kokoro]: kokoro_fastapi/README.md
[readme-tuya]: tuya_ipc_bridge/README.md
[v-phoneblock]: https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2FYaannnTech%2FHA-Apps%2Fmain%2Fphoneblock_dongle%2Fconfig.yaml&query=%24.version&label=
[v-chhoto]: https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2FYaannnTech%2FHA-Apps%2Fmain%2Fchhoto_url%2Fconfig.yaml&query=%24.version&label=
[v-kokoro]: https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2FYaannnTech%2FHA-Apps%2Fmain%2Fkokoro_fastapi%2Fconfig.yaml&query=%24.version&label=
[v-tuya]: https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2FYaannnTech%2FHA-Apps%2Fmain%2Ftuya_ipc_bridge%2Fconfig.yaml&query=%24.version&label=
