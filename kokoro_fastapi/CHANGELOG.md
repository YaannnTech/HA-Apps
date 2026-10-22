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