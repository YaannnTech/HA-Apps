# PhoneBlock - Home Assistant App

Runs the Linux build of the [PhoneBlock Dongle](https://phoneblock.net/phoneblock/dongle) SIP spam-call blocker inside Home Assistant. It is intended to run on the same network as a Fritz!Box or other compatible router. The app supports Home Assistant `amd64` and `aarch64` installations. Open the shared PhoneBlock web UI with the app's **Open Web UI** link.

## Setup

Open the app's web UI with **Open Web UI**. Until the app is ready, it shows the **Setup** page with two steps: **Set up telephony** and **Connect PhoneBlock**.

### Set up telephony

Click **Set up telephony** and choose how the app connects to your phone system:

- **Fritz!Box (recommended):** Keep **fritz.box** as the Fritz!Box address (or enter its IP address), leave **User** empty unless you log in to your Fritz!Box with a user name, enter the Fritz!Box **Password** and click **Create extension**. The app adds itself to your Fritz!Box as an IP phone. The password is not stored.
- **Other provider:** Pick your provider (Telekom, Vodafone, 1&1, sipgate or easybell) and enter the SIP credentials from its customer portal.
- **Manual (expert):** Fill in all SIP settings yourself.

### Connect PhoneBlock

Click **Connect PhoneBlock**, then **Link PhoneBlock Account**. The web UI shows a code and guides you through confirming it with your PhoneBlock account. When it shows **PhoneBlock account linked**, the app has its token and starts blocking spam calls.

Instead, you can paste a PhoneBlock API token (starts with `pbt_`) into the **PhoneBlock token** field on the app's **Configuration** tab in Home Assistant, save, and restart the app. If you connected your account in the web UI, leave that field empty.

## Announcement

Spam callers hear a built-in default announcement in your language. In the web UI's **Spam announcement** section you can play it, upload your own recording (WAV, MP3 or OGG) and later click **Reset to default**.

## App options (Configuration tab)

These options are on the app's **Configuration** tab in Home Assistant. Changes need an app restart. Everything else, such as the telephony setup, announcement, dialog and call recording, is set in the app's web UI.

| Option | Meaning |
| --- | --- |
| **PhoneBlock token** | Optional, best left empty. PhoneBlock API token (starts with `pbt_`), only needed if you do not link your account in the web UI. If set, it replaces the token from the web UI link on every start. |
| **Advertised host** | Optional. Hostname or IP address the SIP registrar should use to reach this app, for NAT or routed setups. Leave empty to detect it automatically. |
| **Advertised SIP port** | Optional. UDP port the registrar should use to reach this app, for example a forwarded port. Leave empty to use the local SIP port. |
| **Verbose log** | Optional. Include full SIP messages, keepalives and registration handshakes in the log. Enable only when troubleshooting. |

## Data and backups

- The call list and recordings are stored in the app's data, so they are part of the app's backups.
- Recordings use up to 200 MB.
- Call recording is opt-in in the web UI's dialog settings.
- On first start the app takes Home Assistant's timezone. You can change it later in the web UI's settings.

## Network

The app uses host networking so SIP and RTP can use their configured UDP ports.

## Troubleshooting

**"PhoneBlock: token rejected" notification**

PhoneBlock does not accept the token the app uses. The app gets its token from one of two places:

- The **PhoneBlock token** field on the app's **Configuration** tab in Home Assistant, if it is filled.
- Otherwise, linking your account in the app's web UI.

You see this notification when:

- The token in the **PhoneBlock token** field on the Configuration tab is rejected when the app starts. The app then does not start.
- The token in use, from either place, stops working while the app runs. The app checks once a day.

To fix it:

- **The PhoneBlock token field on the Configuration tab is filled:** Clear it (recommended) or paste a new, valid token, save, and restart the app. If you cleared it, link your account again: In the web UI, click **Renew** next to the PhoneBlock token on the **Status** page.
- **The PhoneBlock token field on the Configuration tab is empty:** In the web UI, click **Renew** next to the PhoneBlock token on the **Status** page and link your account again.

The notification disappears once PhoneBlock accepts the token.

**Other**

- For NAT or routed setups, set **Advertised host** and **Advertised SIP port** on the app's **Configuration** tab in Home Assistant.
- The log omits full SIP messages, keepalives and routine registration handshakes. Enable **Verbose log** on the app's **Configuration** tab and restart the app when you need them.
- The web UI's log panel shows the service's warnings and errors.

## Differences from the ESP32 dongle

- Not available: Wi-Fi provisioning, firmware upload/update, factory reset, mail reporting, live log streaming, crash tests, and chip/heap/task diagnostics. The web UI hides the firmware, factory reset and mail reporting sections.
- New PhoneBlock firmware comes with app updates in Home Assistant.
