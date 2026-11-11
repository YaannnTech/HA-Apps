# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## What this repository is

A Home Assistant app repository (formerly "add-on" repository; use "app" in all user-facing text). `repository.yaml` names the repository; each top-level folder is one app that the Supervisor builds locally from its `Dockerfile`. There is no build system or test suite here: Apps are wrappers around an upstream program, and verification is done by building and running the image with Docker. CI (see below) lints every push and pull request and builds the changed apps.

| App | Upstream | How it wraps it |
| --- | --- | --- |
| `chhoto_url` | `sintan1729/chhoto-url` image | `FROM` the upstream `-alpine` image, sed-patches the minified frontend, `rootfs/run.sh` maps options to `CHHOTO_*` env vars and `exec`s `/app/chhoto-url` |
| `kokoro_fastapi` | `ghcr.io/remsky/kokoro-fastapi-cpu` image | `rootfs/run.sh` maps options to env vars, then `exec`s upstream's `/app/entrypoint.sh` |
| `phoneblock_dongle` | package `phoneblock-dongle` from the upstream APT repository (haumacher/phoneblock) | installs the pinned package on Home Assistant's Debian base image, runs it behind nginx for Ingress |
| `tuya_ipc_bridge` | a pinned commit of the YaannnTech/tuya-ipc-terminal fork, a release since app 0.10.0 (`TUYA_IPC_TERMINAL_REF` in `build.yaml` and the Dockerfile, keep both equal) | multi-stage Go build with one sed patch (QR login URL); `run.sh` supervises the RTSP server, `qr_server.py` is the Ingress login UI |

## Anatomy of an app

- `config.yaml`: Supervisor manifest. `version` must be bumped for Home Assistant to offer an update and rebuild the image; text-only changes can ship without a bump.
- `translations/en.yaml`: labels for the Configuration tab. Its keys must match the `schema` keys in `config.yaml` exactly (no leftovers for removed options).
- `CHANGELOG.md`: newest version first, one entry per version bump; older entries are history and stay as written.
- `README.md` (Info tab); `tuya_ipc_bridge` also has `DOCS.md` (Documentation tab).
- `run.sh` (or `rootfs/run.sh`, copied to `/run.sh`): reads `/data/options.json` (directly with jq/python, or via bashio in apps on a Home Assistant base image) and talks to the Supervisor API at `http://supervisor` with `$SUPERVISOR_TOKEN`.

## Versioning

