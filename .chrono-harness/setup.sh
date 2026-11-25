#!/bin/sh
set -eu

# mise supplies its native platform key from the registered task.
key="tools.\"http:chrono-host-bootstrap\".platforms.${1:?missing mise platform}.checksum"
scratch=$(mktemp -d /tmp/chrono-template.XXXXXXXX)
trap 'rm -rf -- "$scratch"' EXIT
trap 'exit 1' HUP INT TERM
disabled=$(mise settings get disable_tools)
case "$disabled" in
    *'"http:chrono-host-bootstrap"'*|*'"chrono-host-bootstrap"'*)
        # Prepare a new checkout even when bootstrap is disabled for everyday use.
        cp .config/mise/conf.d/chrono-harness.toml "$scratch/mise.toml"
        mise config get --file "$scratch/mise.toml" "$key" > "$scratch/pin"
        MISE_TRUSTED_CONFIG_PATHS="$scratch${MISE_TRUSTED_CONFIG_PATHS:+:$MISE_TRUSTED_CONFIG_PATHS}" \
            MISE_DISABLE_TOOLS= mise -C "$scratch" install-into http:chrono-host-bootstrap "$scratch/once"
        executable="$scratch/once/chrono-host-bootstrap"
        ;;
    *)
        mise vars template_bootstrap_checksum > "$scratch/pin"
        executable=$(mise which chrono-host-bootstrap)
        ;;
esac

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
if [ -f .chrono-harness/setup-check-retention.sh ]; then
    sh .chrono-harness/setup-check-retention.sh
fi
