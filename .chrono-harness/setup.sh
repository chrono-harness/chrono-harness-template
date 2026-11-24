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
    set -- sha256sum -c -
else
    set -- shasum -a 256 -c -
fi
# Decode one complete mise pin. The check record names only our open input.
if digest=$(LC_ALL=C expr "$checksum" : 'sha256:\([0-9a-f]\{64\}\)$') &&
    printf '%s  /dev/fd/3\n' "$digest" | "$@" 3< "$executable" >/dev/null
then
    "$executable" prepare-template
else
    echo 'template setup executable checksum differs from the mise pin' >&2
    exit 2
fi
