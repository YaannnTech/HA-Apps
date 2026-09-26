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