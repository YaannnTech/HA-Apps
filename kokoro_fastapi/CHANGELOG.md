# 0.10.0.1

- Update Kokoro-FastAPI to [v0.10.0](https://github.com/remsky/Kokoro-FastAPI/releases/tag/v0.10.0): Memory no longer keeps growing with every new text length, because the CPU image now uses the jemalloc memory allocator (remsky/Kokoro-FastAPI#594), and it is returned to the system when the app is idle.
- Also new upstream: websocket and OpenAI Realtime compatible endpoints for voice agents, and the OpenAI voice names marin, cedar, verse and ballad. Optional API keys exist upstream but are not exposed as an app option.

# 0.9.2.2

- Home Assistant now checks the app's health with a Docker health check on `/health`. The app shows as started once the model is loaded, and with **Watchdog** on, Home Assistant restarts it when it turns unhealthy. The health checks stay out of the log unless API Log Level is Debug.

# 0.9.2.1

- Update Kokoro-FastAPI to [v0.9.2](https://github.com/remsky/Kokoro-FastAPI/releases/tag/v0.9.2): The health check and voice list stay responsive during generation, words around an unspaced ellipsis are read as words instead of spelled out, and `1,5s` reads as "one point five seconds". A sentence that fails to generate now fails the request instead of going silently missing.

# 0.9.1.1

- Update Kokoro-FastAPI to [v0.9.1](https://github.com/remsky/Kokoro-FastAPI/releases/tag/v0.9.1): Dependency updates for security advisories, the startup log shows the configured port instead of the default one, and the web player keeps text typed with an input method editor (IME).

# 0.9.0.3

- Quieter log: HTTP request lines, including Home Assistant's health check every few seconds, are only logged when **API Log Level** is set to `Debug`.

# 0.9.0.2

- Remove the leftover "Download model at startup" label for a setting that no longer exists; the model is always downloaded when missing.
- Drop the advice to disable SSML from its setting description, which contradicted the default of SSML being enabled.

# 0.9.0.1

- Initial release of the CPU-only Kokoro-FastAPI backend as a Home Assistant app for `amd64` and `aarch64`.
- Expose the OpenAI-compatible API and browser-based web player on port `8880`.
- Add app settings for API log level, default voice, web player availability, and SSML support.
- Include a health check endpoint and persistent app data storage.
