# 0.2.4

- The web UI's log panel now shows the service's warnings and errors (and info lines when enabled), and they are included in the daily log report to PhoneBlock when error reports are enabled.
- Take the timezone from Home Assistant on first start instead of defaulting to Central European Time. A timezone chosen later in the web UI is kept.
- A timezone change in the web UI applies immediately and safely while the service is running.
- Hide the PhoneBlock sign-in buttons ("Neu anfordern" and the button on the token page) in the web UI, since that sign-in cannot complete through Home Assistant. The token is set in the app configuration.
- Report the PhoneBlock firmware version the service was built from (e.g. 1.7.0-beta3-102-g092776f), derived from the upstream release tags, instead of a fixed version.
- Rebuild with the latest upstream changes, including the safer service shutdown from the step 3 review.

# 0.2.3

- Rebuild with the reworked Linux service: it stays up while SIP or the PhoneBlock token is not configured yet, and applies the configured timezone.
- Build the service on the same Alpine release as the pinned Home Assistant base image, so build and runtime libraries match.
- Point the app's homepage link to this repository; the PhoneBlock fork remains linked from the README.

# 0.2.2

- Also omit successful periodic re-registrations from the log; failures are still logged.

# 0.2.1

- Reduce log noise by omitting full SIP messages, keepalives and routine registration handshakes; add an optional verbose log setting to restore them.

# 0.2.0

- Switched to the shared Web UI that is also used by the PhoneBlock Dongle ESP code.
- Require the PhoneBlock token in the app configuration and apply it on every start, replacing the web sign-in that cannot complete through Home Assistant ingress.
- Add optional advertised host and SIP port settings for NAT or routed setups; clearing them restores automatic detection.
- Check the PhoneBlock token at start: a rejected token prevents the app from starting and creates a Home Assistant notification. The daily token check raises the same notification when the token expires, and it is dismissed once the token is accepted again.

# 0.1.28

- Use Home Assistant's dynamically assigned ingress port for the Web UI to avoid clashes with other host-network apps.

# 0.1.27

- Move ingress off the default 8099 port after it conflicted with another app.

# 0.1.26

- Add authenticated access to the Web UI through Home Assistant ingress and the PhoneBlock sidebar entry.
- Make dashboard API links relative so they work under the ingress path.

# 0.1.25

- Restore the selected announcement after restarting the app.

# 0.1.24

- Bundle localized prerecorded announcements, with preview and switching between a preset and an uploaded message.

# 0.1.23

- Support uploading a custom raw G.711 A-law announcement to persistent app storage.
- Allow playback to be disabled without deleting the uploaded announcement.

# 0.1.22

- Refresh SIP registration correctly after service updates.

# 0.1.21

- Rebuild the app with the current Linux PhoneBlock service.

# 0.1.20

- Include timezone-aware logging updates from the Linux service.

# 0.1.19

- Fix truncation of PhoneBlock bearer tokens in the Linux service.

# 0.1.18

- Add token fingerprint diagnostics without logging the bearer token itself.

# 0.1.17

- Fail safely when caller classification returns an error.

# 0.1.16

- Support overriding the advertised address for routed or NAT network setups.

# 0.1.15

- Improve diagnostics for the SIP Contact address.

# 0.1.14

- Add diagnostics for the SIP receive loop.

# 0.1.13

- Rebuild with the Linux SIP transport connection fix.

# 0.1.12

- Fix startup when the persistent dongle configuration has not been created yet.
- Clarify the app description in Home Assistant.

# 0.1.10

- Move dongle setup from Home Assistant options into the Web UI.

# 0.1.9

- Persist Web UI configuration in the app's data directory.

# 0.1.8

- Show call statistics in the dashboard.

# 0.1.7

- Improve dashboard status reporting.

# 0.1.5

- Add the Linux service Web UI and simplify the SIP configuration fields.

# 0.1.4

- Support separate SIP authentication username and realm settings.

# 0.1.3

- Add Fritz!Box SIP phone provisioning options.

# 0.1.2

- Fix app configuration and add the Home Assistant app logo.

# 0.1.0

- Initial release of the PhoneBlock Linux SIP spam-call blocker as a Home Assistant app.