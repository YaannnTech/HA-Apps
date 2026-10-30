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