# Kokoro-FastAPI Backend for Home Assistant

This Home Assistant app runs the [Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI) text-to-speech server locally on the Home Assistant host. It is essentially nothing more than a wrapper around the work the FastKoko folks did, with the goal to have the backend running inside Home Assistant.

It works well alongside the [Kokoro TTS HACS integration](https://github.com/beecho01/Kokoro-TTS).

## Hardware requirements

This app runs Kokoro on the CPU, so it needs a fast host. To speak a reply without interruptions, the CPU has to generate audio faster than it plays. If it can't, you hear pauses in long replies, even in the middle of words.

| CPU | Generation speed | Long replies |
| --- | --- | --- |
| Intel Core i3-7100U (2 cores) | About 0.9x real time | Pauses |
| AMD Ryzen 7 PRO 6860Z (8 cores) | About 3x real time | Smooth |

- **Memory**: Plan for at least 2.5 GB of free RAM for this app, on top of what Home Assistant already uses. It uses about 1 GB when idle and about 2 GB while speaking. In a test with a 2 GB limit and no swap, it ran out of memory.
- **Disk**: The image needs about 4.5 GB.
- **Raspberry Pi**: Not recommended. We have not tested a Pi, but a 4-core limit on a much faster ARM laptop only just reached 1x real time, so expect a Pi 5 to fall below that and a Pi 4 to be slower still. 32-bit systems are not supported.

On slower hosts, you can run [Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI) on a faster machine in your network and point the Kokoro TTS integration to it, or use a lighter voice engine such as Piper.

## Installation & Usage

1. If not already done in HA, add this repository (`https://github.com/YaannnTech/HA-Apps`) to **Settings → Apps → Install Apps → ⋮ → Repositories → Add**, or simply press this button: <br>
[![Add Repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FYaannnTech%2FHA-Apps)
2. Install **Kokoro-FastAPI**.
3. Start the app and wait for the model to finish loading.
4. Add and configure the [Kokoro TTS HACS integration](https://github.com/beecho01/Kokoro-TTS).

Click **Open Web UI**, or open `http://HOME_ASSISTANT_IP:8880/web/` to play around with the Kokoro-FastAPI backend.

## Settings

- **API Log Level**: Choose how much detail Kokoro writes to the app log. Options are `Debug`, `Info`, `Warning`, and `Error`. Only `Debug` logs every HTTP request, including Home Assistant's health checks every few seconds.
- **Default Voice**: Default Kokoro voice identifier. Use the **Open Web UI** link to browse and preview voices.
- **Enable Web UI**: Serve Kokoro's browser-based web interface at `http://HOME_ASSISTANT_IP:8880/web/`.
- **Support SSML**: Enable Speech Synthesis Markup Language, including pauses and other supported speech controls.

The app supports Home Assistant `amd64` and `aarch64` installations (CPU-only).

## Related links

- [Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI)
- [Kokoro TTS HACS integration](https://github.com/beecho01/Kokoro-TTS)
