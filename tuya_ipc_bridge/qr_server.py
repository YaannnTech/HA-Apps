#!/usr/bin/env python3
"""Ingress web UI: lets a user add a Tuya account via QR-code login in the browser."""
import argparse
import html
import io
import json
import re
import subprocess
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

import qrcode
import qrcode.image.svg

# Used when "auth show-regions" cannot be read; the binary's list wins.
FALLBACK_REGIONS = {
    "eu-central": "Central Europe",
    "eu-east": "East Europe",
    "us-west": "West America",
    "us-east": "East America",
    "china": "China",
    "india": "India",
    "brazil": "Brazil (West America data center)",
}
REGION_LINE_RE = re.compile(r"^(\S+)\s+(\S+\.ismartlife\.me)\s+(.+?)\s*$")


def load_regions():
    """Read the regions from the binary, so the form offers exactly what it supports."""
    try:
        out = subprocess.run(
            ["tuya-ipc-terminal", "auth", "show-regions"],
            capture_output=True, text=True, timeout=10, check=False,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return dict(FALLBACK_REGIONS)
    regions = {}
    for line in out.splitlines():
        match = REGION_LINE_RE.match(line)
        if match:
            regions[match.group(1)] = match.group(3)
    return regions or dict(FALLBACK_REGIONS)


REGIONS = load_regions()
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def render_qr_svg(data):
    img = qrcode.make(data, image_factory=qrcode.image.svg.SvgPathImage)
    buf = io.BytesIO()
    img.save(buf)
    return buf.getvalue()


JOBS = {}

# run.sh watches for this file; it then refreshes the cameras, restarts the RTSP server
# and re-checks the sessions, so a new login takes effect without restarting the app.
LOGIN_MARKER = "/data/.login-done"


def signal_login(job):
    """Signal a completed login and report a marker failure to the job."""
    try:
        with open(LOGIN_MARKER, "w", encoding="ascii"):
            pass
    except OSError as exc:
        print(f"Failed to signal login: {exc}", file=sys.stderr, flush=True)
        job["message"] += " Could not restart camera discovery. Restart the app."


def start_job(target, region, email, *args):
    job_id = uuid.uuid4().hex
    JOBS[job_id] = {"region": region, "email": email, "state": "starting", "url": None, "message": ""}
    thread = threading.Thread(target=target, args=(job_id, region, email, *args), daemon=True)
    thread.start()
    return job_id


def run_qr_job(job_id, region, email):
    """Run a QR login and signal the app after success."""
    job = JOBS[job_id]
    job["state"] = "running"
    success = False
    try:
        proc = subprocess.Popen(
            ["tuya-ipc-terminal", "auth", "add", region, email, "--qr", "--print-qr-url"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except OSError as exc:
        job["message"] = f"Failed to start CLI: {exc}"
        job["state"] = "error"
        return

    for raw_line in iter(proc.stdout.readline, ""):
        line = raw_line.rstrip("\n")

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
            success = True
            job["message"] = line
        elif "authentication failed" in line or "error polling" in line.lower():
            job["message"] = line
            job["state"] = "error"

    proc.wait()
    if success and job["state"] != "error":
        signal_login(job)
        job["state"] = "success"
    elif job["state"] != "error":
        job["message"] = "Process exited before login completed."
        job["state"] = "error"


def run_password_job(job_id, region, email, password):
    """Run a password login and signal the app after success."""
    job = JOBS[job_id]
    job["state"] = "running"
    try:
        proc = subprocess.run(
            ["/usr/bin/add_account.exp", region, email, password],
            capture_output=True,
            check=False,
            text=True,
            timeout=90,
        )
    except subprocess.TimeoutExpired:
        # Never format the exception: its text contains the command line with the password.
        job["message"] = "The CLI did not respond in time. Retry and check the app log."
        job["state"] = "error"
        return
    except OSError as exc:
        job["message"] = f"Failed to run login. {exc.strerror or ''}".strip()
        job["state"] = "error"
        return

    output = f"{proc.stdout or ''}{proc.stderr or ''}".replace(password, "[REDACTED]")
    if output:
        print(output, file=sys.stderr, end="" if output.endswith("\n") else "\n", flush=True)

    if proc.returncode == 0:
        job["message"] = "Account added successfully."
        signal_login(job)
        job["state"] = "success"
    else:
        if proc.returncode == 1:
            job["message"] = (
                "Authentication failed. Check the email/password and try again. "
                "OEM accounts (such as LittleElf and many others) cannot use password login; use QR login."
            )
        elif proc.returncode == 2:
            job["message"] = "The CLI did not respond in time. Retry and check the app log."
        else:
            job["message"] = "Login ended without success. Check the app log."
        job["state"] = "error"


def get_auth_list():
    try:
        result = subprocess.run(
            ["tuya-ipc-terminal", "auth", "list"],
            capture_output=True,
            check=False,
            text=True,
            timeout=15,
        )
        return result.stdout or result.stderr
    except (OSError, subprocess.SubprocessError) as exc:
        return f"Failed to list accounts: {exc}"


PAGE_HEAD = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tuya IPC Bridge</title>
<style>
:root {
  color-scheme: light dark;
  --background: #f3f5f7; --card: #fff; --text: #212b36; --muted: #526371;
  --border: #bac6ce; --input: #fff; --accent: #006a9b; --primary: #03a9f4;
  --primary-text: #00334a; --soft: #e9f5fb; --success: #17613c;
  --success-bg: #e3f4ea; --error: #a32121; --error-bg: #fceaea;
  --warning: #754900; --warning-bg: #fff0c2;
  --shadow: 0 2px 12px rgba(0, 0, 0, .09);
}
@media (prefers-color-scheme: dark) {
  :root {
    --background: #111820; --card: #202b34; --text: #edf3f7; --muted: #b7c5cf;
    --border: #637584; --input: #17212a; --accent: #70d0ff; --primary-text: #00334a;
    --soft: #153849; --success: #a4e5bc; --success-bg: #193d2d;
    --error: #ffb6b6; --error-bg: #482829; --shadow: 0 2px 12px rgba(0, 0, 0, .25);
    --warning: #ffda80; --warning-bg: #493710;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--background); color: var(--text);
  font: 16px/1.5 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
main { width: min(100% - 32px, 680px); margin: 36px auto 48px; }
h1 { font-size: 1.7rem; line-height: 1.2; margin: 0 0 8px; }
h2 { font-size: 1.2rem; line-height: 1.3; margin: 0 0 8px; }
p { margin: 0; }
.subtitle, .hint, .empty { color: var(--muted); }
.subtitle { margin-bottom: 24px; }
.card {
  background: var(--card); border-radius: 14px; padding: 24px;
  box-shadow: var(--shadow); margin-bottom: 16px;
}
.hint { font-size: .9rem; margin: 8px 0 18px; }
label { display: block; font-weight: 600; margin: 16px 0 6px; }
input, select, button { font: inherit; }
input, select {
  width: 100%; min-width: 0; border: 1px solid var(--border); border-radius: 8px;
  padding: 11px 12px; color: var(--text); background: var(--input);
}
input:focus-visible, select:focus-visible, button:focus-visible, a:focus-visible {
  outline: 3px solid var(--primary); outline-offset: 2px;
}
button, .button {
  display: inline-block; border: 0; border-radius: 8px; padding: 11px 18px;
  font-weight: 700; text-align: center; cursor: pointer; text-decoration: none;
}
.primary { background: var(--primary); color: var(--primary-text); }
.primary:visited { color: var(--primary-text); }
button:disabled { opacity: .5; cursor: not-allowed; }
a, a:visited { color: var(--accent); }
.submit { width: 100%; margin-top: 24px; }
.switch { display: flex; padding: 4px; border-radius: 10px; background: var(--background); }
.switch label {
  flex: 1; margin: 0; padding: 8px; border-radius: 7px; text-align: center;
  cursor: pointer; font-weight: 600;
}
.switch label:has(input:checked) { background: var(--primary); color: var(--primary-text); }
.switch label:has(input:focus-visible) { outline: 3px solid var(--accent); outline-offset: 2px; }
.switch input { position: absolute; width: 1px; height: 1px; opacity: 0; }
[hidden] { display: none !important; }
.account { padding: 14px 0; border-top: 1px solid var(--border); overflow-wrap: anywhere; }
.account:first-child { border-top: 0; padding-top: 4px; }
.account:last-child { padding-bottom: 0; }
.account-heading { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
.badge {
  border-radius: 999px; padding: 2px 9px; font-size: .75rem; font-weight: 700;
  color: var(--text); background: var(--background);
}
.badge.valid { color: var(--success); background: var(--success-bg); }
.badge.old { color: var(--warning); background: var(--warning-bg); }
.badge.invalid { color: var(--error); background: var(--error-bg); }
.account-details { color: var(--muted); font-size: .9rem; }
pre {
  white-space: pre-wrap; overflow-wrap: anywhere; margin: 12px 0 0;
  background: var(--background); border-radius: 8px; padding: 14px;
  color: var(--text); font-size: .85rem;
}
.progress { text-align: center; }
.progress h1 { margin-bottom: 8px; }
.progress .hint { margin-bottom: 20px; }
.status {
  display: flex; align-items: center; justify-content: center; gap: 10px;
  font-weight: 700; margin: 20px 0 0;
}
.spinner {
  width: 20px; height: 20px; flex: none; border: 3px solid var(--border);
  border-top-color: var(--accent); border-radius: 50%; animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) { .spinner { animation-duration: 2s; } }
.notice { border-radius: 8px; padding: 14px; margin-top: 18px; overflow-wrap: anywhere; }
.notice.success { color: var(--success); background: var(--success-bg); }
.notice.error { color: var(--error); background: var(--error-bg); }
.notice #notice-title { font-weight: 700; }
.notice p + p { margin-top: 6px; }
#qrcode {
  display: inline-flex; align-items: center; justify-content: center; min-height: 120px;
  max-width: 100%; padding: 16px; border-radius: 10px; background: #fff; color: #38444c;
}
#qrcode img { display: block; width: min(256px, 100%); height: auto; }
.back { margin-top: 24px; width: 100%; }
@media (max-width: 420px) {
  main { margin-top: 24px; }
  .card { padding: 20px; }
}
</style></head><body><main>
"""
PAGE_TAIL = "</main></body></html>"


def render_index(base):
    options = "".join(
        f'<option value="{html.escape(name)}">{html.escape(name)} - {html.escape(desc)}</option>'
        for name, desc in REGIONS.items()
    )
    accounts = html.escape(get_auth_list())
    return (
        PAGE_HEAD
        + '<h1>Tuya IPC Bridge</h1><p class="subtitle">Manage your camera accounts</p>'
        + '<section class="card" aria-labelledby="accounts-title">'
        + '<h2 id="accounts-title">Authenticated accounts</h2>'
        + f'<div id="accounts"><pre>{accounts}</pre></div></section>'
        + '<section class="card" aria-labelledby="add-title">'
        + '<h2 id="add-title">Add or renew account</h2>'
        + '<p class="hint">Choose how to sign in to your account.</p>'
        + f'<form id="login-form" method="POST" action="{base}/qr/start">'
        + '<div class="switch" role="group" aria-label="Login method">'
        + '<label><input type="radio" name="method" value="qr" checked>QR code</label>'
        + '<label><input type="radio" name="method" value="password">Password</label></div>'
        + '<p class="hint">OEM accounts, such as LittleElf, use QR login with their own app.</p>'
        + f'<label for="region">Region</label><select id="region" name="region">{options}</select>'
        + '<label for="email">Email</label><input id="email" name="email" type="email" '
        + 'autocomplete="username" required>'
        + '<div id="password-field" hidden><label for="password">Password</label>'
        + '<input id="password" name="password" type="password" autocomplete="current-password" disabled></div>'
        + '<button class="primary submit" type="submit" id="submit">Start QR login</button></form></section>'
        + """
<script>
const accounts = document.getElementById('accounts');
const raw = accounts.querySelector('pre').textContent.trim().replace(/\\r\\n/g, '\\n');
const lines = raw.split(/\\r?\\n/);
const empty = raw === "No authenticated users found.\\n" +
  "Use 'tuya-ipc-terminal auth add [region] [email]' to add a user.";
const header = /^Found (\\d+) authenticated user\\(s\\):$/.exec(lines[0]);
const users = [];
let valid = !!header;
if (header) {
  for (const line of lines.slice(1)) {
    if (!line.trim()) continue;
    const user = /^User (\\d+): (.+) \\(([^()]+)\\)$/.exec(line);
    if (user && Number(user[1]) === users.length + 1) {
      users.push({email: user[2], region: user[3], refresh: '', status: null});
    } else if (users.length && /^  Last refresh: .+$/.test(line) && !users[users.length - 1].refresh) {
      users[users.length - 1].refresh = line.slice('  Last refresh: '.length);
    } else if (users.length && /^  Status: .*$/.test(line)) {
      users[users.length - 1].status = line.slice('  Status: '.length);
    } else if (!(users.length && /^  (User ID|Nickname): .*$/.test(line))) {
      valid = false;
      break;
    }
  }
  valid = valid && users.length === Number(header[1]) && users.length > 0;
}
if (empty) {
  accounts.replaceChildren();
  const message = document.createElement('p');
  message.className = 'empty';
  message.textContent = 'No accounts yet. Add an account to get started.';
  accounts.append(message);
} else if (valid) {
  accounts.replaceChildren();
  for (const user of users) {
    const item = document.createElement('div');
    item.className = 'account';
    const heading = document.createElement('div');
    heading.className = 'account-heading';
    const email = document.createElement('strong');
    email.textContent = user.email;
    heading.append(email);
    if (user.status) {
      const badge = document.createElement('span');
      const statuses = {
        '\\u2713 Valid': ['valid', 'Valid'],
        '\\u26a0 Old (>7 days)': ['old', 'Old'],
        '\\u2717 Invalid': ['invalid', 'Invalid']
      };
      const status = Object.hasOwn(statuses, user.status) ? statuses[user.status] : ['', user.status];
      badge.className = 'badge' + (status[0] ? ' ' + status[0] : '');
      badge.textContent = status[1];
      heading.append(badge);
    }
    const details = document.createElement('div');
    details.className = 'account-details';
    details.textContent = user.region + (user.refresh ? ' - Last refresh: ' + user.refresh : '');
    item.append(heading, details);
    accounts.append(item);
  }
}
const form = document.getElementById('login-form');
const password = document.getElementById('password');
form.addEventListener('change', (event) => {
  if (event.target.name !== 'method') return;
  const usePassword = event.target.value === 'password';
  document.getElementById('password-field').hidden = !usePassword;
  password.disabled = !usePassword;
  password.required = usePassword;
  form.action = usePassword ? form.action.replace(/\\/qr\\/start$/, '/password/start')
                            : form.action.replace(/\\/password\\/start$/, '/qr/start');
  document.getElementById('submit').textContent = usePassword ? 'Log in' : 'Start QR login';
});
</script>
"""
        + PAGE_TAIL
    )


def render_progress_page(base, job_id, qr):
    return (
        PAGE_HEAD
        + '<section class="card progress">'
        + ("<h1>QR code login</h1>"
           '<p class="hint">Scan with Tuya Smart, Smart Life, or your OEM app.</p>'
           '<div id="qrcode">Waiting for QR code...</div>' if qr else "<h1>Password login</h1>")
        + '<div aria-live="polite" aria-atomic="true"><div class="status" id="status">'
        + '<span class="spinner" id="spinner" aria-hidden="true"></span>'
        + '<span id="state">Logging in...</span></div>'
        + '<div class="notice" id="notice" hidden><p id="notice-title"></p><p id="message"></p></div></div>'
        + f'<a class="button primary back" href="{base}/">Back to accounts</a></section>'
        + "<script>"
        + f'const jobId = "{job_id}"; const base = "{base}"; const method = "{"qr" if qr else "password"}";'
        + """
let rendered = false;
const labels = {
  starting: 'Logging in...', running: 'Logging in...',
  waiting_for_scan: 'Scan the code with the app', success: 'Account added', error: 'Login failed'
};
function update(state, message) {
  const final = state === 'success' || state === 'error';
  const notice = document.getElementById('notice');
  document.getElementById('message').textContent = message || '';
  document.getElementById('notice-title').textContent = final ? labels[state] : '';
  notice.className = 'notice' + (final ? ' ' + state : '');
  notice.hidden = !final && !message;
  document.getElementById('spinner').hidden = final;
  document.getElementById('state').textContent = final ? '' : (labels[state] || 'Logging in...');
  document.getElementById('status').hidden = final;
}
async function poll() {
  try {
    const res = await fetch(`${base}/${method}/${jobId}/status`);
    if (res.status === 404) {
      update('error', 'This login is no longer known (the app may have restarted). Go back and start again.');
      return;
    }
    if (!res.ok) throw new Error(`Status request failed (${res.status})`);
    const data = await res.json();
    update(data.state, data.message);
    if (method === 'qr' && data.url && !rendered) {
      rendered = true;
      document.getElementById('qrcode').innerHTML =
        `<img src="${base}/qr/${jobId}/image" width="256" height="256" alt="QR code">`;
    }
    if (data.state !== 'success' && data.state !== 'error') {
      setTimeout(poll, 1500);
    }
  } catch (error) {
    document.getElementById('message').textContent = 'Status check failed. Retrying...';
    document.getElementById('notice').hidden = false;
    setTimeout(poll, 1500);
  }
}
poll();
"""
        + "</script>"
        + PAGE_TAIL
    )


def render_qr_page(base, job_id):
    return render_progress_page(base, job_id, True)


def render_password_page(base, job_id):
    return render_progress_page(base, job_id, False)


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

            job_id = start_job(run_qr_job, region, email)
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

            job_id = start_job(run_password_job, region, email, password)
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
