#!/bin/sh
set -eu

OPTIONS=/data/options.json

get_option() {
	jq -r --arg key "$1" --arg default "$2" '.[$key] // $default' "$OPTIONS"
}

get_bool_option() {
	value="$(get_option "$1" "$2")"
	case "$value" in
	true | True) echo True ;;
	*) echo False ;;
	esac
}

export CHHOTO_PASSWORD
CHHOTO_PASSWORD="$(get_option password '')"
export CHHOTO_DB_URL=/data/urls.sqlite
export CHHOTO_SQLITE_USE_WAL_MODE
CHHOTO_SQLITE_USE_WAL_MODE="$(get_bool_option enable_wal_mode true)"

redirect_method="$(get_option redirect_method Permanent)"
export CHHOTO_REDIRECT_METHOD
CHHOTO_REDIRECT_METHOD="$(echo "$redirect_method" | tr '[:lower:]' '[:upper:]')"

# CHHOTO_PUBLIC_MODE is only meaningful when set to "Enable"; leave it unset otherwise.
if [ "$(get_bool_option public_mode false)" = "True" ]; then
	export CHHOTO_PUBLIC_MODE=Enable
fi

supervisor_get() {
	wget -qO- --header "Authorization: Bearer ${SUPERVISOR_TOKEN:-}" "http://supervisor$1" 2>/dev/null || true
}

# Host from HA's internal URL, else the host's primary IPv4, joined with this app's published port.
default_site_url() {
	port="$(supervisor_get /addons/self/info | jq -r '.data.network["4567/tcp"] // empty' 2>/dev/null || true)"
	[ -n "$port" ] || return 0

	host="$(supervisor_get /core/api/config | jq -r '.internal_url // empty' 2>/dev/null |
		sed -E 's#^[a-zA-Z]+://##; s#^(\[[^]]*\]|[^/:]+).*#\1#' || true)"
	if [ -z "$host" ]; then
		host="$(supervisor_get /network/info |
			jq -r '[.data.interfaces[] | select(.primary) | .ipv4.address[0] // empty][0] // empty | split("/")[0]' 2>/dev/null || true)"
	fi
	[ -n "$host" ] || return 0

	echo "http://${host}:${port}"
}

site_url="$(jq -r '.site_url // empty' "$OPTIONS")"
if [ -z "$site_url" ]; then
	site_url="$(default_site_url)"
	[ -z "$site_url" ] || echo "Site URL not set, defaulting to ${site_url}"
fi
if [ -n "$site_url" ]; then
	export CHHOTO_SITE_URL="$site_url"
fi

api_key="$(jq -r '.api_key // empty' "$OPTIONS")"
if [ -n "$api_key" ]; then
	export CHHOTO_API_KEY="$api_key"
fi

cd /app
exec /app/chhoto-url
