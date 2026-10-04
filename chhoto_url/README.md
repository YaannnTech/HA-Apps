# Chhoto URL for Home Assistant

This Home Assistant app runs [Chhoto URL](https://github.com/SinTan1729/chhoto-url), a simple, fast, selfhosted URL shortener with no unnecessary features, written in Rust. It is a thin wrapper around the official `sintan1729/chhoto-url` Docker image.

## Installation & Usage

1. If not already done in HA, add this repository (`https://github.com/YaannnTech/HA-Apps`) to **Settings → Apps → Install Apps → ⋮ → Repositories → Add**.
2. Or simply press this button: <br>
[![Add Repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FYaannnTech%2FHA-Apps)
3. Install **Chhoto URL**.
4. (Optional) Set an **Admin Password** on the Configuration tab.
5. Start the app, then open it from the **Chhoto URL** entry in the sidebar, or at `http://HOME_ASSISTANT_IP:4567/`.

## Settings

- **Admin Password**: Optional. Password used to add, list, or delete short links. Leave it blank to allow open access to everyone.
- **Public Site URL**: Optional. Base URL used for the short links, e.g. `https://s.example.com`. Defaults to Home Assistant's host (from its internal URL, else the host IP) plus this app's port, e.g. `http://homeassistant.local:4567`.
- **API Key**: Optional. Enables Chhoto URL's JSON API and CLI usage.
- **Allow public link creation**: Lets anyone create short links without the admin password.
- **Enable WAL database mode**: Recommended for better performance; the database already lives in the app's persistent storage.
- **Redirect Method**: `Permanent` (308, default) or `Temporary` (307).

Optional settings without a value are hidden; enable **Show unused optional configuration options** on the Configuration tab to see them.

The short link database is stored in the app's persistent data storage, so it survives app restarts and updates.

## Related links

- [Chhoto URL Upstream Repository](https://github.com/SinTan1729/chhoto-url)