- Apps wrapping an upstream release use the upstream version plus a fourth component: `7.9.3.1` = upstream 7.9.3, first app build. Reset the last digit to `.1` when upstream changes.
- `phoneblock_dongle` follows the PhoneBlock firmware version, with the app build after a dash: `1.7.0-beta7-1` = package `1.7.0~beta7`, first app build; a stable release becomes `1.7.0.1` under the rule above. A fourth dot component on a pre-release (`1.7.0-beta7.1`) does not sort correctly in AwesomeVersion; the dash form does, including the step to `1.7.0.1`. Use the dash only on pre-releases: On a stable version, `7.9.5-1` is a semver pre-release that sorts below `7.9.5`, and `7.9.5-10` sorts below `7.9.5-9`.
- PhoneBlock renumbered the 1.7.0 line to 2.0.0 (haumacher/phoneblock#719): After `1.7.0-beta9-1` come `2.0.0-betaN-1`, `2.0.0-rcN-1` (first: `2.0.0-rc1-1`) or `2.0.0.1`, and all sort above it.
- `tuya_ipc_bridge` keeps its own semver while the YaannnTech/tuya-ipc-terminal fork is on 0.x: The upstream-plus-fourth-digit form (`0.1.0.1`) would sort below the installed `0.9.5`, so the Supervisor would never offer it. App `0.10.0` builds fork `v0.1.0`; each new fork release gets the next app minor version (fork `v0.2.0` -> app `0.11.0`), app-only changes a patch bump (`0.10.1`). Every CHANGELOG entry names the fork release it builds.
- When the fork releases `v1.0.0`, `tuya_ipc_bridge` switches to the normal scheme (`1.0.0.1` = fork 1.0.0, first app build), which sorts above every 0.x version. Then add a comment with the release tag next to `TUYA_IPC_TERMINAL_REF` and a `tuya_ipc_bridge` entry in `UPSTREAM_PINS` in `.github/scripts/check_apps.py`.
- The Supervisor compares versions with AwesomeVersion; check that a new scheme still sorts above the installed one.

## Cross-file details that are easy to break

- **Frontend/source patches are verified at build time.** Every `sed -i` in a Dockerfile is followed by a `grep -q` (or `! grep -q`) check so the build fails if upstream changed the patched code. Keep that pattern for new patches. For `chhoto_url`, also check the minified variable names around a patch still mean the same thing after an upstream update (the build check only proves the text was inserted).
- **Chhoto URL option parsing:** `get_option` in `chhoto_url/rootfs/run.sh` must not use jq's `//`, which treats `false` as missing.
- **Chhoto URL session key:** `run.sh` generates `/data/session_master_key` once (64 random bytes, URL-safe base64 without padding, as upstream reads it since 7.9.8) and exports it as `CHHOTO_SESSION_MASTER_KEY`. Keys from app 7.9.5.1 are hex, which still decodes as base64 (96 bytes) and is kept. Upstream falls back to a random per-start key if the value does not decode to at least 64 bytes; the startup log must say "Using provided session master key."
- **Kokoro logging:** upstream hardcodes `uvicorn --log-level debug`; `run.sh` sets `UVICORN_ACCESS_LOG=false` unless API Log Level is Debug, to keep the health check's `/health` requests out of the log.
- **PhoneBlock package pinning:** the Dockerfile installs `phoneblock-dongle=${PHONEBLOCK_VERSION}` from https://haumacher.github.io/phoneblock/apt/ (the repository keeps older versions). To update, set `PHONEBLOCK_VERSION` (Debian syntax, `2.0.0` or `2.1.0~beta1`) and `version` in `config.yaml` together. `PHONEBLOCK_CHANNEL` is `stable` since 2.0.0; a pre-release is only in the `beta` channel, so pinning one needs `beta` again. `PHONEBLOCK_SUITE` must match the Debian release of the `base-debian` image. The signing key is checked against `PHONEBLOCK_REPO_FINGERPRINT`. The package keeps its state in `/var/lib/phoneblock`, a symlink to `/data`. `run.sh` sets `PHONEBLOCK_PLATFORM="Linux; HA"` for the User-Agent.
- **PhoneBlock token option:** `phoneblock_token` is optional, because the web UI can link the account by code behind Ingress and the service stores that token in `dongle.conf`. In `run.sh` an empty option must keep the stored `pb_token` (unlike `contact_host`/`contact_port`, where empty removes the key) and must skip the start-up token check, so the web UI stays reachable.
- **PhoneBlock upload limit:** `client_max_body_size` in `phoneblock_dongle/nginx.conf` must cover the service's largest request body (`STORAGE_DIALOG_PLAIN_FS_MAX`, 2 MB).
- **mawk:** Debian's `awk` is mawk, which holds back piped input; the live log filter in `run.sh` uses `mawk -W interactive`.
- **Dynamic Ingress ports:** `phoneblock_dongle` and `tuya_ipc_bridge` use `host_network: true` with `ingress_port: 0`; `run.sh` reads the real port (and the slug, which the Supervisor prefixes with a repository hash) from `/addons/self/info`. Notification links use `/app/<slug>`.
- **Health checks:** `chhoto_url` and `kokoro_fastapi` use a Docker `HEALTHCHECK`, not the `watchdog` option (Frenck's linter rejects it). The Supervisor reports the app as started once the container is healthy and, with Watchdog on, restarts it when unhealthy. Chhoto's check runs on upstream's internal health port `127.0.0.1:1729/healthz`, not on 4567.
- **Tuya base image:** `tuya_ipc_bridge/build.yaml` sets `BUILD_FROM` per architecture (`hassio-addons/base`); armv7 was dropped because that base is no longer published for it.

## CI

`.github/workflows/ci.yml` runs on pushes to `main`, pull requests and manual runs:

- `git diff --check`, ShellCheck on every `*.sh` (bash for bashio shebangs), Hadolint on every Dockerfile (accepted rules in `.hadolint.yaml`, each with its reason), `ruff check` on every `*.py`.
- `.github/scripts/check_apps.py check`: Translation labels match the options, the first CHANGELOG entry is the config version, the version matches the upstream pin (`UPSTREAM_PINS`), a changed version sorts higher in AwesomeVersion, and a warning when image files changed without a version bump.
- Frenck's app linter on every app, and an amd64 `docker build` of each app whose image files changed (all apps on a manual run), with build args from `build.yaml`.

Tool versions are pinned in the workflow. Locally, the same checks run in a throwaway `python:3.13-alpine` container with the pinned packages. A new app that pins an upstream version needs an entry in `UPSTREAM_PINS`.

## Building and running locally

Build for the host's architecture (`aarch64` on arm64 hosts, `amd64` otherwise); the examples use `aarch64`.

```bash
# Apps with a fixed FROM
docker build -t <app>-test --build-arg BUILD_VERSION=<version> --build-arg BUILD_ARCH=aarch64 <app>/

# tuya_ipc_bridge needs its base image passed in
docker build -t tuya-test --build-arg BUILD_FROM=ghcr.io/hassio-addons/base/aarch64:21.0.11 \
  --build-arg TUYA_IPC_TERMINAL_REF=<commit> tuya_ipc_bridge/

# Run the way the Supervisor does: options.json in a mounted /data
mkdir -p /tmp/appdata && echo '{"api_log_level":"Info", ...}' > /tmp/appdata/options.json
docker run --rm -d -v /tmp/appdata:/data -p 14567:4567 <app>-test
```

There is no Supervisor locally: Supervisor API calls in `run.sh` fail, and `chhoto_url` waits about 5 s for them before starting when no Site URL is set. Apps whose `run.sh` exits without the Supervisor (`phoneblock_dongle`, `tuya_ipc_bridge`) are best tested by running their binary directly with `--entrypoint`.

The PhoneBlock app only installs released packages. To try unreleased upstream changes, run the Linux build from the upstream repository directly (`phoneblock-dongle/firmware/test`, `make phoneblock_linux`) instead of changing the app.
