#!/bin/sh
set -eu

case "$(uname -s)-$(uname -m)" in
    Darwin-arm64) platform=macos-arm64 ;;
    Linux-x86_64) platform=linux-x64 ;;
    *) echo 'unsupported template setup platform' >&2; exit 2 ;;
esac
key="tools.\"http:chrono-host-bootstrap\".platforms.$platform"
checksum=$(mise config get "$key.checksum")
case "$checksum" in sha256:*) expected=${checksum#sha256:} ;; *) exit 2 ;; esac

if executable=$(mise which chrono-host-bootstrap 2>/dev/null); then
    :
else
    # An opted-out bootstrap tool is needed only for this first-setup invocation.
    scratch=$(mktemp -d /tmp/chrono-template.XXXXXXXX)
    trap 'rm -rf -- "$scratch"' EXIT
    trap 'exit 1' HUP INT TERM
    executable="$scratch/chrono-host-bootstrap"
    url=$(mise config get "$key.url")
    curl --fail --silent --show-error --location "$url" --output "$executable"
    chmod 700 "$executable"
fi
if command -v sha256sum >/dev/null 2>&1; then
    actual=$(sha256sum < "$executable")
else
    actual=$(shasum -a 256 < "$executable")
fi
if [ "${actual%% *}" != "$expected" ]; then
    echo 'template setup executable checksum differs from the mise pin' >&2
    exit 2
fi
"$executable" prepare-template
