"""Consistency checks for the apps in this repository, run by CI.

  check_apps.py check [--base REF]   check every app; with --base, also compare versions
  check_apps.py changed --base REF   print the apps changed since REF as a JSON list
  check_apps.py build-args APP ARCH  print `--build-arg` options for `docker build`

Errors and warnings are printed as GitHub Actions annotations.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]

# Files that only change the app's text in Home Assistant; everything else
# changes the image or the Supervisor manifest and needs a version bump to
# reach users.
TEXT_ONLY = re.compile(
    r"^(README\.md|DOCS\.md|CHANGELOG\.md|icon\.png|logo\.png|translations/.*)$"
)

# How each app pins its upstream release, and how the app version must start.
UPSTREAM_PINS = {
    "chhoto_url": (
        r"^FROM sintan1729/chhoto-url:(\S+)-alpine$",
        lambda v: rf"{re.escape(v)}\.\d+",
    ),
    "kokoro_fastapi": (
        r"^FROM ghcr\.io/remsky/kokoro-fastapi-cpu:v(\S+)$",
        lambda v: rf"{re.escape(v)}\.\d+",
    ),
    # 1.7.0~beta9 -> 1.7.0-beta9-1 (pre-release), 1.7.0 -> 1.7.0.1 (stable)
    "phoneblock_dongle": (
        r"^ARG PHONEBLOCK_VERSION=(\S+)$",
        lambda v: (
            rf"{re.escape(v.replace('~', '-'))}-\d+"
            if "~" in v
            else rf"{re.escape(v)}\.\d+"
        ),
    ),
}

failed = False


def error(path, msg):
    global failed
    failed = True
    print(f"::error file={path}::{msg}")


def warning(path, msg):
    print(f"::warning file={path}::{msg}")


def apps():
    return sorted(p.parent.name for p in ROOT.glob("*/config.yaml"))


def git(*args):
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    )


def changed_files(base, app):
    out = git("diff", "--name-only", f"{base}...HEAD", "--", app)
    if out.returncode != 0:
        out = git("diff", "--name-only", base, "HEAD", "--", app)
    return [f[len(app) + 1 :] for f in out.stdout.split()]


def check_app(app, base):
    from awesomeversion import AwesomeVersion

    config_path = f"{app}/config.yaml"
    config = yaml.safe_load((ROOT / config_path).read_text())
    version = str(config["version"])

    schema = set((config.get("schema") or {}).keys())
    translations_path = ROOT / app / "translations/en.yaml"
    if translations_path.exists():
        labels = set(
            (
                (yaml.safe_load(translations_path.read_text()) or {}).get(
                    "configuration"
                )
                or {}
            ).keys()
        )
        for key in sorted(schema - labels):
            error(f"{app}/translations/en.yaml", f"Option '{key}' has no label")
        for key in sorted(labels - schema):
            error(
                f"{app}/translations/en.yaml",
                f"Label '{key}' has no option in config.yaml",
            )
    elif schema:
        error(config_path, "Options without translations/en.yaml")

    heading = next(
        (
            l
            for l in (ROOT / app / "CHANGELOG.md").read_text().splitlines()
            if l.startswith("# ")
        ),
        "",
    )
    if heading != f"# {version}":
        error(
            f"{app}/CHANGELOG.md", f"First entry is '{heading}', expected '# {version}'"
        )

    if app in UPSTREAM_PINS:
        pin_re, version_re = UPSTREAM_PINS[app]
        pins = re.findall(pin_re, (ROOT / app / "Dockerfile").read_text(), re.MULTILINE)
        if len(pins) != 1:
            error(f"{app}/Dockerfile", "Upstream version pin not found")
        elif not re.fullmatch(version_re(pins[0]), version):
            error(
                config_path,
                f"Version {version} does not match the upstream pin {pins[0]}",
            )

    if not base:
        return
    old = git("show", f"{base}:{config_path}")
    if old.returncode != 0:
        return  # new app
    old_version = str(yaml.safe_load(old.stdout)["version"])
    if old_version != version:
        if not AwesomeVersion(version) > AwesomeVersion(old_version):
            error(
                config_path,
                f"Version {version} does not sort above {old_version} (AwesomeVersion)",
            )
    else:
        image_files = [f for f in changed_files(base, app) if not TEXT_ONLY.match(f)]
        if image_files:
            warning(
                config_path,
                f"{', '.join(image_files)} changed without a version bump; users get it with the next bump",
            )


def build_args(app, arch):
    args = [
        f"BUILD_VERSION={yaml.safe_load((ROOT / app / 'config.yaml').read_text())['version']}",
        f"BUILD_ARCH={arch}",
    ]
    build_yaml = ROOT / app / "build.yaml"
    if build_yaml.exists():
        build = yaml.safe_load(build_yaml.read_text()) or {}
        if arch in (build.get("build_from") or {}):
            args.append(f"BUILD_FROM={build['build_from'][arch]}")
        args += [f"{k}={v}" for k, v in (build.get("args") or {}).items()]
    print(" ".join(f"--build-arg {a}" for a in args))


def main(argv):
    base = argv[argv.index("--base") + 1] if "--base" in argv else ""
    if argv[0] == "check":
        for app in apps():
            check_app(app, base)
        sys.exit(1 if failed else 0)
    elif argv[0] == "changed":
        if not base:
            print(json.dumps(apps()))
        else:
            print(
                json.dumps(
                    [
                        a
                        for a in apps()
                        if any(not TEXT_ONLY.match(f) for f in changed_files(base, a))
                    ]
                )
            )
    elif argv[0] == "build-args":
        build_args(argv[1], argv[2])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
