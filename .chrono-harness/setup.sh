#!/bin/sh
set -eu

# mise supplies its native platform key from the registered task.
key="tools.\"http:chrono-host-bootstrap\".platforms.${1:?missing mise platform}.checksum"
checksum=$(mise config get --file .config/mise/conf.d/chrono-harness.toml "$key")

if executable=$(mise which chrono-host-bootstrap 2>/dev/null); then
    :
else
    scratch=$(mktemp -d /tmp/chrono-template.XXXXXXXX)
    trap 'rm -rf -- "$scratch"' EXIT
    trap 'exit 1' HUP INT TERM
    # Use this tool once, even when the host opted out of installing it.
    MISE_DISABLE_TOOLS= mise install-into http:chrono-host-bootstrap "$scratch"
    executable="$scratch/chrono-host-bootstrap"
fi

if command -v sha256sum >/dev/null 2>&1; then
    actual=$(sha256sum < "$executable")
else
    actual=$(shasum -a 256 < "$executable")
fi
if [ "$checksum" != "sha256:${actual%% *}" ]; then
    echo 'template setup executable checksum differs from the mise pin' >&2
    exit 2
fi
"$executable" prepare-template
