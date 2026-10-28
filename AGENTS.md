# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## What this repository is

A Home Assistant app repository (formerly "add-on" repository; use "app" in all user-facing text). `repository.yaml` names the repository; each top-level folder is one app that the Supervisor builds locally from its `Dockerfile`. There is no build system, test suite or CI here: apps are wrappers around an upstream program, and verification is done by building and running the image with Docker.

| App | Upstream | How it wraps it |
| --- | --- | --- |
| `chhoto_url` | `sintan1729/chhoto-url` image | `FROM` the upstream `-alpine` image, sed-patches the minified frontend, `rootfs/run.sh` maps options to `CHHOTO_*` env vars and `exec`s `/app/chhoto-url` |
| `kokoro_fastapi` | `ghcr.io/remsky/kokoro-fastapi-cpu` image | `rootfs/run.sh` maps options to env vars, then `exec`s upstream's `/app/entrypoint.sh` |
| `phoneblock_dongle` | package `phoneblock-dongle` from the upstream APT repository (haumacher/phoneblock) | installs the pinned package on Home Assistant's Debian base image, runs it behind nginx for Ingress |
| `tuya_ipc_bridge` | branch `fix/rtsp-stream-lockup` of the YaannnTech/tuya-ipc-terminal fork | multi-stage Go build with sed patches; `run.sh` supervises the RTSP server, `qr_server.py` is the Ingress login UI |

## Anatomy of an app

- `config.yaml`: Supervisor manifest. `version` must be bumped for Home Assistant to offer an update and rebuild the image; text-only changes can ship without a bump.
- `translations/en.yaml`: labels for the Configuration tab. Its keys must match the `schema` keys in `config.yaml` exactly (no leftovers for removed options).
- `CHANGELOG.md`: newest version first, one entry per version bump; older entries are history and stay as written.
- `README.md` (Info tab); `tuya_ipc_bridge` also has `DOCS.md` (Documentation tab).
- `run.sh` (or `rootfs/run.sh`, copied to `/run.sh`): reads `/data/options.json` (directly with jq/python, or via bashio in apps on a Home Assistant base image) and talks to the Supervisor API at `http://supervisor` with `$SUPERVISOR_TOKEN`.

## Versioning

- Apps wrapping an upstream release use the upstream version plus a fourth component: `7.9.3.1` = upstream 7.9.3, first app build. Reset the last digit to `.1` when upstream changes.
- `phoneblock_dongle` follows the PhoneBlock firmware version, with the app build after a dash: `1.7.0-beta7-1` = package `1.7.0~beta7`, first app build; a stable release becomes `1.7.0.1` under the rule above. A fourth dot component on a pre-release (`1.7.0-beta7.1`) does not sort correctly in AwesomeVersion; the dash form does, including the step to `1.7.0.1`. Use the dash only on pre-releases: on a stable version, `7.9.5-1` is a semver pre-release that sorts below `7.9.5`, and `7.9.5-10` sorts below `7.9.5-9`.
- `tuya_ipc_bridge` has its own semver (`0.9.3`).
- The Supervisor compares versions with AwesomeVersion; check that a new scheme still sorts above the installed one.

## Cross-file details that are easy to break

- **Frontend/source patches are verified at build time.** Every `sed -i` in a Dockerfile is followed by a `grep -q` (or `! grep -q`) check so the build fails if upstream changed the patched code. Keep that pattern for new patches. For `chhoto_url`, also check the minified variable names around a patch still mean the same thing after an upstream update (the build check only proves the text was inserted).
- **Chhoto URL option parsing:** `get_option` in `chhoto_url/rootfs/run.sh` must not use jq's `//`, which treats `false` as missing.
- **Chhoto URL session key:** `run.sh` generates `/data/session_master_key` once (64 random bytes, hex) and exports it as `CHHOTO_SESSION_MASTER_KEY`. Upstream silently falls back to a random per-start key if the value fails its length or strength check; the startup log must say "Using provided session master key."
- **Kokoro logging:** upstream hardcodes `uvicorn --log-level debug`; `run.sh` sets `UVICORN_ACCESS_LOG=false` unless API Log Level is Debug, to keep the watchdog's `/health` requests out of the log.
- **PhoneBlock package pinning:** the Dockerfile installs `phoneblock-dongle=${PHONEBLOCK_VERSION}` from https://haumacher.github.io/phoneblock/apt/ (the repository keeps older versions). To update, set `PHONEBLOCK_VERSION` (Debian syntax, `1.7.0~beta8`) and `version` in `config.yaml` together, and `PHONEBLOCK_CHANNEL` to `stable` once a stable release exists. `PHONEBLOCK_SUITE` must match the Debian release of the `base-debian` image. The signing key is checked against `PHONEBLOCK_REPO_FINGERPRINT`. The package keeps its state in `/var/lib/phoneblock`, a symlink to `/data`. `run.sh` sets `PHONEBLOCK_PLATFORM="Linux; HA"` for the User-Agent.
- **mawk:** Debian's `awk` is mawk, which holds back piped input; the live log filter in `run.sh` uses `mawk -W interactive`.
- **Dynamic Ingress ports:** `phoneblock_dongle` and `tuya_ipc_bridge` use `host_network: true` with `ingress_port: 0`; `run.sh` reads the real port (and the slug, which the Supervisor prefixes with a repository hash) from `/addons/self/info`. Notification links use `/app/<slug>`.
- **Tuya base image:** `tuya_ipc_bridge/build.yaml` sets `BUILD_FROM` per architecture (`hassio-addons/base`); armv7 was dropped because that base is no longer published for it.

## Building and running locally

Build for the host's architecture (`aarch64` on arm64 hosts, `amd64` otherwise); the examples use `aarch64`.

```bash
# Apps with a fixed FROM
docker build -t <app>-test --build-arg BUILD_VERSION=<version> --build-arg BUILD_ARCH=aarch64 <app>/

# tuya_ipc_bridge needs its base image passed in
docker build -t tuya-test --build-arg BUILD_FROM=ghcr.io/hassio-addons/base/aarch64:21.0.8 \
  --build-arg TUYA_IPC_TERMINAL_REF=fix/rtsp-stream-lockup tuya_ipc_bridge/

# Run the way the Supervisor does: options.json in a mounted /data
mkdir -p /tmp/appdata && echo '{"api_log_level":"Info", ...}' > /tmp/appdata/options.json
docker run --rm -d -v /tmp/appdata:/data -p 14567:4567 <app>-test
```

There is no Supervisor locally: Supervisor API calls in `run.sh` fail, and `chhoto_url` waits about 5 s for them before starting when no Site URL is set. Apps whose `run.sh` exits without the Supervisor (`phoneblock_dongle`, `tuya_ipc_bridge`) are best tested by running their binary directly with `--entrypoint`.

The PhoneBlock app only installs released packages. To try unreleased upstream changes, run the Linux build from the upstream repository directly (`phoneblock-dongle/firmware/test`, `make phoneblock_linux`) instead of changing the app.
