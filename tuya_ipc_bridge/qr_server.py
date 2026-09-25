#!/usr/bin/env python3
"""Ingress web UI: lets a user add a Tuya account via QR-code login in the browser."""
import argparse
import html
import io
import json
import re
import subprocess
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

import qrcode
import qrcode.image.svg

REGIONS = ["eu-central", "eu-east", "us-west", "us-east", "china", "india"]
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def render_qr_svg(data):
    img = qrcode.make(data, image_factory=qrcode.image.svg.SvgPathImage)
    buf = io.BytesIO()
    img.save(buf)
    return buf.getvalue()

JOBS = {}
JOBS_LOCK = threading.Lock()


def run_qr_job(job_id, region, email):
    job = JOBS[job_id]
    try:
        proc = subprocess.Popen(
            ["tuya-ipc-terminal", "auth", "add", region, email, "--qr"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except OSError as exc:
        job["state"] = "error"
        job["message"] = f"Failed to start CLI: {exc}"
        return

    job["process"] = proc
    for raw_line in iter(proc.stdout.readline, ""):
        line = raw_line.rstrip("\n")
        job["log"].append(line)

        if line.startswith("QR_LOGIN_URL:"):
            job["url"] = line[len("QR_LOGIN_URL:"):]
            job["state"] = "waiting_for_scan"
        elif "already exists" in line or "Continue anyway?" in line:
            proc.stdin.write("y\n")
            proc.stdin.flush()
        elif "Press Enter after scanning" in line:
            proc.stdin.write("\n")
            proc.stdin.flush()
        elif "Successfully added" in line:
            job["state"] = "success"
            job["message"] = line
        elif "authentication failed" in line or "error polling" in line.lower():
            job["state"] = "error"
            job["message"] = line

    proc.wait()
    if job["state"] not in ("success", "error"):
        job["state"] = "error"
        job["message"] = "Process exited before login completed."


def new_job(region, email):
    job_id = uuid.uuid4().hex
    JOBS[job_id] = {
        "region": region,
        "email": email,
        "state": "starting",
        "url": None,
        "message": "",
        "log": [],
        "process": None,
    }
    thread = threading.Thread(target=run_qr_job, args=(job_id, region, email), daemon=True)
    thread.start()
    return job_id


def run_password_job(job_id, region, email, password):
    job = JOBS[job_id]
    try:
        proc = subprocess.run(
            ["/usr/bin/add_account.exp", region, email, password],
            capture_output=True,
            text=True,
            timeout=90,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        job["state"] = "error"
        job["message"] = f"Failed to run login: {exc}"
        return

    if proc.returncode == 0:
        job["state"] = "success"
        job["message"] = "Account added successfully."
    else:
        job["state"] = "error"
        job["message"] = "Authentication failed. Check the email/password and try again."


def new_password_job(region, email, password):
    job_id = uuid.uuid4().hex
    JOBS[job_id] = {
        "region": region,
        "email": email,
        "state": "starting",
        "url": None,
        "message": "",
        "log": [],
        "process": None,
    }
    thread = threading.Thread(target=run_password_job, args=(job_id, region, email, password), daemon=True)
    thread.start()
    return job_id


def get_auth_list():
    try:
        result = subprocess.run(
            ["tuya-ipc-terminal", "auth", "list"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.stdout or result.stderr
    except (OSError, subprocess.SubprocessError) as exc:
        return f"Failed to list accounts: {exc}"


PAGE_HEAD = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Tuya IPC Bridge</title>
<style>
body { font-family: sans-serif; margin: 2em; background:#111; color:#eee; }
pre { background:#000; color:#0f0; padding:1em; overflow-x:auto; }
label { display:block; margin-top:0.75em; }
select, input { padding:0.4em; width:100%; max-width:320px; }
button { margin-top:1em; padding:0.6em 1.2em; }
#qrcode { margin-top:1em; background:#fff; padding:16px; display:inline-block; border-radius:4px; }
#qrcode img { display:block; }
.state { font-weight:bold; }
</style></head><body>
"""
PAGE_TAIL = "</body></html>"


def render_index(base):
    options = "".join(f'<option value="{r}">{r}</option>' for r in REGIONS)
    accounts = html.escape(get_auth_list())
    return (
        PAGE_HEAD
        + "<h1>Tuya IPC Bridge</h1>"
        + "<h2>Authenticated accounts</h2>"
        + f"<pre>{accounts}</pre>"
        + "<h2>Add account via QR code</h2>"
        + f'<form method="POST" action="{base}/qr/start">'
        + f'<label>Region <select name="region">{options}</select></label>'
        + '<label>Email <input name="email" type="email" required></label>'
        + '<button type="submit">Start QR login</button>'
        + "</form>"
        + "<h2>Add account via email/password (likely only works for Tuya & Smart Life accounts, not any other app variants)</h2>"
        + f'<form method="POST" action="{base}/password/start">'
        + f'<label>Region <select name="region">{options}</select></label>'
        + '<label>Email <input name="email" type="email" required></label>'
        + '<label>Password <input name="password" type="password" required></label>'
        + '<button type="submit">Log in</button>'
        + "</form>"
        + PAGE_TAIL
    )


def render_qr_page(base, job_id):
    return (
        PAGE_HEAD
        + "<h1>Scan with the Tuya Smart / Smart Life app</h1>"
        + '<div id="qrcode">Waiting for QR code&hellip;</div>'
        + '<p class="state" id="state">starting</p>'
        + '<p id="message"></p>'
        + f'<p><a href="{base}/">&larr; Back</a></p>'
        + "<script>"
        + f'const jobId = "{job_id}"; const base = "{base}";'
        + """
let rendered = false;
async function poll() {
  const res = await fetch(`${base}/qr/${jobId}/status`);
  const data = await res.json();
  document.getElementById('state').textContent = data.state;
  document.getElementById('message').textContent = data.message || '';
  if (data.url && !rendered) {
    rendered = true;
    document.getElementById('qrcode').innerHTML =
      `<img src="${base}/qr/${jobId}/image" width="256" height="256" alt="QR code">`;
  }
  if (data.state !== 'success' && data.state !== 'error') {
    setTimeout(poll, 1500);
  }
}
poll();
"""
        + "</script>"
        + PAGE_TAIL
    )


def render_password_page(base, job_id):
    return (
        PAGE_HEAD
        + "<h1>Logging in&hellip;</h1>"
        + '<p class="state" id="state">starting</p>'
        + '<p id="message"></p>'
        + f'<p><a href="{base}/">&larr; Back</a></p>'
        + "<script>"
        + f'const jobId = "{job_id}"; const base = "{base}";'
        + """
async function poll() {
  const res = await fetch(`${base}/password/${jobId}/status`);
  const data = await res.json();
  document.getElementById('state').textContent = data.state;
  document.getElementById('message').textContent = data.message || '';
  if (data.state !== 'success' && data.state !== 'error') {
    setTimeout(poll, 1500);
  }
}
poll();
"""
        + "</script>"
        + PAGE_TAIL
    )


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _base(self):
        # HA Ingress proxies requests under a per-session token prefix; this
        # header carries that prefix so generated links/forms stay under it.
        return self.headers.get("X-Ingress-Path", "")

    def _send(self, code, body, content_type="text/html; charset=utf-8"):
        encoded = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        base = self._base()
        if self.path == "/" or self.path == "":
            self._send(200, render_index(base))
        elif self.path.startswith("/qr/") and self.path.endswith("/image"):
            job_id = self.path.split("/")[2]
            job = JOBS.get(job_id)
            if not job or not job["url"]:
                self._send(404, "QR code not ready yet")
                return
            self._send(200, render_qr_svg(job["url"]), "image/svg+xml")
        elif self.path.startswith("/qr/") and self.path.endswith("/status"):
            job_id = self.path.split("/")[2]
            job = JOBS.get(job_id)
            if not job:
                self._send(404, json.dumps({"state": "error", "message": "unknown job"}), "application/json")
                return
            self._send(
                200,
                json.dumps({"state": job["state"], "url": job["url"], "message": job["message"]}),
                "application/json",
            )
        elif self.path.startswith("/qr/"):
            job_id = self.path.split("/")[2]
            if job_id not in JOBS:
                self._send(404, "Unknown job")
                return
            self._send(200, render_qr_page(base, job_id))
        elif self.path.startswith("/password/") and self.path.endswith("/status"):
            job_id = self.path.split("/")[2]
            job = JOBS.get(job_id)
            if not job:
                self._send(404, json.dumps({"state": "error", "message": "unknown job"}), "application/json")
                return
            self._send(
                200,
                json.dumps({"state": job["state"], "message": job["message"]}),
                "application/json",
            )
        elif self.path.startswith("/password/"):
            job_id = self.path.split("/")[2]
            if job_id not in JOBS:
                self._send(404, "Unknown job")
                return
            self._send(200, render_password_page(base, job_id))
        else:
            self._send(404, "Not found")

    def do_POST(self):
        if self.path == "/qr/start":
            length = int(self.headers.get("Content-Length", 0))
            fields = parse_qs(self.rfile.read(length).decode("utf-8"))
            region = fields.get("region", [""])[0]
            email = fields.get("email", [""])[0]

            if region not in REGIONS:
                self._send(400, "Invalid region")
                return
            if not EMAIL_RE.match(email):
                self._send(400, "Invalid email")
                return

            job_id = new_job(region, email)
            self.send_response(303)
            self.send_header("Location", f"{self._base()}/qr/{job_id}")
            self.end_headers()
        elif self.path == "/password/start":
            length = int(self.headers.get("Content-Length", 0))
            fields = parse_qs(self.rfile.read(length).decode("utf-8"))
            region = fields.get("region", [""])[0]
            email = fields.get("email", [""])[0]
            password = fields.get("password", [""])[0]

            if region not in REGIONS:
                self._send(400, "Invalid region")
                return
            if not EMAIL_RE.match(email):
                self._send(400, "Invalid email")
                return
            if not password:
                self._send(400, "Password required")
                return

            job_id = new_password_job(region, email, password)
            self.send_response(303)
            self.send_header("Location", f"{self._base()}/password/{job_id}")
            self.end_headers()
        else:
            self._send(404, "Not found")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    server.serve_forever()
