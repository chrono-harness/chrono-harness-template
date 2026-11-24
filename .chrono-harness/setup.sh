#!/bin/sh
set -eu

# mise supplies its native platform key from the registered task.
key="tools.\"http:chrono-host-bootstrap\".platforms.${1:?missing mise platform}.checksum"
scratch=$(mktemp -d /tmp/chrono-template.XXXXXXXX)
trap 'rm -rf -- "$scratch"' EXIT
trap 'exit 1' HUP INT TERM
mise config get --file .config/mise/conf.d/chrono-harness.toml "$key" > "$scratch/pin"

if executable=$(mise which chrono-host-bootstrap 2>/dev/null); then
    :
else
    # Use this tool once, even when the host opted out of installing it.
    MISE_DISABLE_TOOLS= mise install-into http:chrono-host-bootstrap "$scratch/once"
    executable="$scratch/once/chrono-host-bootstrap"
fi

if command -v sha256sum >/dev/null 2>&1; then
    digest_record=$(sha256sum < "$executable")
else
    digest_record=$(shasum -a 256 < "$executable")
fi
# The system utility hashes standard input and prints its digest first.
# Compare the complete mise value with that digest in mise's SHA-256 encoding.
if ! printf 'sha256:%s\n' "${digest_record%% *}" | cmp -s - "$scratch/pin"; then
    echo 'template setup executable checksum differs from the mise pin' >&2
    exit 2
fi
"$executable" prepare-template
