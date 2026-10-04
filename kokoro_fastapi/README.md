# Kokoro-FastAPI Backend for Home Assistant

This Home Assistant app runs the [Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI) text-to-speech server locally on the Home Assistant host. It is essentially nothing more than a wrapper around the work the FastKoko folks did, with the goal to have the backend running inside Home Assistant.

It works well alongside the [Kokoro TTS HACS integration](https://github.com/beecho01/Kokoro-TTS).

## Installation & Usage

1. If not already done in HA, add this repository (`https://github.com/YaannnTech/HA-Apps`) to **Settings → Apps → Install Apps → ⋮ → Repositories → Add**.
2. Or simply press this button: <br>
[![Add Repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FYaannnTech%2FHA-Apps)
3. Install **Kokoro-FastAPI**.
4. Start the app and wait for the model to finish loading.
5. Add and configure the [Kokoro TTS HACS integration](https://github.com/beecho01/Kokoro-TTS).

Click **Open Web UI**, or open `http://HOME_ASSISTANT_IP:8880/web/` to play around with the Kokoro-FastAPI backend.

## Settings

- **API Log Level**: Choose how much detail Kokoro writes to the app log. Options are `Debug`, `Info`, `Warning`, and `Error`.
- **Default Voice**: Default Kokoro voice identifier. Use the **Open Web UI** link to browse and preview voices.
- **Enable Web UI**: Serve Kokoro's browser-based web interface at `http://HOME_ASSISTANT_IP:8880/web/`.
- **Support SSML**: Enable Speech Synthesis Markup Language, including pauses and other supported speech controls.

The app supports Home Assistant `amd64` and `aarch64` installations (CPU-only).

## Related links

- [Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI)
- [Kokoro TTS HACS integration](https://github.com/beecho01/Kokoro-TTS)
